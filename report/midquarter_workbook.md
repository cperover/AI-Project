# Mid-Quarter Update: Workbook (facts from the repo + what only YOU can fill in)

The assignment says: *"Please write this yourself"* and wants evidence of YOUR thinking.
So this file gives you verified facts and the questions each criterion asks. The prose, the reasons
and the judgment calls must be yours. Reply to the questions in plain words (even messy) and I will
help you tighten them, check numbers, and format the PDF.

---

## Facts verified from the project (safe to cite)

| Item | Value |
|---|---|
| Scope | 3 regions x 3 plans, weekly, ~3 years simulated (orders.csv 1,404 rows); ~40 stops/week (deliveries.csv) |
| Forecast split | Time-based. Test = last 20 weeks (2025-08-11 to 2025-12-22) |
| MAE | Baseline 27.45 vs ML 16.63 (-39%) |
| MAPE | Baseline 10.05% vs ML 5.90% |
| By week type (MAE) | Holiday: 56.6 -> 30.7. Normal: 22.3 -> 15.1. Promo: 56.1 -> 14.9 |
| Top feature | avg_4_weeks (103.8), then week_of_year (4.1). The rest are small |
| Inventory (test weeks) | Waste 4,290 -> 2,833 kits (8.3% -> 5.6% of ordered). Stockout kits 1,245 -> 691. Fill rate 97.4% -> 98.6% |
| Built so far | simulate.py, forecast.py, inventory.py, dashboard v1 (demand explorer) |
| NOT built yet | routing.py (OR-Tools), planner/dispatcher Approve buttons, KPI cards, optional Claude summary |

## Honest caveats to put in the update (criterion 4 rewards this)
- All data is **simulated by us**, so the ML win partly reflects how we built the simulator (trend + seasonality + promo + holidays are exactly what a model with a rolling average can learn). It does not prove it would work on real HarvestBox data.
- avg_4_weeks dominates the model. The "ML" is mostly a smoothed average, and that is why it beats a one-week-ago baseline that copies noise. A simple 4-week moving-average baseline would be a fairer comparison. **Running that is a cheap, strong "checking the work" move.**
- Inventory results use one safety-buffer setting. Show the tradeoff chart (report/inventory_tradeoff.png).
- All commits are dated 2026-11-01. If your diary claims week-by-week progress, make it match what really happened (see the diary section).

---

## Part 1: The 3-page written update (PDF, you write it)

Suggested layout, ~1/2 page per criterion. Don't pad.

### 1. Problem definition (10 pts)
Questions for you:
- Who has the problem (planner? dispatcher?) and what does it cost them today (waste $, stockouts, miles)?
- What real contact with reality do you have: a conversation with someone in food or logistics, a real meal-kit company's published numbers, an observed workflow? (Right now it is all simulated, so this is the weakest point. Even one 15-minute conversation or a cited industry figure helps a lot.)
- What is "success" in numbers? (e.g. forecast MAPE below baseline, waste down X%)
- Did the problem change after talking to the professor? What prompted it?

### 2. Approach and rationale (10 pts)
Questions for you:
- Why does ML fit the forecast but not the routing? (Course lesson: not every problem needs ML.)
- Which non-AI options did you consider (same-as-last-week, moving average, spreadsheet, fixed buffer)?
- Tradeoffs you can name: accuracy vs. explainability, simulated vs. real data, cost of a wrong forecast (waste vs. stockout).
- Why Claude Code for building? What did you not delegate?

### 3. Learning about AI through the work (15 pts)
Questions for you (answer from real memory of the chats):
- What did you ask Claude that came out wrong or too complex, and how did you change the prompt/context?
- Did a change to instructions (CLAUDE.md, step-by-step prompts, "keep scope small") visibly change output? Why?
- Problem-specific failure modes so far. Candidates from the repo, confirm which really happened: simulator too easy / unrealistic; model leaning on one feature; holiday and promo weeks having higher error; AI explanations sounding confident without checks.

### 4. Checking the work (15 pts)
What exists: baseline comparison, time-based test, error by week type, feature importance, inventory simulation.
What to add (plan): 4-week-average baseline; sensitivity to the safety buffer; test on a differently seeded simulation; show one planner/dispatcher the dashboard and write down their feedback; independently recompute a few MAE numbers by hand.
Questions for you: what did you check yourself versus just accept? Did anything not match your expectation?

