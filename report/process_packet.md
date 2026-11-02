# Process Evidence Packet (criterion 6, 20 points)

The rubric rewards YOUR judgment: where you redirected, rejected or questioned the AI, and why.
Below, the quotes of your messages are real (from the build chat). The "Why" lines are blank on
purpose: only you know why you did it. Even 1-2 sentences each, in your own words, is what gets points.

Exported transcripts (zip with full conversation), in your Downloads folder:
- Build chat ("Project AI environment setup"): `C:\Users\camil\Downloads\session-export-1793593079263.zip`
- This chat ("AI course homework project"): `C:\Users\camil\Downloads\session-export-1793593079873.zip`

---

## A. Annotated conversation trail (choose 2-4 chats; annotate the turning points)

Chat 1: Build chat. Candidate turning points (I read only the last ~200 of its 624 messages, so add earlier ones you remember, such as the choice of scope or the region/plan breakdown):

1. **You questioned where the "real" numbers came from.**
   Your message: *"how did you create the real numbers to compare with the 2 forecasts?"*
   What happened: the AI answered that the "real" orders are simulated by a recipe (base x trend x season x holiday x promo x noise), and that the model finds patterns the AI planted, so real data would probably give worse accuracy.
   **Why I asked / what I concluded:** ______________________

2. **You checked for fairness of the test (no peeking at the future).**
   Your message: *"how many weeks were used for creating the forecast and how and between which dates we are assuming like the real weeks with which we compare the forecast created?"*
   What happened: AI laid out 4 warm-up weeks, 132 training weeks (2023-01-30 to 2025-08-04), 20 test weeks (2025-08-11 to 2025-12-22).
   **Why I asked / what I concluded:** ______________________

3. **You redirected the plan: dashboard before routes.**
   Your message: *"before step 4. i want to create an app that i can use to see in each week the plans and regions real and forecast and also with a historical graph..."*
   What happened: AI built dashboard v1 (week view and history), not in the original prompt list.
   **Why I changed the order:** ______________________

Chat 2: This chat. Candidate turning points:

4. **Stronger baseline.** The first result said ML cut error by 39%; the 4-week-average baseline showed the gain is about 20% and that the 4-week average is slightly better in normal weeks. 
   **What I thought when I saw this / what I decided:** ______________________

5. **Authorship.** The brief said to write the update yourself; you showed the professor's message saying AI is allowed for the 3-page report, and then edited it (real-data paragraph, "behind the AI" learning, bullets instead of tables, week 7 data goal).
   **What I overruled or changed in the AI's draft, and why:** ______________________

How to annotate: export or open the transcripts, take screenshots of the messages above, paste them into a Word doc, and write your "Why" under each. (Or print to PDF and write on it.)

---

## B. Failure exhibit (pick ONE; say what failed, what you tried, what you concluded)

Real candidates from the project:
- **The dashboard would not open.** You wrote *"i cannmot opern the app"* and then *"what terminal?"*. The AI had assumed you knew the Terminal panel; the real cause was Streamlit waiting for an email prompt. What you tried, and what you learned about how AI explains things (it assumed knowledge; you had to ask).
- **The headline result that shrank.** ML looked 39% better, but only 20% better against a fairer baseline, and not better in normal weeks. What you concluded about weak baselines.
- **Anything else that really happened to you** (a prompt that gave a wrong or too complex answer, a code error, an output you rejected).

**My pick and what I concluded:** ______________________

---

## C. Weekly diary (decision log). Fill in YOUR real dates and reasons.

All commits are dated 2026-11-01, so write the real weeks you worked, and be honest if it was done in a few days. Graders say they will be skeptical of anything unrealistic.

| Week / date | What I did | Decision and why (my reasoning) | Commit |
|---|---|---|---|
| | Set up project, folders, venv | | e391327 |
| | Simulated orders and deliveries | | 2c55df8 |
| | Baseline vs ML forecast | | 30c8c6f |
| | Inventory waste and stockout simulation | | e68981f |
| | Breakdown by region and plan | | e5946ef |
| | Dashboard v1 | | 601e361 |
| | Stronger baseline + seed checks (report/extra_checks.py) | | not committed yet |
| | Mid-quarter update written | | not committed yet |
| 7 (plan) | Try to get real data; routing | | |

Tip: push the repo to GitHub so the commit history serves as version history, and put the link in the packet.

---

## D. Optional extras that help
- Before/after: the first forecast result (39% gain) vs. the checked result (20% over the 4-week average).
- Screenshots of the dashboard.
- Any message or email from the people you are asking for real data.
