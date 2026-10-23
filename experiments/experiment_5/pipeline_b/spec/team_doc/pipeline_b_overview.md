# Pipeline A + B — one baseline, one improvement, one test

**Approved by the team on 2026-10-22: Pipeline B = Pipeline A + one change request.** Status: plan; nothing of B is built yet. Pipeline A is the complete, accepted pipeline (tab "Pipeline v2"). Pipeline B changes only what its change request lists and reuses everything else from A. Both are frozen before the test cohort is read, the test is read once for both, and B is the delivered model.

&#91;embedded content: Pipeline A + B · 9 steps, one test read\]

Read top to bottom: the team approves B's definition first; A finishes its gate and is frozen; B is built from A's outputs and code; both meet one test read; the conclusion compares them; the release, dashboard and business impact are B's.

## Steps

| # | Step | Pipeline | Who decides | Output and where |
| --- | --- | --- | --- | --- |
| 1 | Decision G-79 + change request | B (definition) | team, in this doc | decision\_log.md G-79; CHANGELOG.md CR |
| 2 | Combined review of s06–s08, gate 8.1–8.4 | A | team | spec/human\_decisions.yaml s08 |
| 3 | Freeze A (8.5), no test read | A | experiment lead | stages/s08\_selection/\*/frozen\_recipe.json; tag e5-A-frozen |
| 4 | B2 population and new columns; B4–B5 recipe and folds | B | experiment lead (review) | pipeline\_b/stages/b02, b04, b05 |
| 5 | B6–B7 training and tuning | B | experiment lead (review) | pipeline\_b/stages/b06, b07 |
| 6 | B8.1–B8.5 gate and freeze | B | team | pipeline\_b/spec/human\_decisions.yaml; tag e5-B-frozen |
| 7 | One test read (8.6–8.7) | A and B | nobody: run once | test outputs in both trees, one run |
| 8 | 9 Conclusion | A, B, comparison | team | s09 cards + one generated comparison table |
| 9 | 10 Release | B | team and lead | bundle, dashboard, report and slides from B |

## Pipeline B's change list (everything else is inherited from A)

| Change | What |
| --- | --- |
| Population | Customer and seller in SP, MG, RJ, PR, RS, BA, SC; distance present; lead-time cap mean + 8 × SD (AMENDED by B-G-03: computed on B's own rows, 83.66 days in B2 round 2; the earlier 93.63 from A's s02 values is superseded); six-week warm-up |
| Prediction time | Classification at carrier handover; regression stays at checkout |
| Features | Candidates, all promise-free and defined in CR-054 §4 (B-C6 to B-C9): route one-hot, prior seller dispatch days, seller handover lateness against the shipping limit, route lead and transit time (both tasks), this order's handover facts (classification). The 99% importance rule (B-C11) keeps or drops each; all are listed in feature\_dictionary\_B.csv |
| Extra rule | Missed-dispatch alert for orders never handed over (a rule, not a model) |
| Inherited unchanged | Fold boundaries (filtered), model families, grids, one-SE rule, metrics, calibration and threshold procedure, s08 gates |

## Keeping the two apart

- **Names:** "Pipeline A – baseline" and "Pipeline B – improved", never just "the model".
- **Folders:** A in stages/ (frozen at e5-A-frozen, never edited again); B in pipeline\_b/ with its own runner. B imports A's code read-only, so A never goes stale.
- **Evidence IDs:** A keeps 6.2, 8.4 and so on; B uses B6.2, B8.4. Every manifest names its pipeline.
- **Doc:** B's reviews get their own tab group; A's review tabs stay as they are.
- **Report and slides:** one comparison table, generated from both pipelines' outputs, is the only place A and B appear side by side. The dashboard and business impact cite B only.
- **Probes are not results:** probe 1 motivated B; probe 2 is withdrawn. Neither is cited.
