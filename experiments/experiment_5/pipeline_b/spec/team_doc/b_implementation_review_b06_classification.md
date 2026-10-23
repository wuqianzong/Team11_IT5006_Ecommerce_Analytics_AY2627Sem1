# B6 › classification — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s06-accepted) · run `20261023T162918Z` on code commit e358f81 (clean tree) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B6 Training"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B6 = A's s06 on B's inputs: dummy, plain linear/logistic, single tree, forest; the basic-to-complex ladder under the one-SE rule; paired gains as description; residual and classification diagnostics; learning curves. Same code, other inputs (no copy).

## B6.1

**What was done:** 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (135,093 training rows over the folds). Learned imputation values per fold are in imputation\_by\_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros).

**Check** preprocessing fitted inside the training fold only (learned medians equal the training-fold medians): PASS (15 fitted pipelines checked) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs): PASS (selected set of 25 features)

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): imputation\_by\_fold.csv

## B6.2

**What was done:** Families basic to complex, validation ap mean ± SE over the folds: dummy 0.1380 ± 0.0198; linear/logistic 0.2616 ± 0.0349; single tree 0.2394 ± 0.0354; forest 0.2739 ± 0.0305. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest).

**Candidates** (candidates.csv):

| candidate\_id | family | validation\_mean | validation\_se | kept | reason |
| --- | --- | --- | --- | --- | --- |
| clf.sel.log.dummy\_prior | dummy | 0.1380 | 0.0198 | True | baseline (simplest family) |
| clf.sel.log.logistic | linear/logistic | 0.2616 | 0.0349 | True | kept: beats dummy by more than one SE |
| clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100 | single tree | 0.2394 | 0.0354 | False | not kept: within one SE of linear/logistic, the simpler family stays |
| clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | forest | 0.2739 | 0.0305 | False | not kept: within one SE of linear/logistic, the simpler family stays |

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs): PASS (selected set of 25 features) **Check** the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest): PASS

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): candidates.csv, counts.json, decision.json, paired\_differences.csv; plus 3 figure/curve files

## B6.4

**What was done:** metrics\_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric (threshold metrics at 0.5 and 1/6); fit\_log.csv: rows and warnings per fit, fit times in \_manifest.json (convergence warnings: 0); predictions.csv.gz: 200,860 out-of-fold predictions.

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): fit\_log.csv, metrics\_long.csv, predictions.csv.gz; plus 3 figure/curve files

## B6.6

**What was done:** Pooled out-of-fold PR, ROC and reliability curves for every family, Brier score, and the predicted-probability histogram per class for the best non-dummy family. dummy: AP 0.1406, ROC-AUC 0.5012, Brier 0.1207; linear/logistic: AP 0.2587, ROC-AUC 0.6531, Brier 0.1152; single tree: AP 0.2556, ROC-AUC 0.6444, Brier 0.1144; forest: AP 0.2684, ROC-AUC 0.6642, Brier 0.1150.

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): oof\_diagnostics.csv, predictions.csv.gz; plus 15 figure/curve files

## B6.7

**What was done:** Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (8,646 rows). Linear/logistic design matrix per training fold: fold 1 rank 134 of 134, condition number 910; fold 2 rank 142 of 142, condition number 913; fold 3 rank 143 of 143, condition number 834; fold 4 rank 144 of 144, condition number 865; fold 5 rank 144 of 144, condition number 934.

**Check** linear/logistic design matrix full rank in every training fold: PASS (fold 1 rank 134 of 134; fold 2 rank 142 of 142; fold 3 rank 143 of 143; fold 4 rank 144 of 144; fold 5 rank 144 of 144)

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): design\_matrix\_by\_fold.csv; plus 4 figure/curve files

## B6.8

**What was done:** Outputs: metrics\_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit\_log.csv, imputation\_by\_fold.csv, design\_matrix\_by\_fold.csv, curves/ and figures/ with sidecar data.

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): counts.json
