# B7 › regression — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s07-accepted) · run `20261023T163311Z` on code commit e358f81 (clean tree) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B7 Tuning"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B7 = A's s07 on B's inputs: A's grids per family; one-SE choice inside each grid and against the plain B6 model (G-55). Same code, other inputs (no copy).

## B7.1

**What was done:** linear/logistic: 9 configurations; best mean 5.0191 days ({'alpha': 20.0}); one-SE choice {"alpha": 100.0} with 5.0205 ± 0.5946 days.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv

## B7.3

**What was done:** single tree: 36 configurations; best mean 4.9735 days ({'max\_depth': 8, 'min\_samples\_leaf': 100}); one-SE choice {"max\_depth": 4, "min\_samples\_leaf": 200} with 5.0841 ± 0.6443 days.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv

## B7.4

**What was done:** forest: 24 configurations; best mean 4.8867 days ({'max\_depth': 18, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 5.0821 ± 0.6490 days.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv

## B7.5

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring neg\_mean\_absolute\_error, refit=False, return\_train\_score=True, seed 42; 69 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.9442 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0285 days, better in 2 of 5 folds); forest not kept over linear/logistic (paired gain +0.0619 days, better in 3 of 5 folds); result linear/logistic.

**Plain B6 model against the family's tuned one-SE choice** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_best | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 5.0247 | reg.sel.log.ridge.alpha=100 | 5.0205 | 0.5946 | 0.0041 | 0.0270 | 3 | plain |
| single tree | 5.0532 | reg.sel.log.tree\_reg.max\_depth=4.min\_samples\_leaf=200 | 5.0841 | 0.6443 | -0.0309 | 0.0269 | 1 | plain |
| forest | 4.9627 | reg.sel.log.forest\_reg.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200 | 5.0821 | 0.6490 | -0.1193 | 0.0260 | 0 | plain |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## B7.6

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic +1.1421 days; single tree +1.0608 days; forest +1.0320 days.

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv; plus 12 figure/curve files

## B7.7

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): counts.json, oof\_scores.csv, predictions.csv.gz
