# Literature register (manual checklist)

The report cites only the 12 sources of the team's audited list (`_DONOTCOMMIT/Literature/ML_Ecommerce_Literature_AUDITED.md`,
audit date 2026-10-28; the file itself is private and not committed). Each row says what the report may claim from the
source, at the source's evidence level, and where. Henry sends this table to the team; a reviewer checks each row
(the claim matches the audited summary, the link opens the publisher record, the metadata is complete) and signs it.

Rule for writing: a claim goes no further than its evidence level. "Topic only" means the source may be cited for what
it studies, never for a result or an effect size.

| # | Source (full metadata) | Link | Evidence level | Claim the report may make | Section | Checked by, date |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | James, G., Witten, D., Hastie, T., Tibshirani, R., & Taylor, J. (2023). *An Introduction to Statistical Learning: with Applications in Python*. Springer. | https://doi.org/10.1007/978-3-031-38747-0 | Book identity and overview | Bias–variance trade-off; resampling and cross-validation to estimate generalisation. Not cited for simple baselines first (the project description's rule), the one-standard-error rule or the variance inflation factor (no abstract supports them) | §2 | |
| 2 | Müller, A. C., & Guido, S. (2016). *Introduction to Machine Learning with Python: A Guide for Data Scientists*. O'Reilly. | https://www.oreilly.com/library/view/introduction-to-machine/9781449369880/ | Book identity and overview (first edition 2016) | Simple baselines; train/test separation; preprocessing inside pipelines to avoid leakage; metric choice | §2, §3, §6 | |
| 3 | Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5–32. | https://doi.org/10.1023/A:1010933404324 | Canonical technical synthesis | A random forest aggregates randomised trees; its error depends on tree strength and between-tree correlation | §2, §6 | |
| 4 | Wolpert, D. H. (1992). Stacked Generalization. *Neural Networks*, 5(2), 241–259. | https://doi.org/10.1016/S0893-6080(05)80023-1 | Canonical technical synthesis | Stacking learns from held-out predictions of first-stage models; named as considered and not used | §2 | |
| 5 | Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. | https://doi.org/10.1145/2939672.2939785 | Canonical technical synthesis | XGBoost is a scalable gradient tree boosting system; named as considered and not used | §2, §6 | |
| 6 | He, H., & Garcia, E. A. (2009). Learning from Imbalanced Data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263–1284. | https://doi.org/10.1109/TKDE.2008.239 | Canonical survey synthesis | Accuracy can hide weak minority-class detection; evaluation should reflect prevalence and error costs; resampling and cost-sensitive methods are alternatives, not requirements. Not cited for the AP baseline or for calibration harm | §1, §2 | |
| 7 | Cui, R., Lu, Z., Sun, T., & Golden, J. M. (2024). Sooner or Later? Promising Delivery Speed in Online Retail. *Manufacturing & Service Operations Management*, 26(1), 233–251. | https://doi.org/10.1287/msom.2021.0174 | Publisher abstract checked | Varying the delivery speed promised to shoppers (actual speed unchanged) raised sales and profit but also returns and reduced retention, so promises should be set for longer-run customer value; not evidence about actual delivery speed | §2, §9 | |
| 8 | Deshpande, V., & Pendem, P. K. (2023). Logistics Performance, Ratings, and Its Impact on Customer Purchasing Behavior and Sales in E-Commerce Platforms. *Manufacturing & Service Operations Management*, 25(3), 827–845. | https://doi.org/10.1287/msom.2021.1045 | Publisher metadata checked; results not audited | Topic only: the study examines how logistics performance and ratings relate to purchasing and sales on an e-commerce platform; no coefficients, effect sizes or mechanisms | §2, §5 | |
| 9 | Kandula, S., Krishnamoorthy, S., & Roy, D. (2021). A Prescriptive Analytics Framework for Efficient E-Commerce Order Delivery. *Decision Support Systems*, 147, 113584. | https://doi.org/10.1016/j.dss.2021.113584 | Journal abstract checked | Not cited (last-mile routing; outside both tasks) | — | |
| 10 | Kapoor, S., & Narayanan, A. (2023). Leakage and the Reproducibility Crisis in Machine-Learning-Based Science. *Patterns*, 4(9), 100804. | https://doi.org/10.1016/j.patter.2023.100804 | Published abstract checked | Leakage takes several forms and inflates reported results (294 affected papers across 17 fields in the published article); our prediction-time feature rules, time-ordered folds and fold-local preprocessing are stated as our application of that warning, not as its findings | §2, §3, §6 | |
| 11 | van den Goorbergh, R., van Smeden, M., Timmerman, D., & Van Calster, B. (2022). The Harm of Class Imbalance Corrections for Risk Prediction Models: Illustration and Simulation Using Logistic Regression. *Journal of the American Medical Informatics Association*, 29(9), 1525–1534. | https://doi.org/10.1093/jamia/ocac093 | Journal metadata and study focus checked | In logistic-regression risk prediction, imbalance corrections can harm the calibration of predicted risks; scope limited to that setting | §2, §6 | |
| 12 | Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? *Advances in Neural Information Processing Systems*, 35 (Datasets and Benchmarks Track). | https://proceedings.neurips.cc/paper_files/paper/2022/file/0378c7692da36807bdec87ab043cdadc-Paper-Datasets_and_Benchmarks.pdf | Proceedings paper identified; technical synthesis | On the medium-sized tabular datasets studied, tree ensembles remain strong baselines; not a claim for every setting | §2, §6 | |

## Author and claim check (2026-10-28)

- Authors and initials were read from the publisher's registered metadata (Crossref record of each DOI), the NeurIPS
  proceedings page (row 12) and library catalogue records for ISBN 9781449369415 (row 2; the O'Reilly page refused
  the request). Nothing was added from memory. The audited file carries the same check.
- Corrected: row 1 has a fifth author, J. Taylor; row 11's full author list replaces "et al."; row 12's page range
  (507–520) is not on the proceedings page and was removed; row 5 names the full proceedings.
- Dropped: ISLP (row 1) is not cited for the one-standard-error rule or the variance inflation factor. The Springer
  chapter pages for chapter 3 (Linear Regression) and chapter 6 (Linear Model Selection and Regularization) have no
  abstract that mentions either, and the audited summary does not cover them. The report already uses both without a
  citation, as the project's own rules, so no report text changes.
- Row 2: first edition, 2016, as catalogued; confirm this is the edition the team used.
- The course lecture notes and tutorials are not literature sources and are not cited as such.
