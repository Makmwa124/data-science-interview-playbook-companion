# Case question framework

*From The Data Science Interview Playbook by Mathew Kariuki. Print it, or keep it beside you while you practise Chapters 10 and 11.*

## 1. Clarify the goal (2 minutes)

- What is the product or feature for? Who uses it?
- What decision depends on the answer?
- Any constraints: time, budget, data available?

Notes:

## 2. Structure the problem (3 minutes)

Pick one structure and say it out loud.

| Case type | Structure |
|---|---|
| Measure a feature | Goal → adoption → direct effect → primary metric → long term → guardrails |
| Metric dropped | Is it real? → decompose → segment → hypotheses → test → recommend |
| North Star | Value to customers → leads to revenue → teams can move it → weaknesses |
| Two metrics disagree | Combine them → explain the mechanism → check profitability |
| No experiment possible | Comparison group (diff-in-diff) → bunching → interrupted time series |
| Market sizing | Top-down chain of factors → bottom-up sanity check |
| Unit economics | Revenue per unit → variable costs → contribution → levers |
| New market | Attractive? → profitable? → operable? → risk and pilot |

Notes:

## 3. Prioritise (1 minute)

Which part would you look at first, and why?

## 4. Get specific (5 to 10 minutes)

| Metric or analysis | Exact definition | Data source |
|---|---|---|
| | | |
| | | |
| | | |

Guardrails (what must not get worse):

## 5. Close the loop (2 minutes)

- Recommendation:
- What result would change your mind:
- Next step or test:

## Checks before you finish

- [ ] Did I restate the goal before solving?
- [ ] Did I name one primary metric and at least two guardrails?
- [ ] Did I separate correlation from causation?
- [ ] Did I name my most sensitive assumption?
- [ ] Did I end with a recommendation, not "more research is needed"?
