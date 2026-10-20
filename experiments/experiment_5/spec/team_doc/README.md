# Team doc mirror (read-only, for audit)

**The team works in the commented doc, not here.** These files are a read-only mirror: never edit
them, never review or comment on them, and never treat a change here as a decision. Markdown export of every tab of the team doc "Feature solution — stages s02 to s05" (Claude Docs
artifact `21432fd4-4cc0-4d68-8fa2-4e0414fffe5e`), so an auditing agent can check the repository
against the documents the team approved without access to the doc (G-65).

- **Exported:** 2026-10-20, at the s04 acceptance (CR-044 to CR-048): every tab, with the s04 review tab and its two task sub-tabs added. Only the implementation reviews tab and the new s04 tabs changed in content; the others are re-exported unchanged. Earlier exports: after s01 (CR-032), s02 (CR-035), s03 (CR-039), CR-040, CR-041, CR-042 and CR-043.
- **Refreshed:** in the same commit that accepts each stage (README §9.1 step 6). Files are
  replaced, never edited by hand; git history keeps every earlier snapshot.
- **What is not here:** comment threads (their outcomes are in the decision log and the stage
  cards), dropdown widgets (exported as their text value, e.g. "Approved"), and the Pipeline v2
  chart (exported as a placeholder; its content is the box-to-ID table below the chart and
  `spec/pipeline_design.md`).
- **Authority:** the doc is where the team reviews and decides; the AGREED blueprints,
  `spec/protocol.yaml` and the decision log record those decisions in the repository. This mirror
  only shows what the doc said at export time; any difference is a finding to report.

| Doc tab | File | Doc revision |
| --- | --- | --- |
| Pipeline v2 (frozen) | [pipeline_v2.md](pipeline_v2.md) | 39 |
| Feature solution (s02–s05, frozen) | [feature_solution_s02-s05.md](feature_solution_s02-s05.md) | 123 |
| Model solution (s01, s06–s10) | [model_solution_s01_s06-s10.md](model_solution_s01_s06-s10.md) | 200 |
| Implementation reviews | [implementation_reviews.md](implementation_reviews.md) | 36 |
| Implementation reviews › s01 Problem | [implementation_review_s01_problem.md](implementation_review_s01_problem.md) | 21 |
| Implementation reviews › s02 Data | [implementation_review_s02_data.md](implementation_review_s02_data.md) | 26 |
| Implementation reviews › s03 EDA | [implementation_review_s03_eda.md](implementation_review_s03_eda.md) | 30 |
| Implementation reviews › s03 EDA › regression | [implementation_review_s03_eda_regression.md](implementation_review_s03_eda_regression.md) | 8 |
| Implementation reviews › s03 EDA › classification | [implementation_review_s03_eda_classification.md](implementation_review_s03_eda_classification.md) | 15 |
| Implementation reviews › s04 Features | [implementation_review_s04_features.md](implementation_review_s04_features.md) | 19 |
| Implementation reviews › s04 Features › regression | [implementation_review_s04_features_regression.md](implementation_review_s04_features_regression.md) | 4 |
| Implementation reviews › s04 Features › classification | [implementation_review_s04_features_classification.md](implementation_review_s04_features_classification.md) | 4 |
