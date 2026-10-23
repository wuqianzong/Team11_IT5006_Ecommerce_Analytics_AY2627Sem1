# B6 › regression — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s06-accepted) · run `20261023T162830Z` on code commit e358f81 (clean tree) · 7 checks, all PASS. Coverage and review dropdowns are on the parent tab "B6 Training"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B6 = A's s06 on B's inputs: dummy, plain linear/logistic, single tree, forest; the basic-to-complex ladder under the one-SE rule; paired gains as description; residual and classification diagnostics; learning curves. Same code, other inputs (no copy).

## B6.1

**What was done:** 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (137,255 training rows over the folds). Learned imputation values per fold are in imputation\_by\_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros).

**Check** preprocessing fitted inside the training fold only (learned medians equal the training-fold medians): PASS (15 fitted pipelines checked) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs, log target): PASS (selected set of 21 features) **Check** regression scored on raw days (log target inverted): PASS

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): imputation\_by\_fold.csv

## B6.2

**What was done:** Families basic to complex, validation mae mean ± SE over the folds: dummy 5.9689 ± 0.7107 days; linear/logistic 5.0247 ± 0.6115 days; single tree 5.0532 ± 0.6394 days; forest 4.9627 ± 0.6457 days. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest).

**Candidates** (candidates.csv):

| candidate\_id | family | validation\_mean | validation\_se | kept | reason |
| --- | --- | --- | --- | --- | --- |
| reg.sel.log.dummy\_median | dummy | 5.9689 | 0.7107 | True | baseline (simplest family) |
| reg.sel.log.linear | linear/logistic | 5.0247 | 0.6115 | True | kept: beats dummy by more than one SE |
| reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100 | single tree | 5.0532 | 0.6394 | False | not kept: within one SE of linear/logistic, the simpler family stays |
| reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | forest | 4.9627 | 0.6457 | False | not kept: within one SE of linear/logistic, the simpler family stays |

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs, log target): PASS (selected set of 21 features) **Check** the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest): PASS

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): candidates.csv, counts.json, decision.json, paired\_differences.csv; plus 3 figure/curve files

## B6.4

**What was done:** metrics\_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric; fit\_log.csv: rows and warnings per fit, fit times in \_manifest.json (convergence warnings: 0); predictions.csv.gz: 202,472 out-of-fold predictions.

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34) **Check** regression scored on raw days (log target inverted): PASS

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): fit\_log.csv, metrics\_long.csv, predictions.csv.gz; plus 3 figure/curve files

## B6.5

**What was done:** Residual vs fitted, histogram and Q-Q plot on out-of-fold predictions of the plain linear model and the better tree model (forest). linear: residual mean 2.92, median 1.10, skewness 2.36, share above +10 days 12.22%; forest: residual mean 2.57, median 0.51, skewness 2.47, share above +10 days 11.99%.

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): predictions.csv.gz; plus 5 figure/curve files

## B6.7

**What was done:** Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (9,059 rows). Linear/logistic design matrix per training fold: fold 1 rank 130 of 130, condition number 245; fold 2 rank 138 of 138, condition number 285; fold 3 rank 139 of 139, condition number 243; fold 4 rank 140 of 140, condition number 386; fold 5 rank 140 of 140, condition number 434.

**Check** linear/logistic design matrix full rank in every training fold: PASS (fold 1 rank 130 of 130; fold 2 rank 138 of 138; fold 3 rank 139 of 139; fold 4 rank 140 of 140; fold 5 rank 140 of 140)

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): design\_matrix\_by\_fold.csv; plus 4 figure/curve files

## B6.8

**What was done:** Outputs: metrics\_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit\_log.csv, imputation\_by\_fold.csv, design\_matrix\_by\_fold.csv, curves/ and figures/ with sidecar data.

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): counts.json
