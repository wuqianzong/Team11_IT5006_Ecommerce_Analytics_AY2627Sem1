# s08 Selection — implementation review

> **Round 2 · FROZEN (8.5) · 2026-10-23 · runs `20261023T082458Z` (regression) and `20261023T082539Z` (classification), all checks PASS.** The combined team review of s06–s08 is closed, and its decisions are in spec/human\_decisions.yaml s08 (Henry and the experiment lead): one-SE models (regression linear, classification logistic); the agreed rule is kept and s06 is not reopened; sigmoid calibration is kept; threshold 1/6 with a daily alert cap of 25 (23.9 alerts/day out of fold). 8.5 wrote frozen\_recipe.json from development rows only (regression sha256 df4beee3…, classification 8de9d4f1…); two runs are byte-identical. Pipeline A stops here: the final fit, the single test and the bundle (8.6–8.8) run together with Pipeline B. Accepted by the experiment lead for 8.1–8.5 (2026-10-23): the clean rerun on code commit a7329b2 (runs 20261023T084947Z regression, 20261023T085014Z classification) is identical to round 2; tag e5-A-frozen.

**Round 1 · LEAD REVIEW (G-78), gate part 8.1–8.4** · runs `20261021T050311Z` (regression) and `20261021T050340Z` (classification) · 4 + 5 checks, all PASS · coverage: regression 2 of 6, classification 4 of 8; 8.5–8.8 MISSING by design. The run stops at the gate: nothing reads the test cohort. Under G-78 the experiment lead reviews this gate part first; then the team reviews s06, s07 and s08 together here and records its decisions in spec/human\_decisions.yaml s08. Only after that are the freeze, final fit, single test and bundle (8.5–8.8) built, and s08 is accepted as a whole. Evidence cards are in the two sub-tabs. Nothing is committed until the lead has reviewed (G-64).

> **Freeze checklist for Pipeline A (2026-10-23).** A can be frozen (8.5) only when every item below is done. Then A waits for Pipeline B, and the test is read once for both (draft G-79).
>
> 1. **Team review of the gate part:** set the six IMPLEMENTED rows below (8.1–8.4) to Approved, or comment. *Now: all Open.* The eight MISSING rows (8.5–8.8) are not reviewed yet.
> 2. **s06 and s07 confirmed** by the combined review, with no change requested. *Now: comments answered; Henry's feature question went to the bonus round (Pipeline B), with no change to A.*
> 3. **Decision 2 (adoption rule):** keep the agreed one-SE rule for A. *Now: open.* A change would reopen s06.
> 4. **Point 1 (calibration):** keep sigmoid as the agreed rule says, or treat the consistent AP loss as failing it. *Now: open.*
> 5. **Model decisions** in spec/human\_decisions.yaml s08, recorded by the team: regression model (recommended: linear, grid\_edge\_action none) and classification model (recommended: logistic). *Now: null.*
> 6. **Threshold decision** for classification in s08.classification.threshold: a value from the trade-off table, with an optional daily alert cap. *Now: null.*
>
> When items 1–6 are done, 8.5 is built and run: frozen\_recipe.json with its hash, written without reading the test. It is reviewed as s08 round 2, and A is committed and tagged e5-A-frozen.

**Checklist done, 2026-10-23:** items 1–6 closed in the threads on this tab, the six gate rows set to Approved, decisions recorded, and 8.5 built and run (round 2).

## Current (round 1)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | 8.1 | Finalists | IMPLEMENTED | PASS | Approved |
| regression | 8.2 | Choose the model | IMPLEMENTED | PASS | Approved |
| regression | 8.5 | Freeze | IMPLEMENTED | PASS | Open |
| regression | 8.6 | Final fit | MISSING (after the gate) | — | Open |
| regression | 8.7 | Test once | MISSING (after the gate) | — | Open |
| regression | 8.8 | Bundle | MISSING (after the gate) | — | Open |
| classification | 8.1 | Finalists | IMPLEMENTED | PASS | Approved |
| classification | 8.2 | Choose the model | IMPLEMENTED | PASS | Approved |
| classification | 8.3 | Calibration (classification) | IMPLEMENTED | PASS | Approved |
| classification | 8.4 | Threshold (classification) | IMPLEMENTED | — | Approved |
| classification | 8.5 | Freeze | IMPLEMENTED | PASS | Open |
| classification | 8.6 | Final fit | MISSING (after the gate) | — | Open |
| classification | 8.7 | Test once | MISSING (after the gate) | — | Open |
| classification | 8.8 | Bundle | MISSING (after the gate) | — | Open |

