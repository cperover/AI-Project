"""
inventory.py - Step 3: turn a forecast into an order quantity, then test it.

NOT machine learning: this is simple arithmetic on top of the forecast from forecast.py.
Data is SIMULATED (see simulate.py). Cost numbers below are made-up assumptions.

Idea:   order quantity = forecast x (1 + safety buffer)
        waste    = ordered but not demanded   (food thrown away)
        stockout = demanded but not ordered   (customers we could not serve)
We "replay" the 20 test weeks with the baseline forecast and the ML forecast
and count both. One order = one meal kit = one unit of food to prepare.

Outputs:
  data/inventory_results.csv
  report/inventory_comparison.png    waste and stockouts at the chosen buffer
  report/inventory_tradeoff.png      what happens as the buffer grows
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# ---------- Settings you can adjust ----------
SAFETY_BUFFER = 0.05        # extra 5% on top of the forecast (planner can change this)
WASTE_COST_PER_KIT = 9.0    # $ lost for each kit prepared but not sold (assumption)
STOCKOUT_COST_PER_KIT = 6.0 # $ profit lost for each kit we could not supply (assumption)
SERVICE_TARGET = 0.98       # "fill rate" goal used for the fair comparison below


def order_quantity(forecast, buffer=SAFETY_BUFFER):
    """Forecast plus a safety buffer, rounded up to whole kits."""
    return np.ceil(np.asarray(forecast) * (1 + buffer)).astype(int)


def simulate(df, forecast_col, buffer):
    """Replay the test weeks: compare what we ordered with what customers demanded."""
    ordered = order_quantity(df[forecast_col], buffer)
    demand = df["actual"].to_numpy()
    waste = np.maximum(ordered - demand, 0)
    short = np.maximum(demand - ordered, 0)
    return {
        "ordered": int(ordered.sum()),
        "demand": int(demand.sum()),
        "waste_kits": int(waste.sum()),
        "waste_pct_of_ordered": 100 * waste.sum() / ordered.sum(),
        "stockout_kits": int(short.sum()),
        "stockout_cases": int((short > 0).sum()),     # region/plan/weeks with a shortage
        "fill_rate_pct": 100 * (1 - short.sum() / demand.sum()),
        "cost_$": waste.sum() * WASTE_COST_PER_KIT + short.sum() * STOCKOUT_COST_PER_KIT,
    }


def main():
    df = pd.read_csv(ROOT / "data" / "forecast_test.csv", parse_dates=["week_start"])
    methods = {"Baseline (same as last week)": "baseline", "ML (gradient boosting)": "ml"}

    # ---- 1. Comparison at the chosen buffer ----
    table = pd.DataFrame({name: simulate(df, col, SAFETY_BUFFER)
                          for name, col in methods.items()}).T
    print(f"=== Last 20 weeks, safety buffer = {SAFETY_BUFFER:.0%} ===")
    print(table.round(1).to_string(), "\n")

    # ---- 2. Sweep the buffer to show the trade-off ----
    buffers = np.arange(0, 0.301, 0.01)
    sweep = {name: pd.DataFrame([{"buffer": b, **simulate(df, col, b)} for b in buffers])
             for name, col in methods.items()}

    # ---- 3. Fair comparison: smallest buffer that reaches the service target ----
    print(f"=== Fair comparison: smallest buffer reaching {SERVICE_TARGET:.0%} fill rate ===")
    fair = {}
    for name, s in sweep.items():
        ok = s[s.fill_rate_pct >= 100 * SERVICE_TARGET]
        row = ok.iloc[0] if len(ok) else s.iloc[-1]
        fair[name] = row
        print(f"{name}: buffer {row.buffer:.0%} -> waste {int(row.waste_kits)} kits, "
              f"stockouts {int(row.stockout_kits)} kits, cost ${row['cost_$']:,.0f}")
    print()

    table.to_csv(ROOT / "data" / "inventory_results.csv")

    # ---- 4. Breakdown by region and plan (same calculation, on each subset) ----
    rows = []
    for region in ["All"] + sorted(df.region.unique()):
        for plan in ["All"] + sorted(df.plan.unique()):
            part = df
            if region != "All":
                part = part[part.region == region]
            if plan != "All":
                part = part[part.plan == plan]
            for name, col in methods.items():
                rows.append({"region": region, "plan": plan, "forecast": name,
                             **simulate(part, col, SAFETY_BUFFER)})
    breakdown = pd.DataFrame(rows)
    breakdown.to_csv(ROOT / "data" / "inventory_by_group.csv", index=False)

    def show(title, region, plan, keys):
        part = breakdown[(breakdown.region.isin(region)) & (breakdown.plan.isin(plan))]
        view = part.pivot(index=keys, columns="forecast",
                          values=["waste_kits", "stockout_kits", "cost_$"])
        print(f"=== {title} (buffer {SAFETY_BUFFER:.0%}) ===")
        print(view.round(0).astype(int).to_string(), "\n")

    regions = sorted(df.region.unique())
    plans = sorted(df.plan.unique())
    show("By region", regions, ["All"], "region")
    show("By plan", ["All"], plans, "plan")
    show("By region and plan", regions, plans, ["region", "plan"])

    # ---- Charts ----
    (ROOT / "report").mkdir(exist_ok=True)
    colors = ["tab:orange", "tab:blue"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, col, title in [(axes[0], "waste_kits", "Food waste (kits)"),
                           (axes[1], "stockout_kits", "Stockouts (kits not supplied)")]:
        ax.bar(["Baseline", "ML"], table[col], color=colors)
        ax.set_title(title)
        for i, v in enumerate(table[col]):
            ax.text(i, v, f"{int(v):,}", ha="center", va="bottom")
    fig.suptitle(f"Inventory test on the last 20 weeks (buffer {SAFETY_BUFFER:.0%})")
    fig.text(0.5, 0.01, "SIMULATED DATA", ha="center", color="red")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(ROOT / "report" / "inventory_comparison.png", dpi=120)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for (name, s), c in zip(sweep.items(), colors):
        axes[0].plot(s.buffer * 100, s.waste_kits, color=c, label=name)
        axes[1].plot(s.buffer * 100, s.stockout_kits, color=c, label=name)
    axes[0].set_title("Waste goes UP as the buffer grows")
    axes[1].set_title("Stockouts go DOWN as the buffer grows")
    for ax, yl in zip(axes, ["Wasted kits", "Kits not supplied"]):
        ax.set_xlabel("Safety buffer (%)")
        ax.set_ylabel(yl)
        ax.axvline(SAFETY_BUFFER * 100, color="gray", ls=":")
    axes[0].legend()
    fig.text(0.5, 0.01, "SIMULATED DATA", ha="center", color="red")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(ROOT / "report" / "inventory_tradeoff.png", dpi=120)
    plt.close(fig)
    print("Saved data/inventory_results.csv and two charts in report/")


if __name__ == "__main__":
    main()
