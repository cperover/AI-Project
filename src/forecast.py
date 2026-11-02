"""
forecast.py - Step 2: demand forecast (THIS IS THE ONLY MACHINE LEARNING IN THE PROJECT).

Data is SIMULATED (see simulate.py).

We forecast next week's orders for each region + plan, using only information
that would be known at that time. Two forecasts are compared:
  1. BASELINE: "same as last week"
  2. ML MODEL: gradient boosting (many small decision trees, each fixing the
     mistakes of the previous ones)

Time-based split: train on the past, test on the most recent 20 weeks.
We never shuffle randomly, because that would let the model "peek" at the future.

Outputs:
  data/forecast_test.csv                  actual + baseline + ML forecast per test row
  report/forecast_actual_vs_pred.png      total weekly orders, actual vs forecasts
  report/forecast_by_series.png           same, one panel per region and plan
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance

SEED = 42
TEST_WEEKS = 20
ROOT = Path(__file__).resolve().parent.parent
FEATURES = ["week_of_year", "last_week", "avg_4_weeks", "region", "plan",
            "promo", "holiday_week"]


def load_features():
    """Read orders and add 'what we knew beforehand' columns."""
    df = pd.read_csv(ROOT / "data" / "orders.csv", parse_dates=["week_start"])
    df = df.sort_values(["region", "plan", "week_start"]).reset_index(drop=True)
    g = df.groupby(["region", "plan"])["orders"]
    df["last_week"] = g.shift(1)                                   # orders one week ago
    df["avg_4_weeks"] = g.transform(lambda s: s.shift(1).rolling(4).mean())  # past 4 weeks only
    df["week_of_year"] = df["week_start"].dt.isocalendar().week.astype(int)
    df["region"] = df["region"].astype("category")
    df["plan"] = df["plan"].astype("category")
    return df.dropna(subset=["last_week", "avg_4_weeks"]).reset_index(drop=True)


def mae(actual, pred):
    return np.mean(np.abs(actual - pred))


def mape(actual, pred):
    return np.mean(np.abs(actual - pred) / actual) * 100


def main():
    df = load_features()

    # ---- Time-based split: last 20 weeks are the test set ----
    weeks = np.sort(df["week_start"].unique())
    cutoff = weeks[-TEST_WEEKS]
    train = df[df["week_start"] < cutoff]
    test = df[df["week_start"] >= cutoff].copy()
    print(f"Train: {train.week_start.min().date()} to {train.week_start.max().date()} "
          f"({len(train)} rows)")
    print(f"Test:  {test.week_start.min().date()} to {test.week_start.max().date()} "
          f"({len(test)} rows)\n")

    # ---- Baseline: same as last week ----
    test["baseline"] = test["last_week"]

    # ---- ML model ----
    model = HistGradientBoostingRegressor(
        categorical_features="from_dtype", max_iter=200, learning_rate=0.05,
        random_state=SEED)
    model.fit(train[FEATURES], train["orders"])
    test["ml"] = model.predict(test[FEATURES]).round()

    # ---- Results table ----
    results = pd.DataFrame({
        "MAE (orders)": [mae(test.orders, test.baseline), mae(test.orders, test.ml)],
        "MAPE (%)": [mape(test.orders, test.baseline), mape(test.orders, test.ml)],
    }, index=["Baseline (same as last week)", "ML (gradient boosting)"]).round(2)
    print("=== Forecast accuracy on the last 20 weeks ===")
    print(results, "\n")
    gain = 100 * (1 - results.iloc[1, 0] / results.iloc[0, 0])
    print(f"ML cuts the average error by {gain:.0f}% compared with the baseline.\n")

    # ---- Where does each forecast struggle? (honesty check) ----
    test["situation"] = np.where(test.promo == 1, "promo week",
                         np.where(test.holiday_week == 1, "holiday week", "normal week"))
    rows = []
    for name, part in test.groupby("situation"):
        rows.append({"situation": name, "rows": len(part),
                     "baseline MAE": mae(part.orders, part.baseline),
                     "ML MAE": mae(part.orders, part.ml)})
    print("=== MAE by type of week ===")
    print(pd.DataFrame(rows).round(1).to_string(index=False), "\n")

    # ---- Which features matter? (permutation: shuffle one column, see how much worse) ----
    imp = permutation_importance(model, test[FEATURES], test["orders"],
                                 n_repeats=10, random_state=SEED,
                                 scoring="neg_mean_absolute_error")
    imp_df = (pd.Series(imp.importances_mean, index=FEATURES)
              .sort_values(ascending=False).round(1))
    print("=== Feature importance (extra MAE when that feature is scrambled) ===")
    print(imp_df.to_string(), "\n")

    # ---- Save predictions for the inventory step ----
    out = test[["week_start", "region", "plan", "orders", "promo", "holiday_week",
                "baseline", "ml"]].rename(columns={"orders": "actual"})
    out.to_csv(ROOT / "data" / "forecast_test.csv", index=False)

    # ---- Charts ----
    (ROOT / "report").mkdir(exist_ok=True)
    tot = test.groupby("week_start")[["orders", "baseline", "ml"]].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tot.index, tot.orders, "k-o", label="Actual")
    ax.plot(tot.index, tot.baseline, "--", color="tab:orange", label="Baseline (last week)")
    ax.plot(tot.index, tot.ml, "-", color="tab:blue", label="ML forecast")
    ax.set_title("Total weekly orders, last 20 weeks: actual vs forecast")
    ax.set_ylabel("Orders (all regions and plans)")
    ax.legend()
    fig.text(0.5, 0.01, "SIMULATED DATA", ha="center", color="red")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(ROOT / "report" / "forecast_actual_vs_pred.png", dpi=120)
    plt.close(fig)

    regions = sorted(test.region.unique())
    plans = sorted(test.plan.unique())
    fig, axes = plt.subplots(3, 3, figsize=(14, 9), sharex=True)
    for i, r in enumerate(regions):
        for j, p in enumerate(plans):
            s = test[(test.region == r) & (test.plan == p)]
            a = axes[i, j]
            a.plot(s.week_start, s.orders, "k-o", ms=3, label="Actual")
            a.plot(s.week_start, s.baseline, "--", color="tab:orange", label="Baseline")
            a.plot(s.week_start, s.ml, color="tab:blue", label="ML")
            a.set_title(f"{r} / {p}", fontsize=9)
            a.tick_params(axis="x", labelrotation=45, labelsize=7)
    axes[0, 0].legend(fontsize=7)
    fig.text(0.5, 0.01, "SIMULATED DATA", ha="center", color="red")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(ROOT / "report" / "forecast_by_series.png", dpi=110)
    plt.close(fig)
    print("Saved data/forecast_test.csv and two charts in report/")


if __name__ == "__main__":
    main()
