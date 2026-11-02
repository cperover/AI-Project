"""Extra checks (scratch): stronger baseline, fair buffer, seed robustness. Data SIMULATED."""
import sys, re, numpy as np, pandas as pd
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingRegressor
ROOT = Path(sys.argv[1]); sys.path.insert(0, str(ROOT / "src"))
FEATURES = ["week_of_year","last_week","avg_4_weeks","region","plan","promo","holiday_week"]
src = (ROOT/"src"/"simulate.py").read_text(encoding="utf-8").split("# ---------- 3. Save")[0]

def make_orders(seed):
    ns = {"__file__": str(ROOT/"src"/"simulate.py")}
    exec(src.replace("SEED = 42", f"SEED = {seed}"), ns)
    return ns["orders_df"]

def feats(df):
    df = df.copy(); df["week_start"] = pd.to_datetime(df["week_start"])
    df = df.sort_values(["region","plan","week_start"]).reset_index(drop=True)
    g = df.groupby(["region","plan"])["orders"]
    df["last_week"] = g.shift(1)
    df["avg_4_weeks"] = g.transform(lambda s: s.shift(1).rolling(4).mean())
    df["week_of_year"] = df.week_start.dt.isocalendar().week.astype(int)
    df["region"] = df.region.astype("category"); df["plan"] = df.plan.astype("category")
    return df.dropna(subset=["last_week","avg_4_weeks"]).reset_index(drop=True)

mae = lambda a,p: np.mean(np.abs(a-p))
mape = lambda a,p: np.mean(np.abs(a-p)/a)*100

def run(seed, ml_seed=42):
    df = feats(make_orders(seed)); weeks = np.sort(df.week_start.unique()); cut = weeks[-20]
    tr, te = df[df.week_start<cut], df[df.week_start>=cut].copy()
    m = HistGradientBoostingRegressor(categorical_features="from_dtype", max_iter=200,
                                      learning_rate=0.05, random_state=ml_seed).fit(tr[FEATURES], tr.orders)
    te["ml"] = m.predict(te[FEATURES]).round()
    te["last"] = te.last_week; te["ma4"] = te.avg_4_weeks.round()
    return te

def inv(te, col, buf, w=9.0, s=6.0):
    o = np.ceil(te[col]*(1+buf)); d = te.orders
    waste = np.maximum(o-d,0).sum(); short = np.maximum(d-o,0).sum()
    return waste, short, 100*(1-short/d.sum()), waste*w+short*s

M = ["last","ma4","ml"]; N = {"last":"Same as last week","ma4":"4-week average","ml":"ML (GB)"}

# 1. Original seed: three-way comparison
te = run(42)
print("=== 1. seed 42, last 20 weeks: accuracy ===")
print(pd.DataFrame({N[c]:[mae(te.orders,te[c]),mape(te.orders,te[c])] for c in M},
      index=["MAE","MAPE %"]).T.round(2))
te["situation"] = np.where(te.promo==1,"promo",np.where(te.holiday_week==1,"holiday","normal"))
print("\nMAE by week type"); print(pd.DataFrame({N[c]:te.groupby("situation").apply(lambda p: mae(p.orders,p[c])) for c in M}).round(1))

print("\n=== 2. Inventory at 5% buffer ===")
print(pd.DataFrame({N[c]:inv(te,c,0.05) for c in M}, index=["waste","stockout","fill %","cost $"]).T.round(1))
print("\n=== 3. Fair comparison: smallest buffer reaching 98% fill ===")
for c in M:
    for b in np.arange(0,0.401,0.01):
        w,s,f,k = inv(te,c,b)
        if f>=98: print(f"{N[c]:20s} buffer {b:.0%}  waste {w:.0f}  stockout {s:.0f}  cost ${k:,.0f}"); break

print("\n=== 4. Cost sensitivity (ML vs best simple, 5% buffer) ===")
for w,s in [(9,6),(5,15),(15,3)]:
    print(f"waste ${w}/kit, stockout ${s}/kit:", {N[c]: round(inv(te,c,0.05,w,s)[3]) for c in M})

print("\n=== 5. Seed robustness: new simulated worlds (MAPE %) ===")
rows=[]
for sd in range(1,11):
    t = run(sd, ml_seed=sd)
    rows.append({"seed":sd, **{N[c]:mape(t.orders,t[c]) for c in M},
                 "ML beats 4wk avg": mape(t.orders,t.ml) < mape(t.orders,t.ma4)})
r = pd.DataFrame(rows).round(2); print(r.to_string(index=False))
print("\nmean MAPE:", r[[N[c] for c in M]].mean().round(2).to_dict())
print("ML beat last-week in", int((r["ML (GB)"]<r["Same as last week"]).sum()), "/10;",
      "beat 4-week avg in", int(r["ML beats 4wk avg"].sum()), "/10")
