# Literature register (manual checklist)

The report cites only the 12 sources of the team's audited list (`_DONOTCOMMIT/Literature/ML_Ecommerce_Literature_AUDITED.md`,
audit date 2026-10-28; the file itself is private and not committed). Each row says what the report may claim from the
source, at the source's evidence level, and where. Henry sends this table to the team; a reviewer checks each row
(the claim matches the audited summary, the link opens the publisher record, the metadata is complete) and signs it.

Rule for writing: a claim goes no further than its evidence level. "Topic only" means the source may be cited for what
it studies, never for a result or an effect size.

| # | Source (full metadata) | Link | Evidence level | Claim the report may make | Section | Checked by, date |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | James, Witten, Hastie & Tibshirani (2023). *An Introduction to Statistical Learning: with Applications in Python*. Springer. | https://doi.org/10.1007/978-3-031-38747-0 | Book identity and overview | Bias–variance trade-off; resampling and cross-validation to estimate generalisation; simple baselines. To verify in the book before use (not in the audited summary): the one-standard-error rule; collinearity and the variance inflation factor | §2, §5, §6 | |
| 2 | Müller & Guido (2016). *Introduction to Machine Learning with Python: A Guide for Data Scientists*. O'Reilly. | https://www.oreilly.com/library/view/introduction-to-machine/9781449369880/ | Book identity and overview (first edition 2016) | Simple baselines; train/test separation; preprocessing inside pipelines to avoid leakage; metric choice | §2, §3, §6 | |
| 3 | Breiman (2001). Random Forests. *Machine Learning*, 45, 5–32. | https://doi.org/10.1023/A:1010933404324 | Canonical technical synthesis | A random forest aggregates randomised trees; its error depends on tree strength and between-tree correlation | §2, §6 | |
| 4 | Wolpert (1992). Stacked Generalization. *Neural Networks*, 5(2), 241–259. | https://doi.org/10.1016/S0893-6080(05)80023-1 | Canonical technical synthesis | Stacking learns from held-out predictions of first-stage models; named as considered and not used | §2 | |
| 5 | Chen & Guestrin (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of KDD 2016*, 785–794. | https://doi.org/10.1145/2939672.2939785 | Canonical technical synthesis | Gradient-boosted trees as a scalable tabular method; named as considered and not used | §2 | |
| 6 | He & Garcia (2009). Learning from Imbalanced Data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263–1284. | https://doi.org/10.1109/TKDE.2008.239 | Canonical survey synthesis | Accuracy can hide weak minority-class detection; evaluation should reflect prevalence and error costs; resampling and cost-sensitive methods are alternatives, not requirements | §1, §2, §6 | |
| 7 | Cui, Lu, Sun & Golden (2024). Sooner or Later? Promising Delivery Speed in Online Retail. *Manufacturing & Service Operations Management*, 26(1), 233–251. | https://doi.org/10.1287/msom.2021.0174 | Publisher abstract checked | Varying the delivery speed promised to shoppers (actual speed unchanged) raised sales and profit but also returns and reduced retention, so promises should be set for longer-run customer value; not evidence about actual delivery speed | §2, §9 | |
| 8 | Deshpande & Pendem (2023). Logistics Performance, Ratings, and Its Impact on Customer Purchasing Behavior and Sales in E-Commerce Platforms. *Manufacturing & Service Operations Management*, 25(3), 827–845. | https://doi.org/10.1287/msom.2021.1045 | Publisher metadata checked; results not audited | Topic only: the study examines how logistics performance and ratings relate to purchasing and sales on an e-commerce platform; no coefficients, effect sizes or mechanisms | §2, §5 | |
| 9 | Kandula, Krishnamoorthy & Roy (2021). A Prescriptive Analytics Framework for Efficient E-Commerce Order Delivery. *Decision Support Systems*, 147, 113584. | https://doi.org/10.1016/j.dss.2021.113584 | Journal abstract checked | Not cited (last-mile routing; outside both tasks) | — | |
| 10 | Kapoor & Narayanan (2023). Leakage and the Reproducibility Crisis in Machine-Learning-Based Science. *Patterns*, 4(9), 100804. | https://doi.org/10.1016/j.patter.2023.100804 | Published abstract checked | Leakage takes several forms and inflates reported results (294 affected papers across 17 fields in the published article); prediction-time feature rules, temporal separation and fold-local preprocessing guard against it | §2, §3 | |
| 11 | Van den Goorbergh et al. (2022). The Harm of Class Imbalance Corrections for Risk Prediction Models: Illustration and Simulation Using Logistic Regression. *Journal of the American Medical Informatics Association*, 29(9), 1525–1534. | https://doi.org/10.1093/jamia/ocac093 | Journal metadata and study focus checked | In logistic-regression risk prediction, imbalance corrections can harm the calibration of predicted risks; scope limited to that setting | §2, §6 | |
| 12 | Grinsztajn, Oyallon & Varoquaux (2022). Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? *Advances in Neural Information Processing Systems*, 35, 507–520. | https://proceedings.neurips.cc/paper_files/paper/2022/file/0378c7692da36807bdec87ab043cdadc-Paper-Datasets_and_Benchmarks.pdf | Proceedings paper identified; technical synthesis | On the medium-sized tabular datasets studied, tree ensembles remain strong baselines; not a claim for every setting | §2, §6 | |

## To check before citing

- Author names are given exactly as in the audited file (surnames only). Initials, and the full author list of row 11
  ("Van den Goorbergh et al."), are to be read from each publisher page before the reference list is final; none is
  added from memory.
- Row 2: the audited file gives the first edition as 2016; confirm the edition the team used.
- The course lecture notes and tutorials are not literature sources and are not cited as such.