### Summary

Finalists: the dummy, plain linear/logistic and single tree from s06, plus each family's carried model from s07 (the plain s06 model in every family), refitted on the same five folds; each reproduces its s06 fold scores exactly (check). Primary metric: MAE (regression), AP (classification), mean ± SE over the folds.

| Task | One-SE recommendation | Best mean | Ladder result | Calibration kept |
| --- | --- | --- | --- | --- |
| regression | linear/logistic (5.4701 ± 0.6733) | single tree (5.4244 ± 0.7147) | linear/logistic | — |
| classification | linear/logistic (0.2435 ± 0.0314) | forest (0.2544 ± 0.0267) | linear/logistic | sigmoid |

### Decisions for the team (combined review of s06–s08, G-39, G-78)

1. **Model, both tasks (8.2; human\_decisions.yaml s08, `model` per task).** Confirm the one-SE recommendation (linear/logistic for regression, linear/logistic for classification) or override it with a rationale; an override is a protocol deviation logged as a CR, and the report shows the one-SE choice beside it (G-44). No finalist sits at a grid edge (candidates.csv, grid\_edge), so grid\_edge\_action is none.
2. **The adoption rule (carried from s06 and s07).** The agreed rule keeps a more complex model only when it beats the simpler one by more than one SE of the fold means; that SE also carries the level differences between folds (drift). Paired over the same folds, for description only: classification forest vs logistic +0.0109 AP (paired SE 0.0063, better in 4 of 5 folds); regression single tree vs linear +0.0458 days (paired SE 0.0685, better in 3 of 5) and forest vs linear +0.0267 days (paired SE 0.0601, better in 3 of 5) (ladder.csv). Keeping the rule gives the recommendations above; switching to a paired SE would be a protocol change (G-33, G-55) made now, before any test score exists, and would reopen s06.
3. **Threshold, classification (8.4; s08.classification.threshold).** Hard stop. From threshold\_table.csv: 0.50 → t = 0.5000: 0.3 alerts/day, precision 0.537, recall 0.005, cost 46,274; 1/6 → t = 0.1667: 23.9 alerts/day, precision 0.252, recall 0.223, cost 42,255; empirical minimum of 5·FN + FP → t = 0.1371: 53.5 alerts/day, precision 0.218, recall 0.432, cost 40,839; no alerts → cost 46,485. Pick a value and, if needed, a daily alert cap the CX team can handle (G-56).

### Points for review

1. **Calibration kept under the agreed rule, with an AP loss (8.3).** Sigmoid lowers mean Brier from 0.12426 to 0.12391, and mean AP falls from 0.2435 to 0.2317, inside one fold SE of raw AP (0.0314), so the rule keeps it (G-16, G-45, G-52); AP is lower in 5 of 5 folds (calibration\_folds.csv). Mechanism (unmeasured): CalibratedClassifierCV with time-ordered inner splits averages three models, each fitted on an earlier, smaller part of the training fold, so it re-ranks orders rather than only rescaling them. The threshold table uses these calibrated probabilities. As with decision 2, the fold SE is wide because of drift. For decision at the gate: keep the agreed rule, or treat a consistent AP loss as failing it (a protocol change).
2. **8.3 and 8.4 use the recommended model.** The blueprint applies them to the chosen model. If the team overrides the recommendation, s08 reruns 8.3–8.4 on the chosen model before the threshold is picked (the model is selected before the threshold, gate criterion).
3. **Learning curves in the pack come from s06 (latest fold).** The recommendation is a plain s06 model, so its s06 curves apply unchanged; they are in selection\_review\_pack.md.
4. **Deterministic.** Two s08 runs give byte-identical outputs (checked); the foundation change (e5lib/selection.py) made s01–s07 stale, and their reruns are byte-identical apart from one s01 check detail that now counts the two s08 nodes.

## Round history

### Round 1 — 2026-10-21

- First build of the s08 gate part (8.1–8.4) for both tasks: new foundation module e5lib/selection.py with tests/test\_selection.py (58 tests pass); CR-053.
- Comments and resolutions: none yet.

### Round 2 — 2026-10-23

- The combined team review of s06–s08 closed. The decisions are recorded in human\_decisions.yaml s08 and the 8.1–8.4 rows are Approved.
- 8.5 built in e5lib/selection.py (tests/test\_selection.py: 59 tests pass); CR-055. The foundation change made s01–s07 stale; they were rerun with byte-identical outputs.
- frozen\_recipe.json per task, with its sha256 and no test read. 8.6–8.8 wait for the joint test run with Pipeline B.
