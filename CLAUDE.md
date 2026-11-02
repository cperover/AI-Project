# HarvestBox: Meal-Kit Planning Tool (AI Course Final Project)

## What this project is
A decision-support tool for a meal-kit company (like HarvestBox) that:
1. **Forecasts** weekly demand by region and plan type (ML)
2. **Plans inventory** from the forecast (simple calculation, not ML)
3. **Optimizes delivery routes** (optimization with OR-Tools, NOT ML)
4. **Reports everything** on a live Streamlit dashboard

Users: the **operations planner** (decides how much food to prepare) and the **dispatcher** (decides truck routes).
A human approves every decision. The tool recommends; people decide.

## Main goal
Deliver an excellent, honest, well-explained AI course project. Quality of reasoning matters more than complexity.
The course lesson: *not every problem needs ML; the real question is whether benefits outweigh costs and risks.*

## Hard rules
- **Keep the scope small:** 3 regions, 3 plan types, 1 depot, 2-3 trucks, about 40 delivery stops per week.
- **Keep ML and optimization clearly separated** in code, dashboard and comments. Only the forecast is ML.
- **Always compare against a baseline.** Forecast baseline = "same as last week". Routing baseline = stops visited in the order received.
- **Time-based split only** for forecasting (train on the past, test on the most recent ~20 weeks). Never shuffle randomly.
- **Data is simulated.** State this clearly in code comments, dashboard footer and report. Real customer addresses are personal data and would need permission and privacy protections.
- **Report results honestly**, even if the model only slightly beats the baseline.
- **Human in the loop:** the dashboard must have an Approve step for the planner (inventory) and the dispatcher (routes).
- Use a fixed random seed so results are reproducible.
- Write simple, readable code with short comments. The student must be able to explain every part.
- After finishing each step, **explain in plain language what you built and why**.
- Build a rough end-to-end version first, then improve each part.

## Tech stack
Python 3.11+, pandas, numpy, scikit-learn, ortools, plotly, streamlit, anthropic (optional summary).

## Project structure
```
harvestbox/
  CLAUDE.md
  requirements.txt
  data/            # simulated CSVs (orders.csv, deliveries.csv)
  src/
    simulate.py    # data generation
    forecast.py    # baseline + ML model + evaluation
    inventory.py   # order quantity, waste and stockout simulation
    routing.py     # OR-Tools vehicle routing + naive baseline
    summary.py     # optional Claude-written weekly summary
  app/
    dashboard.py   # Streamlit dashboard
  report/          # final write-up and screenshots
```

## Metrics
**Business:** food waste, stockouts, miles driven, delivery cost.
**Model:** forecast error (MAE and MAPE) vs. the "same as last week" baseline.

## Dashboard must show
- Next-week forecast by region and plan
- Inventory recommendation + planner Approve button
- Route map + dispatcher Approve button
- KPI cards: waste, stockouts, miles, cost, forecast error vs. baseline
- Footer noting the data is simulated
- Optional: "Generate summary" button (Claude API; summary must be checked against the numbers)

## Risks to document in the report
- Simulated data may not reflect real behavior
- Forecast errors around holidays or promotions
- Privacy of customer addresses with real data
- LLM summaries can misstate numbers, so a human must verify
- Over-trusting the tool; that is why people approve every decision

## Working style
Do one step at a time. Run the code, check that it works, fix errors yourself, then summarize results and wait for the next instruction.
