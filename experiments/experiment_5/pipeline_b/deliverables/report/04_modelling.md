## 4 Modelling approach

**Two pipelines, one change request.** Pipeline A replays the course workflow in ten steps (problem, data, EDA, features, partition, training, tuning, selection, conclusion, release). Pipeline B is A plus change request CR-054 and nothing else: B's population, prediction moment and new features; every other choice (folds, model families, grids, selection rule, metrics, calibration and threshold procedure) is inherited from A and reused through A's own code.

**Features.** Each task starts from A's predictor pool plus B's new candidates. Features are ranked on development rows (Spearman correlation with the log target for regression, mutual information for classification) and the top features reaching 99% of the cumulative share are kept. Day counts are log1p-transformed; numeric features are scaled and categories one-hot encoded (first level dropped for linear models). Every step is inside one scikit-learn pipeline fitted per training fold.

**Validation.** Five chronological, customer-purged folds plus the held-out test period (figure: time-ordered folds). We do not use random or stratified splits because orders are dated and customers return: a random split would train on the future. Instead each fold's class support is checked against minimums set in advance.

**Model ladder (two families).** Dummy baseline → plain linear regression / unregularised logistic regression → single decision tree → random forest, then grid tuning of each family, all on the same folds. Class weight (none or balanced) is a grid option for the classifiers.

**Selection.** The one-SE rule keeps the simplest model within one standard error of the best fold mean. In both tasks the forest had the best mean but stayed within one SE, so the plain linear model (regression) and plain logistic model (classification) were selected. The classifier's probabilities are sigmoid-calibrated (as A, so A and B share one probability scale), and the alert threshold of 1/6 follows from the 5:1 cost.

**Ensembles.** The random forest is our ensemble (bagged trees). Stacking or voting were optional in the brief; within the course's limit on model families we did not add them, and the forest did not beat the simple models by more than one SE.

**Adoption of B.** On the same validation rows, B's selected model beat A's frozen model in both tasks, so B is the delivered model; both went to the single test read.
