"""
simulate.py - Step 1: build the HarvestBox data.

*** ALL DATA IN THIS FILE IS SIMULATED (made up by a random number generator). ***
It is NOT real customer data. Real customer addresses are personal data and would
need permission and privacy protections before use.

Outputs:
  data/orders.csv      weekly orders by region and plan type (156 weeks)
  data/deliveries.csv  about 40 delivery stops per week (lat/lon, boxes per stop)
  report/orders_overview.png  chart to eyeball whether the orders look realistic
"""
from pathlib import Path

import numpy as np
import pandas as pd

# ---------- Constants (easy to change) ----------
SEED = 42                      # fixed seed so results are reproducible
N_WEEKS = 156                  # 3 years
START_DATE = "2023-01-02"      # a Monday
REGIONS = ["North", "Central", "South"]
PLANS = ["Family", "Vegetarian", "Low-Carb"]

# Delivery / truck constants (used later by routing.py)
STOPS_PER_WEEK = 40
NUM_TRUCKS = 3
TRUCK_CAPACITY_BOXES = 60      # max boxes one truck can carry
COST_PER_MILE = 2.50           # dollars per mile driven
DEPOT_LAT, DEPOT_LON = 41.85, -87.65   # one depot (fictional location)

ROOT = Path(__file__).resolve().parent.parent
rng = np.random.default_rng(SEED)

# ---------- 1. Orders ----------
# Typical weekly orders for each region and plan (before trend/season/etc.)
BASE = {
    ("North", "Family"): 300, ("North", "Vegetarian"): 150, ("North", "Low-Carb"): 120,
    ("Central", "Family"): 400, ("Central", "Vegetarian"): 250, ("Central", "Low-Carb"): 180,
    ("South", "Family"): 250, ("South", "Vegetarian"): 100, ("South", "Low-Carb"): 140,
}
TREND_PER_WEEK = 0.0020        # about +11% growth per year
SEASON_SIZE = 0.10             # +/-10% swing over the year (peaks in winter, dips in summer)
PROMO_CHANCE = 0.08            # about 1 in 12 weeks per region has a promotion
PROMO_LIFT = 0.25              # promotions add about 25% orders
NOISE_SD = 0.05                # random week-to-week noise (5%)

weeks = pd.date_range(START_DATE, periods=N_WEEKS, freq="W-MON")


def holiday_effect(week_start):
    """Multiplier for weeks containing a holiday (people order less or differently)."""
    days = pd.date_range(week_start, periods=7)
    effect = 1.0
    for d in days:
        if d.month == 12 and d.day == 25:
            effect *= 0.80     # Christmas week: fewer orders
        if d.month == 1 and d.day == 1:
            effect *= 0.85     # New Year's week
        if d.month == 11 and 22 <= d.day <= 28 and d.weekday() == 3:
            effect *= 1.15     # Thanksgiving week: bump
        if d.month == 7 and d.day == 4:
            effect *= 0.90     # July 4th week
    return effect


# One promo schedule per region (promo applies to all 3 plans in that region)
promo = {r: rng.random(N_WEEKS) < PROMO_CHANCE for r in REGIONS}

rows = []
for i, wk in enumerate(weeks):
    season = 1 + SEASON_SIZE * np.cos(2 * np.pi * (wk.day_of_year - 15) / 365)
    holiday = holiday_effect(wk)
    trend = 1 + TREND_PER_WEEK * i
    for r in REGIONS:
        promo_flag = int(promo[r][i])
        for p in PLANS:
            expected = BASE[(r, p)] * trend * season * holiday * (1 + PROMO_LIFT * promo_flag)
            orders = int(round(expected * rng.normal(1, NOISE_SD)))
            rows.append({"week_start": wk.date(), "region": r, "plan": p,
                         "orders": orders, "promo": promo_flag,
                         "holiday_week": int(holiday != 1.0)})

orders_df = pd.DataFrame(rows)

# ---------- 2. Deliveries ----------
# Each region is a cluster of stops at a different spot around the depot.
REGION_CENTER = {"North": (0.08, 0.00), "Central": (0.00, 0.03), "South": (-0.08, -0.02)}
REGION_SHARE = [0.30, 0.40, 0.30]
SPREAD = 0.03                  # how far stops scatter (degrees, roughly 2 miles)

stop_rows = []
for wk in weeks:
    for s in range(STOPS_PER_WEEK):
        r = rng.choice(REGIONS, p=REGION_SHARE)
        dlat, dlon = REGION_CENTER[r]
        stop_rows.append({
            "week_start": wk.date(),
            "stop_id": s + 1,                       # order the stop was received
            "region": r,
            "lat": round(DEPOT_LAT + dlat + rng.normal(0, SPREAD), 5),
            "lon": round(DEPOT_LON + dlon + rng.normal(0, SPREAD), 5),
            "boxes": int(rng.choice([1, 2, 3, 4], p=[0.2, 0.4, 0.3, 0.1])),
        })
deliveries_df = pd.DataFrame(stop_rows)

# ---------- 3. Save ----------
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "report").mkdir(exist_ok=True)
orders_df.to_csv(ROOT / "data" / "orders.csv", index=False)
deliveries_df.to_csv(ROOT / "data" / "deliveries.csv", index=False)

# Sanity check: does one week of boxes fit in the trucks?
max_week_boxes = deliveries_df.groupby("week_start")["boxes"].sum().max()
print(f"orders.csv: {len(orders_df)} rows | deliveries.csv: {len(deliveries_df)} rows")
print(f"Busiest week has {max_week_boxes} boxes; fleet capacity is "
      f"{NUM_TRUCKS * TRUCK_CAPACITY_BOXES} boxes")

# ---------- 4. Chart ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
total = orders_df.groupby("week_start")["orders"].sum()
axes[0].plot(total.index, total.values, color="black")
promo_weeks = orders_df[orders_df.promo == 1]["week_start"].unique()
for w in promo_weeks:
    axes[0].axvline(w, color="orange", alpha=0.3)
axes[0].set_title("Total weekly orders (orange lines = a promotion in some region)")
axes[0].set_ylabel("Orders")

for p in PLANS:
    s = orders_df[orders_df.plan == p].groupby("week_start")["orders"].sum()
    axes[1].plot(s.index, s.values, label=p)
axes[1].set_title("Weekly orders by plan type")
axes[1].set_ylabel("Orders")
axes[1].legend()
fig.text(0.5, 0.01, "SIMULATED DATA - not real customers", ha="center", color="red")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(ROOT / "report" / "orders_overview.png", dpi=120)
print("Saved report/orders_overview.png")
