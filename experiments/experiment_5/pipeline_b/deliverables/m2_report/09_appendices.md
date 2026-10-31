## Appendices

### A. Validation folds

*Table A1. Fold windows and sizes, lead time.*

{{table:M2.reg.folds}}

*Table A2. Fold windows and sizes, detractor alert.*

{{table:M2.clf.folds}}

### B. Derived features, multicollinearity and selection

**Derived features.** Almost every feature is computed from the nine raw tables rather than read from one column; a feature read straight from a raw column shows that column. Table B1 gives the formula of each, as stored with the feature pipeline. Order-level sums, counts and shares are taken over the order's items after the joins of section 2.

*Table B1. Features and how each is derived (both tasks; the missing-value indicators are added inside each fold).*

{{table:APX.features_derived_A}}

*Table B2. Variance inflation factors, lead time.*

{{table:A3.reg.vif}}

*Table B3. Variance inflation factors, detractor alert.*

{{table:A3.clf.vif}}

*Table B4. Selection ranking and the 99% rule, lead time (absolute Spearman correlation).*

{{table:M2.reg.selection_ranking}}

*Table B5. Selection ranking and the 99% rule, detractor alert (mutual information).*

{{table:M2.clf.selection_ranking}}

### C. Plain against tuned models

*Table C1. Plain against tuned models, lead time (validation MAE in days).*

{{table:M2.reg.plain_vs_tuned}}

*Table C2. Plain against tuned models, detractor alert (validation AP).*

{{table:M2.clf.plain_vs_tuned}}

### D. Coefficients and odds ratios

The largest coefficients of the frozen models, on the transformed inputs. For lead time, a coefficient multiplies the predicted lead time by its ratio per unit; for the alert, the odds ratio multiplies the odds of a detractor.

*Figure: Coefficients, lead time (F.M2A.reg.coefficients) and odds ratios, detractor alert (F.M2A.clf.coefficients).*

### E. Declaration of AI use

The team used Anthropic's Claude (Claude Code) throughout. It wrote and ran most of the pipeline code under the team's instructions, drafted the stage documentation, built the number register, and drafted this report. The team set the problem, the scope and every decision recorded in the project's decision logs, reviewed each stage before it was accepted, and checked the drafts. Every number in the report is filled from the stored pipeline outputs through the register, never typed. Every reference was checked against the publisher's record, and each claim made from a source was checked against that source's abstract (literature audit record).
