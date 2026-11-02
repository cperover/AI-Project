# Prompts to Give Claude Code (one at a time)

Do them in order. After each one, check the result, ask for an explanation if anything is unclear, and commit to GitHub before moving on.

---

## Step 0: Setup
```
Read CLAUDE.md. Create the project folder structure described there, a requirements.txt
with the libraries listed, and a Python virtual environment. Install the requirements,
and initialize a git repository. Then explain in simple terms what you set up.
```

## Step 1: Simulate the data
```
Create src/simulate.py. Generate about 3 years of weekly orders for 3 regions and 3 plan
types (for example Family, Vegetarian, Low-Carb). Include trend, yearly seasonality,
holiday effects, occasional promotions (with a promo flag column) and random noise. Use a
fixed seed. Save to data/orders.csv. Also generate data/deliveries.csv with about 40
delivery stops per week (latitude/longitude around a depot, with box counts per stop), and
include truck capacity and cost per mile as constants. Make a plot of the weekly orders so
I can check it looks realistic. Then explain how the data was built.
```

## Step 2: Forecast (the ML core)
```
Create src/forecast.py. Build two forecasts: (1) a baseline that predicts "same as last
week", and (2) a gradient boosting model with features such as week of year, last week's
orders, a 4-week rolling average, region, plan type and promo flag. Use a time-based split:
train on the past and test on the last 20 weeks. Report MAE and MAPE for both and show a
comparison table and a chart of actual vs. predicted. Be honest about whether the model
beats the baseline. Explain which features matter and why.
```

## Step 3: Inventory
```
Create src/inventory.py. Convert a forecast into an order quantity (forecast plus a safety
buffer that I can adjust). Simulate the test weeks using both the baseline forecast and the
ML forecast, and count food waste (ordered but not demanded) and stockouts (demand above
what was ordered). Show a comparison table and chart. Explain the safety-buffer tradeoff.
```

## Step 4: Routes (optimization, not ML)
```
Create src/routing.py. Use Google OR-Tools to solve a vehicle routing problem for one
week's deliveries with capacity-limited trucks starting and ending at one depot. Also
implement a naive baseline that visits stops in the order received. Compare total miles and
delivery cost. Return route coordinates so they can be drawn on a map. In comments, make
clear that this is optimization and not machine learning.
```

## Step 5: Dashboard
```
Create app/dashboard.py with Streamlit and Plotly. Show: next-week forecast by region and
plan, the inventory recommendation with a planner "Approve" button, a route map with a
dispatcher "Approve" button, and KPI cards for waste, stockouts, miles, cost and forecast
error vs. baseline. Add a footer saying the data is simulated. Keep it clean and simple.
Tell me how to run it.
```

## Step 6 (optional): Claude summary
```
Create src/summary.py that sends this week's numbers to the Claude API and returns a short
plain-language summary for the planner and dispatcher. Read the API key from an environment
variable, never hardcode it. Add a "Generate summary" button to the dashboard and a note
that a human must verify the summary against the numbers.
```

## Step 7: Polish and review
```
Review the whole project. Check that every result is compared to its baseline, that ML and
optimization are clearly separated, that the simulated-data note is visible, and that both
approval steps work. Fix any bugs, add a README.md with setup and run instructions, and
list the main results in a short table I can use in my report.
```

---

## Habits that protect your grade
- After every step, ask: **"Explain what you just built as if I had to present it to my professor."**
- If something fails, paste the full error back to Claude Code.
- Commit after each step: `git add . && git commit -m "step 2: forecast"`
- Keep a note of your results as you go, so the report is easy to write.
