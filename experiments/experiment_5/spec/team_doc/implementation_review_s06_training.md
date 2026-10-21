# s06 Training — implementation review

> **ACCEPTED · round 3 · 2026-10-21 · tag e5-s06-accepted · accepted by the experiment lead under G-78.** Accepted runs 20261021T033145Z (regression) and 20261021T033221Z (classification) on a clean tree (code commit 0734057); every output is identical to the round 3 review packs, so the cards in the sub-tabs are the accepted values. Ladder result for both tasks: linear/logistic (the tree and forest gains stay within one SE; paired gains shown as description only). Learning-curve subsets keep the most recent rows (confirmed by the lead). The team reviews s06 together with s07 and s08 at the s08 gate; a change from that review reopens s06 and the later stages rerun (G-78).

**Round 3 · LEAD REVIEW (G-78)** · runs `20261021T032208Z` (regression) and `20261021T032248Z` (classification) · coverage 6 of 6 per task, 0 MISSING · 7 + 6 checks, all PASS. Under G-78 the experiment lead reviews and accepts s06 on its own; the team reviews s06, s07 and s08 together at the s08 gate, before anything reads the test cohort. Evidence cards are in the two sub-tabs. Nothing is committed until s06 is accepted (G-64).

## Current (round 3)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | 6.1 | Pipeline factory | IMPLEMENTED | PASS | Open |
| regression | 6.2 | Families, basic to complex | IMPLEMENTED | PASS | Open |
| regression | 6.4 | Scores recorded | IMPLEMENTED | PASS | Open |
| regression | 6.5 | Residual diagnostics | IMPLEMENTED | — | Open |
| regression | 6.7 | Learning curves and design matrix | IMPLEMENTED | PASS | Open |
| regression | 6.8 | Outputs | IMPLEMENTED | — | Open |
| classification | 6.1 | Pipeline factory | IMPLEMENTED | PASS | Open |
| classification | 6.2 | Families, basic to complex | IMPLEMENTED | PASS | Open |
| classification | 6.4 | Scores recorded | IMPLEMENTED | PASS | Open |
| classification | 6.6 | Classification diagnostics | IMPLEMENTED | — | Open |
| classification | 6.7 | Learning curves and design matrix | IMPLEMENTED | PASS | Open |
| classification | 6.8 | Outputs | IMPLEMENTED | — | Open |

### Summary

Validation primary metric, mean ± SE over the 5 folds (candidates.csv). The ladder keeps a more complex family only if the one-SE rule chooses it over the current one (s01 1.7).

| Task | Metric | Families (dummy; linear/logistic; single tree; forest) | Ladder result | Best mean |
| --- | --- | --- | --- | --- |
| regression | MAE | dummy 6.4946 ± 0.6889; linear/logistic 5.4701 ± 0.6733; single tree 5.4244 ± 0.7147; forest 5.4434 ± 0.6826 | linear/logistic | single tree |
| classification | AP | dummy 0.1482 ± 0.0198; linear/logistic 0.2435 ± 0.0314; single tree 0.2158 ± 0.0233; forest 0.2544 ± 0.0267 | linear/logistic | forest |

### Points for review

