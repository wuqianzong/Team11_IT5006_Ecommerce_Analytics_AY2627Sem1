# Pipeline B team-doc mirror (read-only, for audit)

**The team works in the commented doc, not here.** These files are a read-only Markdown export of the
Pipeline B tabs of the team doc (Claude Docs artifact `21432fd4-4cc0-4d68-8fa2-4e0414fffe5e`), kept
inside pipeline_b/ so Pipeline A's `../../spec/team_doc/` is never touched (README rule 1). Never
edit them, review them or treat a change here as a decision. They are refreshed, never edited by
hand, in the commit that accepts each B stage; git history keeps every earlier snapshot.

- **Exported:** 2026-10-23, at B2 round 2 and B4 acceptance (tags e5-B-s02-accepted-r2, e5-B-s04-accepted); CR-054 and overview refreshed after their AMENDED notes (B-CR-06); B5 tabs and the parent progress table added at B5 acceptance (tag e5-B-s05-accepted); B6 and B7 tabs added at their acceptance (tags e5-B-s06-accepted, e5-B-s07-accepted). The B6/B7 files are the exact Markdown uploaded to those tabs, with dropdowns written as "Open" (their value at upload); the B7 tabs include the full grid tables added 2026-10-24 (B-CR-11). At the B8 freeze (tag e5-B-frozen): the parent and B8 stage tabs are exports; the two B8 task tabs are the generated Markdown uploaded to them (the regression tab also carries the within\_3d note). They show the gate-time tables; the frozen figures are in the B8 stage tab and in EVIDENCE.md's current b08 runs. At B9 acceptance (tag e5-B-s09-accepted, 2026-10-25): B9 stage and sub-tabs, Report notes, the blueprints tab, and every B2–B8 sub-tab (now with its "Supplement for decisions and the report" section) re-exported. The supplements Claude added to Pipeline A's s06–s08 sub-tabs are mirrored here as `a_supplement_*.md` (whole tab exports), because Pipeline A's folders are never written (README rule 1). Charts and images appear as placeholders in exports; the source PNGs are in the stage output folders.
- **Not here:** comment threads (their outcomes are in `../decision_log_B.md` and the stage cards),
  dropdowns (exported as their text, e.g. "Open"), the overview chart (a placeholder).
- **Amended text:** CR-054 B-C3 and B-C6 and the overview's cap keep their approved wording, with
  an AMENDED note pointing to B-G-03 and B-G-04. Which evidence is current is decided only by
  `../../EVIDENCE.md`.

| Doc tab | File | Doc revision |
| --- | --- | --- |
| Pipeline B (A + change request) | [pipeline_b_overview.md](pipeline_b_overview.md) | 6 |
| CR-054 change request | [pipeline_b_cr054_change_request.md](pipeline_b_cr054_change_request.md) | 17 |
| B blueprints B2–B9 and joint test | [pipeline_b_blueprints.md](pipeline_b_blueprints.md) | 13 |
| B implementation reviews | [b_implementation_reviews.md](b_implementation_reviews.md) | 12 |
| B implementation reviews › B2 Population and features | [b_implementation_review_b02.md](b_implementation_review_b02.md) | 4 |
| B2 › regression | [b_implementation_review_b02_regression.md](b_implementation_review_b02_regression.md) | 5 |
| B2 › classification | [b_implementation_review_b02_classification.md](b_implementation_review_b02_classification.md) | 5 |
| B implementation reviews › B4 Features | [b_implementation_review_b04.md](b_implementation_review_b04.md) | 4 |
| B4 › regression | [b_implementation_review_b04_regression.md](b_implementation_review_b04_regression.md) | 5 |
| B4 › classification | [b_implementation_review_b04_classification.md](b_implementation_review_b04_classification.md) | 5 |
| B implementation reviews › B5 Partition | [b_implementation_review_b05.md](b_implementation_review_b05.md) | 2 |
| B5 › regression | [b_implementation_review_b05_regression.md](b_implementation_review_b05_regression.md) | 3 |
| B5 › classification | [b_implementation_review_b05_classification.md](b_implementation_review_b05_classification.md) | 3 |
| B implementation reviews › B6 Training | [b_implementation_review_b06.md](b_implementation_review_b06.md) | 2 |
| B6 › regression | [b_implementation_review_b06_regression.md](b_implementation_review_b06_regression.md) | 3 |
| B6 › classification | [b_implementation_review_b06_classification.md](b_implementation_review_b06_classification.md) | 3 |
| B implementation reviews › B7 Tuning | [b_implementation_review_b07.md](b_implementation_review_b07.md) | 2 |
| B7 › regression | [b_implementation_review_b07_regression.md](b_implementation_review_b07_regression.md) | 8 |
| B7 › classification | [b_implementation_review_b07_classification.md](b_implementation_review_b07_classification.md) | 7 |
| B implementation reviews › B8 Selection (gate) | [b_implementation_review_b08.md](b_implementation_review_b08.md) | 15 |
| B8 › regression | [b_implementation_review_b08_regression.md](b_implementation_review_b08_regression.md) | 6 (export) |
| B8 › classification | [b_implementation_review_b08_classification.md](b_implementation_review_b08_classification.md) | 4 (export) |
| B implementation reviews › T1 Joint test | [t1_joint_test.md](t1_joint_test.md) | 2 (charts and images appear as placeholders in the export) |
| T1 › regression | [t1_joint_test_regression.md](t1_joint_test_regression.md) | 2 |
| T1 › classification | [t1_joint_test_classification.md](t1_joint_test_classification.md) | 2 |
| B implementation reviews › B9 Conclusion (team review) | [b_implementation_review_b09.md](b_implementation_review_b09.md) | 21 |
| B9 › regression | [b_implementation_review_b09_regression.md](b_implementation_review_b09_regression.md) | 4 |
| B9 › classification | [b_implementation_review_b09_classification.md](b_implementation_review_b09_classification.md) | 6 |
| Report notes (A and B) | [report_notes_a_and_b.md](report_notes_a_and_b.md) | 3 |
| A s06 › regression (supplement) | [a_supplement_s06_regression.md](a_supplement_s06_regression.md) | 8 |
| A s06 › classification (supplement) | [a_supplement_s06_classification.md](a_supplement_s06_classification.md) | 7 |
| A s07 › regression (supplement) | [a_supplement_s07_regression.md](a_supplement_s07_regression.md) | 4 |
| A s07 › classification (supplement) | [a_supplement_s07_classification.md](a_supplement_s07_classification.md) | 4 |
| A s08 › regression (supplement) | [a_supplement_s08_regression.md](a_supplement_s08_regression.md) | 4 |
| A s08 › classification (supplement) | [a_supplement_s08_classification.md](a_supplement_s08_classification.md) | 4 |
