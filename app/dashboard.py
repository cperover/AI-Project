"""
dashboard.py - HarvestBox dashboard (first version: demand explorer).

Data is SIMULATED (see src/simulate.py). No real customers.
Only the forecast is machine learning. Forecasts exist only for the last 20 weeks
(the test weeks), because the model learned from the earlier weeks.

Run with:  .venv\\Scripts\\python.exe -m streamlit run app/dashboard.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="HarvestBox", layout="wide")


@st.cache_data
def load_data():
    """Actual orders for all weeks, with forecasts attached for the test weeks."""
    orders = pd.read_csv(ROOT / "data" / "orders.csv", parse_dates=["week_start"])
    fc = pd.read_csv(ROOT / "data" / "forecast_test.csv", parse_dates=["week_start"])
    fc = fc[["week_start", "region", "plan", "baseline", "ml"]]
    df = orders.merge(fc, on=["week_start", "region", "plan"], how="left")
    return df.rename(columns={"orders": "actual"})


df = load_data()
all_weeks = sorted(df.week_start.unique())
test_start = df.dropna(subset=["ml"]).week_start.min()

st.title("HarvestBox demand explorer")
st.caption("Actual orders vs forecasts by week, region and plan. SIMULATED data.")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Regions", sorted(df.region.unique()),
                                 default=sorted(df.region.unique()))
plans = st.sidebar.multiselect("Plans", sorted(df.plan.unique()),
                               default=sorted(df.plan.unique()))
st.sidebar.markdown(f"Forecasts are available from **{test_start.date()}** "
                    f"(the last 20 weeks).")
view = df[df.region.isin(regions) & df.plan.isin(plans)]

if view.empty:
    st.warning("Pick at least one region and one plan.")
    st.stop()

tab_week, tab_hist = st.tabs(["Single week", "History between dates"])

# ---------- Tab 1: one week ----------
with tab_week:
    week = st.selectbox("Week starting", all_weeks[::-1],
                        format_func=lambda d: pd.Timestamp(d).strftime("%Y-%m-%d"))
    wk = view[view.week_start == week].copy()
    has_fc = wk.ml.notna().any()

    if has_fc:
        wk["ML error"] = wk.ml - wk.actual
        wk["Baseline error"] = wk.baseline - wk.actual
        c1, c2, c3 = st.columns(3)
        c1.metric("Actual orders", f"{int(wk.actual.sum()):,}")
        c2.metric("ML forecast", f"{int(wk.ml.sum()):,}",
                  f"{int(wk.ml.sum() - wk.actual.sum()):+,} vs actual", delta_color="off")
        c3.metric("Baseline forecast", f"{int(wk.baseline.sum()):,}",
                  f"{int(wk.baseline.sum() - wk.actual.sum()):+,} vs actual", delta_color="off")
        long = wk.melt(id_vars=["region", "plan"], value_vars=["actual", "baseline", "ml"],
                       var_name="type", value_name="orders")
        long["type"] = long["type"].map({"actual": "Actual", "baseline": "Baseline",
                                         "ml": "ML forecast"})
    else:
        st.info("No forecast for this week: it is in the period the model learned from, "
                "so only actual orders are shown. Pick a week from the last 20 to compare.")
        st.metric("Actual orders", f"{int(wk.actual.sum()):,}")
        long = wk.assign(type="Actual").rename(columns={"actual": "orders"})

    long["group"] = long.region + " / " + long.plan
    fig = px.bar(long, x="group", y="orders", color="type", barmode="group",
                 color_discrete_map={"Actual": "#a0a0a0", "Baseline": "#f28e2b",
                                     "ML forecast": "#4e79a7"})
    fig.update_layout(xaxis_title="Region / plan", yaxis_title="Orders")
    st.plotly_chart(fig, width="stretch")

    cols = ["region", "plan", "actual"] + (
        ["baseline", "ml", "Baseline error", "ML error"] if has_fc else [])
    if wk.promo.any():
        st.caption("Promotion running this week in: "
                   + ", ".join(sorted(wk[wk.promo == 1].region.unique())))
    if wk.holiday_week.any():
        st.caption("This is a holiday week.")
    st.dataframe(wk[cols].reset_index(drop=True), width="stretch", hide_index=True)

# ---------- Tab 2: history ----------
with tab_hist:
    first, last = pd.Timestamp(all_weeks[0]).date(), pd.Timestamp(all_weeks[-1]).date()
    picked = st.date_input("Choose dates (start and end)", value=(first, last),
                           min_value=first, max_value=last)
    if len(picked) != 2:
        st.info("Click a start date and an end date.")
        st.stop()
    start, end = pd.Timestamp(picked[0]), pd.Timestamp(picked[1])

    group_by = st.radio("Show", ["Total", "By region", "By plan", "By region and plan"],
                        horizontal=True)
    key = {"Total": [], "By region": ["region"], "By plan": ["plan"],
           "By region and plan": ["region", "plan"]}[group_by]

    sel = view[(view.week_start >= start) & (view.week_start <= end)]
    if sel.empty:
        st.warning("No weeks in that range.")
        st.stop()

    # Add up the numbers (keep blanks blank where there is no forecast)
    agg = (sel.groupby(key + ["week_start"])[["actual", "baseline", "ml"]]
              .sum(min_count=1).reset_index())
    agg["group"] = agg[key].astype(str).agg(" / ".join, axis=1) if key else "All"
    long = agg.melt(id_vars=["week_start", "group"], value_vars=["actual", "baseline", "ml"],
                    var_name="type", value_name="orders").dropna(subset=["orders"])
    long["type"] = long["type"].map({"actual": "Actual", "baseline": "Baseline",
                                     "ml": "ML forecast"})

    # With one group, color by type so the three lines are easy to tell apart
    fig = px.line(long, x="week_start", y="orders",
                  color="type" if not key else "group", line_dash="type",
                  color_discrete_map={"Actual": "#a0a0a0", "Baseline": "#f28e2b",
                                      "ML forecast": "#4e79a7"} if not key else None,
                  line_dash_map={"Actual": "solid", "Baseline": "dot", "ML forecast": "dash"},
                  labels={"week_start": "Week", "orders": "Orders", "group": "", "type": ""})
    if sel.ml.notna().any():
        fig.add_vrect(x0=test_start, x1=sel.week_start.max(), fillcolor="lightblue",
                      opacity=0.2, line_width=0,
                      annotation_text="forecast period", annotation_position="top left")
    promo_weeks = sel[sel.promo == 1].week_start.unique()
    st.plotly_chart(fig, width="stretch")
    st.caption(f"{len(promo_weeks)} week(s) in this range had a promotion in at least one "
               "selected region. Solid = actual, dotted = baseline, dashed = ML forecast.")

    # Accuracy on the weeks in range that have forecasts
    tested = sel.dropna(subset=["ml"])
    if tested.empty:
        st.info("No forecast weeks in this range, so no accuracy numbers.")
    else:
        mae_b = (tested.baseline - tested.actual).abs().mean()
        mae_m = (tested.ml - tested.actual).abs().mean()
        mape_b = ((tested.baseline - tested.actual).abs() / tested.actual).mean() * 100
        mape_m = ((tested.ml - tested.actual).abs() / tested.actual).mean() * 100
        a, b, c, d = st.columns(4)
        a.metric("Baseline error (MAE)", f"{mae_b:.1f} orders")
        b.metric("ML error (MAE)", f"{mae_m:.1f} orders")
        c.metric("Baseline error (MAPE)", f"{mape_b:.1f}%")
        d.metric("ML error (MAPE)", f"{mape_m:.1f}%")
        st.caption(f"Accuracy is measured on {tested.week_start.nunique()} forecast week(s) "
                   "in the selected range and filters.")

st.divider()
st.caption("All data on this dashboard is SIMULATED, not real customer data. "
           "Only the forecast is machine learning. A person makes every decision.")