1. **Paired gains of each ladder step (6.2, description only).** Regression: linear/logistic vs dummy +1.0245 days (paired SE 0.1262, better in 5 of 5 folds, kept); single tree vs linear/logistic +0.0458 days (paired SE 0.0685, better in 3 of 5 folds, not kept); forest vs linear/logistic +0.0267 days (paired SE 0.0601, better in 3 of 5 folds, not kept). Classification: linear/logistic vs dummy +0.0953 (paired SE 0.0157, better in 5 of 5 folds, kept); single tree vs linear/logistic -0.0277 (paired SE 0.0115, better in 0 of 5 folds, not kept); forest vs linear/logistic +0.0109 (paired SE 0.0063, better in 4 of 5 folds, not kept). The adoption rule is the agreed one: a more complex family is kept only when its gain over the current family clears one standard error of the fold means. The fold SE also carries the level differences between folds (drift), so a small but consistent paired gain can stay below it; s07 tunes both the linear and the tree families and compares each with its plain s06 model, and s08 makes the final choice at its gate (G-39). For information.
2. **Learning curves on the latest fold (6.7).** Regression: dummy validation mae 5.4686 with the most recent 20% vs 5.0815 with all rows; linear/logistic validation mae 3.3949 with the most recent 20% vs 3.8233 with all rows; single tree validation mae 3.7316 with the most recent 20% vs 3.6002 with all rows; forest validation mae 3.9228 with the most recent 20% vs 3.7815 with all rows; target mean in fold 5: training 13.1094, validation 9.6289. Classification: dummy validation ap 0.1081 with the most recent 20% vs 0.1081 with all rows; linear/logistic validation ap 0.2036 with the most recent 20% vs 0.2288 with all rows; single tree validation ap 0.1978 with the most recent 20% vs 0.1956 with all rows; forest validation ap 0.2327 with the most recent 20% vs 0.2365 with all rows; target mean in fold 5: training 0.1440, validation 0.1081. In regression the plain linear model does better on the most recent 20% than on all rows, while the tree models gain a little from more rows; in classification more rows help logistic and the trees are about flat. In both tasks the validation block is faster and happier than its training data (the drift seen in s03 and s05), so a training-validation gap here is partly drift, not only under- or overfitting. Nothing in the agreed design reacts to it (no sample weighting, no shorter window); s09 reports the drift. For information.
3. **Regression under-predicts on average (6.5).** linear: residual mean 3.32, median 1.28, skewness 2.65, share above +10 days 14.11%; tree: residual mean 3.22, median 1.05, skewness 2.70, share above +10 days 14.16%. The log target fits the geometric mean, which sits below the arithmetic mean of a right-skewed target; in folds 2–4 the validation lead times are also longer on average than their training data (s05 fold\_summary.csv). MAE is the primary metric and the median residual is small; s09 reports the bias. For information.
4. **Learning-curve subsets keep the most recent rows (6.7).** The blueprint says "training sizes 20–100%" without saying which rows. I keep the rows closest to the validation block, so a smaller set is not also an older one. Please confirm.
5. **Classification threshold metrics are description only (6.4).** Precision, recall and F1 are recorded at 0.5 and at the 1/6 cost cutoff; the threshold itself is chosen at the s08 hard stop (G-39).
6. **Foundation fix found while building s06.** A rerun of s04 on another day changed one cell of reduction\_rationale.csv (the run date of the automatic duplicate drop). The automatic rows now carry the accepted rule date (2026-10-20), so reruns stay byte-identical; every s01–s05 output is unchanged and those stages stay ACCEPTED and FRESH.

## Round history

### Round 1 — 2026-10-21

- First build of s06 for both tasks: new foundation module e5lib/training.py with tests/test\_training.py (51 tests pass). The foundation change made s01–s05 stale; they were rerun with byte-identical outputs and stay ACCEPTED.
- Lead review: the paired per-fold differences that s01 1.7 asks for were missing.

### Round 2 — 2026-10-21

- 6.2 gains paired\_differences.csv: the per-fold gain of each ladder step, its mean, paired SE and the folds it wins (description only; the adoption rule is unchanged: a more complex family is kept only if its gain clears one SE of the fold means).
- Superseded before review: a second rerun showed the forest predictions differing in the last digits (about 1e-14) and the fit times changing from run to run.

### Round 3 — 2026-10-21

- Forests now predict with one thread (fitting stays parallel) and fit times are written to \_manifest.json instead of fit\_log.csv, so two s06 reruns give byte-identical outputs (checked). Values and decisions are unchanged.
- Comments and resolutions: none yet.

### Acceptance — 2026-10-21

- The experiment lead reviewed round 3 and accepted s06 (G-78), confirming point 4 (learning-curve subsets keep the most recent rows).
- Code committed first (0734057), then s01–s06 rerun on the clean tree (dirty false); s06 outputs identical to round 3 and s01–s05 byte-identical. Committed and tagged e5-s06-accepted; s07 unlocks.
