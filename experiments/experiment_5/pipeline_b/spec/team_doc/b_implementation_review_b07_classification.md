# B7 › classification — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s07-accepted) · run `20261023T164241Z` on code commit e358f81 (clean tree) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B7 Tuning"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B7 = A's s07 on B's inputs: A's grids per family; one-SE choice inside each grid and against the plain B6 model (G-55). Same code, other inputs (no copy).

## B7.2

**What was done:** linear/logistic: 18 configurations; best mean 0.2734 ({'C': 0.01, 'class\_weight': None}); one-SE choice {"C": 0.01, "class\_weight": null} with 0.2734 ± 0.0318.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv

## B7.3

**What was done:** single tree: 72 configurations; best mean 0.2394 ({'class\_weight': None, 'max\_depth': 5, 'min\_samples\_leaf': 100}); one-SE choice {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} with 0.2298 ± 0.0297.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv

## B7.4

**What was done:** forest: 48 configurations; best mean 0.2761 ({'class\_weight': None, 'max\_depth': 8, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 0.2625 ± 0.0297.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv

## B7.5

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring average\_precision, refit=False, return\_train\_score=True, seed 42; 138 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.1236, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0222, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0123, better in 4 of 5 folds); result linear/logistic.

**Plain B6 model against the family's tuned one-SE choice** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_best | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 0.2616 | clf.sel.log.logistic.C=0.01.class\_weight=none | 0.2734 | 0.0318 | 0.0118 | 0.0051 | 4 | plain |
| single tree | 0.2394 | clf.sel.log.tree\_clf.class\_weight=none.max\_depth=4.min\_samples\_leaf=200 | 0.2298 | 0.0297 | -0.0096 | 0.0076 | 1 | plain |
| forest | 0.2739 | clf.sel.log.forest\_clf.class\_weight=none.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200 | 0.2625 | 0.0297 | -0.0114 | 0.0026 | 0 | plain |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## B7.6

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic -0.0463; single tree -0.0304; forest -0.0230.

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv; plus 12 figure/curve files

## B7.7

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): counts.json, oof\_scores.csv, predictions.csv.gz
