# B8 — selection, gate and freeze (blueprint)

| Field | Value |
| --- | --- |
| Stage | B8, Pipeline B (G-79; CR-054 B-C10, B-C13; B-G-01) |
| Nodes | regression, classification |
| Status | PROPOSED for the lead's approval (2026-10-24) |
| Inherits from A | `e5lib/selection.py` `run()` unchanged (finalists, one-SE recommendation, calibration, threshold table, gate, freeze); A's s08 decision rules (G-39, G-44, G-78) |

## 1. Goal and gate
Goal: choose B's model, calibration and threshold at a human gate, compare B with A on the same
rows (G-79 adoption rule), and freeze B without reading the test.
Gate: B8 stops at the gate until `human_decisions_B.yaml` b08 is filled for its task (as G-39);
`frozen_recipe_B.json` is written before any test row is read. The team reviews B6–B8 together
at this gate (as G-78).

## 2. Inputs (current runs in `../../EVIDENCE.md`)
B4 recipes, B6 metrics and learning curves, B7 counts and grid results, B5 folds, B2 rows,
`human_decisions_B.yaml` b08; for the adoption comparison, A's frozen recipes
(`../../stages/s08_selection/<task>/outputs/frozen_recipe.json` at e5-A-frozen) and A's s05 folds.

## 3. Method
1. **B8.1–B8.5 = A's 8.1–8.5 through the adapter** (as B6–B7). `selection.run()` reads two more
   inputs than s06/s07; the adapter also supplies them for the call:
   - `paths.spec_path("human_decisions.yaml")` → a view of `human_decisions_B.yaml` whose `s08`
     section is B's `b08` section (written under `pipeline_b/.cache/`, never in A's spec);
   - `paths.outputs_dir(s08_selection, task)` → `pipeline_b/stages/b08/<task>/outputs/`, so the
     gate check looks for B's frozen recipe, never A's.
   With b08 empty the run stops at the gate (B8.1–B8.4 only); after the team's decisions it
   writes `frozen_recipe.json` for B (B8.5), as A's 8.5.
2. **Daily alert cap.** Decided again for B at the gate (B's scope and prediction time differ
   from A's); recorded in b08.classification.threshold.daily_alert_cap.
3. **Adoption comparison (G-79), new B code (`e5b/adoption.py`).** Per task and fold: A's frozen
   recipe (e5-A-frozen) refitted on A's training rows of that fold and scored on B's validation
   rows of the same fold; B's recommended model scored on the same rows. B is adopted for a task
   when its 5-fold mean beats A's, even by a thin margin. Paired gains per fold are shown beside
   it, and the comparison on folds 2–5 is shown as description only (B-G-01). Whatever the
   result, A and B both go to the joint test run; the test never re-chooses (G-79).
4. **Missed-dispatch rule (B-C10), new B code.** On the development period: orders whose last
   shipping limit passed with no carrier handover; counts of flagged orders, detractors among
   them, precision and the share of all detractors caught. Reported beside the classifier; not a
   model.

## 4. Outputs (per task, `pipeline_b/stages/b08/<task>/outputs/`)
As A's s08 gate and freeze (finalists, candidates, calibration and threshold tables, selection
pack, `frozen_recipe.json` after the decisions), plus `adoption_comparison.csv` (per fold: A
score, B score, paired gain; 5-fold mean and folds 2–5 mean) and, for classification,
`missed_dispatch_rule.csv`. Evidence IDs B8.1–B8.5, B8.A (adoption), B8.M (missed dispatch).

## 5. Checks
- All of A's s08 checks, run by A's code on B's inputs.
- **Equivalence test** (`tests/test_adapter.py`): the adapter fed A's inputs and A's s08
  decisions reproduces A's accepted s08 outputs, including `frozen_recipe.json` with the same
  sha256 as at e5-A-frozen.
- The adoption comparison uses A's frozen recipe file unchanged (sha256 checked) and exactly B5's
  validation rows; every refit of A uses A's s05 training rows of the same fold.
- No test row is read before B's freeze; A's tree stays FRESH and matches e5-A-frozen.

## 6. Order of work
1. Build B8 and run it: it stops at the gate (B8.1–B8.4, adoption comparison, missed-dispatch
   rule). Review tabs for B8, then the team's combined B6–B8 review.
2. The team fills `human_decisions_B.yaml` b08 (model, classification threshold and daily cap).
3. Rerun B8: freeze (B8.5), tag `e5-B-frozen`.

## 7. After the freeze
The joint test run (A's 8.6–8.8 and B8.6–B8.8 together, one test read) and the fold-by-fold table
(B-C13) get their own blueprint once B is frozen.
