# B8 — selection, gate and freeze (blueprint)

| Field | Value |
| --- | --- |
| Stage | B8, Pipeline B (G-79; CR-054 B-C10, B-C13) |
| Nodes | regression, classification |
| Status | DRAFT |
| Inherits from A | e5lib/selection.py (finalists, one-SE recommendation, calibration, threshold table, freeze) |

## 1. Goal and gate
Goal: choose B's model, calibration and threshold at a human gate, compare B with A on the same
rows (G-79 adoption rule), and freeze B without reading the test.
Gate: team decisions in `human_decisions_B.yaml` b08; frozen_recipe_B.json written before any
test row is read.

## 2. Method
1. **B8.1–B8.4** as A's 8.1–8.4 (finalists, one-SE recommendation, calibration raw vs sigmoid,
   threshold table) on B's rows. The daily alert cap is decided again for B, because B's scope
   and prediction time differ from A's.
2. **Adoption comparison (G-79).** Per task: A's frozen recipe (e5-A-frozen) refitted per fold
   on A's training rows and scored on B's validation rows, against B's recommended model on the
   same rows. B is adopted for a task when its 5-fold mean beats A's, even by a thin margin.
   Paired gains are shown beside it. Whatever the result, A and B both go to the joint test run.
3. **Missed-dispatch rule (B-C10).** Orders whose shipping limit passed with no handover,
   counted on the development period: flagged orders, detractors among them, precision and the
   share of all detractors caught.
4. **Freeze (B8.5).** frozen_recipe_B.json with its sha256, as A's 8.5.

## 3. Outputs (per task, `pipeline_b/stages/b08/<task>/outputs/`)
As A's s08 gate and freeze, plus `adoption_comparison.csv` and (classification)
`missed_dispatch_rule.csv`.

## 4. After the freeze
The joint test run (A's 8.6–8.8 and B8.6–B8.8 together) and the fold-by-fold table (B-C13) are
drafted as their own blueprint once B is frozen.
