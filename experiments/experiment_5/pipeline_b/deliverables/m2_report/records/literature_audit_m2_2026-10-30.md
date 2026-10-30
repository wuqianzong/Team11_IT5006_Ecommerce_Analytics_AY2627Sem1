# Literature audit for the Milestone 2 report (2026-10-30)

The Milestone 2 report cites only sources from the final report's literature register
(`deliverables/report/records/literature_register.md`, itself drawn from the team's audited list). Each source was
checked again on 2026-10-30, for this report, in three steps:

1. **Link:** the DOI resolves to the publisher record (Crossref API, `api.crossref.org/works/<DOI>`); the book links
   resolve to the publisher or a library catalogue.
2. **Metadata:** title, authors, year, venue, volume, issue and pages read from that record and compared with the
   reference list. All match; nothing was corrected.
3. **Content:** the abstract (Crossref, the NeurIPS proceedings page, OpenAlex or Semantic Scholar) supports the
   exact claim the report makes, at the register's evidence level, and the claim is relevant to the section.

| Source | Link checked | Abstract or record says | Claim in the M2 report | Section | Relevant because |
| --- | --- | --- | --- | --- | --- |
| Cui et al. (2024), MSOM 26(1) 233–251 | doi.org/10.1287/msom.2021.0174 (Crossref) | Field experiment varying the promised delivery speed with physical speed unchanged; a faster promise increases sales and profits but also returns and reduces customer retention | Faster delivery promises raised sales and profit but reduced customer retention | 1 | The lead-time model sets the promise; this is why the promise must be realistic |
| Deshpande and Pendem (2023), MSOM 25(3) 827–845 | doi.org/10.1287/msom.2021.1045 (Crossref) | Examines how delivery time and requested speed affect logistics ratings and third-party sellers' sales (Tmall/Cainiao, 15 million orders) | Topic only: logistics performance is studied alongside ratings and sales; no effect cited | 4 | Grounds the choice of seller and logistics predictors for the alert, without borrowing a result |
| He and Garcia (2009), IEEE TKDE 21(9) 1263–1284 | doi.org/10.1109/TKDE.2008.239 (Crossref, OpenAlex abstract) | Review of learning from imbalanced data, including assessment metrics | With imbalanced classes, accuracy can hide weak detection of the minority class | 1 | Justifies AP over accuracy for a 10–15% minority |
| Kapoor and Narayanan (2023), Patterns 4(9) 100804 | doi.org/10.1016/j.patter.2023.100804 (Crossref, Semantic Scholar abstract) | Leakage found in 17 fields affecting 294 papers; taxonomy of eight leakage types | Leakage takes several forms; our defence is fitting every learned step inside the training fold | 2 | Justifies the leakage rules and fold-fitted preprocessing |
| Müller and Guido (2016), O'Reilly | O'Reilly page; Open Library record for ISBN 9781449369415 (O'Reilly Media, 2016) | Introductory book on scikit-learn practice | Preprocessing inside pipelines; simple baselines | 2, 5 | The report's pipelines follow this practice |
| James et al. (2023), Springer | doi.org/10.1007/978-3-031-38747-0 (Crossref) | Textbook; five authors as listed | Bias–variance trade-off; resampling estimates generalisation | 5 | Justifies the model ladder and cross-validation |
| Breiman (2001), Machine Learning 45(1) 5–32 | doi.org/10.1023/A:1010933404324 (Crossref, Semantic Scholar abstract) | Forests combine randomised trees; error depends on tree strength and correlation | A random forest averages many randomised trees | 5 | Describes the forest family in the ladder |
| Grinsztajn et al. (2022), NeurIPS 35 Datasets and Benchmarks | proceedings.neurips.cc page for the paper | Tree-based models remain state-of-the-art on medium-sized tabular data (45 datasets) | Tree ensembles are strong baselines on medium-sized tabular data | 5 | Why the forest is the non-linear comparison |
| van den Goorbergh et al. (2022), JAMIA 29(9) 1525–1534 | doi.org/10.1093/jamia/ocac093 (Crossref abstract) | Undersampling, oversampling and SMOTE gave poorly calibrated logistic models, overestimating minority risk, without better AUC | Imbalance corrections can harm calibration of logistic risk models; so no resampling | 5 | The 1/6 threshold needs calibrated probabilities |

Not cited in the M2 report: Wolpert (1992) and Chen and Guestrin (2016) (no stacking or boosting is discussed),
Kandula et al. (2021) (outside both tasks).