### 5. Work completed and plan for weeks 7-10 (15 pts)
Done: see the table above (show 1-2 charts from report/).
Plan draft (edit to your real availability):
- Wk 7: routing.py (OR-Tools vs. in-order baseline)
- Wk 8: dashboard completion (forecast, inventory + Approve, route map + Approve, KPI cards, simulated-data footer)
- Wk 9: evaluation upgrades (stronger baseline, sensitivity), optional Claude summary with number-checking
- Wk 10: report, risks, video re-check, polish
Risks and fallbacks (you choose): routing takes too long -> use a smaller instance / naive plus 2-opt; summary misstates numbers -> drop it or show numbers beside it; dashboard bugs -> freeze features by wk 9.

---

## Part 2: Process evidence packet

### A. Annotated conversation trail (2-4 chats)
Only one session exists in the app: "Project AI environment setup" (the build chat). You need to choose 2-4 conversations and export them (PDF or screenshots), then annotate where YOU redirected, rejected or overruled the AI. Pick moments such as:
- scope decisions (3 regions / 3 plans),
- changing the simulation or model after looking at a chart,
- Step 3b (breakdown by region and plan) and dashboard v1, which look like your own additions beyond the prompt list,
- this chat (choosing what to put in the update).
I can export the transcript for you, but the annotations have to be in your words.

### B. Failure exhibit
Pick ONE real failure: what didn't work, what you tried, what you concluded. Tell me what it was and I'll help write it up precisely. Don't invent one.

### C. Weekly decision diary
Draft skeleton from git history. All commits are on 2026-11-01, so fill in the real dates you worked and why you decided each thing:

| Date (yours) | What I did | Decision and why (YOUR reasoning) | Commit |
|---|---|---|---|
| | Set up project, structure, venv | | e391327 Step 0 |
| | Simulated orders and deliveries | | 2c55df8 Step 1 |
| | Baseline vs gradient boosting forecast | | 30c8c6f Step 2 |
| | Inventory waste and stockout simulation | | e68981f Step 3 |
| | Breakdown by region and plan | | e5946ef Step 3b |
| | Dashboard v1 demand explorer | | 601e361 |

Tip: GitHub gives you version history for free. Push the repo and add the link.

### D. Optional extras
Before/after (e.g. baseline vs ML chart), raw inputs (screenshots of dashboard), stakeholder feedback.

---

## Video: later, as you said
Remember: 5 min max, speak from notes, show a real chat turning point, one decision, one failure, and answer the Slack question.

---

## Extra checks I ran (reproduce with `python report/extra_checks.py .`, run from the project root; data is SIMULATED)

**Stronger baseline: 4-week average (last 20 weeks, seed 42)**

| Method | MAE | MAPE % | Waste kits (5% buffer) | Stockout kits | Cost $ |
|---|---|---|---|---|---|
| Same as last week | 27.45 | 10.05 | 4,290 | 1,245 | 46,080 |
| 4-week average | 20.88 | 7.60 | 3,292 | 1,082 | 36,120 |
| ML (gradient boosting) | 16.63 | 5.90 | 2,833 | 691 | 29,643 |

- Most of the "ML gain" over last-week comes from simply smoothing (MAE 27.5 -> 20.9). ML adds a further 20% on top of the 4-week average (20.9 -> 16.6).
- **By week type, the 4-week average is actually slightly better than ML in normal weeks** (MAE 14.6 vs 15.1). ML wins in promo weeks (14.9 vs 52.1) and holiday weeks (30.7 vs 58.7), because it sees the promo and holiday flags. Honest takeaway: ML earns its keep on special weeks, and that is partly because our simulator makes them predictable by flags.
- Fair comparison at 98% fill rate: last-week needs an 8% buffer (waste 5,384, cost $53,652), 4-week average 6% (waste 3,651, $38,541), ML 4% (waste 2,488, $27,372).
- Cost-assumption sensitivity: ML is cheapest under all three waste/stockout cost settings tried ($9/$6, $5/$15, $15/$3).

**Different simulated worlds (seeds 1-10, MAPE %)**: last-week 9.65 avg, 4-week average 7.80, ML 6.65. ML beat last-week 10/10 and the 4-week average 10/10, but narrowly in seed 2 (6.68 vs 6.74).

**Limits:** all of this is on data we simulated, so it only shows the model learns the patterns we put in. The test is 20 weeks, and one seed is the headline result. Cost per kit ($9 waste, $6 stockout) are assumptions, not real figures.
