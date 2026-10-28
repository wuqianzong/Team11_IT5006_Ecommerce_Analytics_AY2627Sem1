## 2 Literature review

The literature shaped three things in this project: what the predictions are for, how the models are compared, and
how the evaluation guards against optimistic results. We organise it around our two questions and our method, and
for each source we state the choice it supports. Every source was checked against the publisher's record; a source
whose detailed results were not audited is cited only for the question it studies.

### 2.1 Delivery promises and customer response

**Delivery time and the promise.** Cui et al. (2024) separate the delivery speed promised to shoppers from the speed
actually delivered. In an experiment with an online retailer they varied only the displayed promise, while the
physical delivery stayed the same. Faster promises raised sales and profit, but also raised returns and reduced
customer retention, and the authors argue that promises should be set for longer-run customer value rather than for
conversion alone. This is why our lead-time model is framed as the input to a promise range (section 9) and not as a
single date to display: a promise that is too optimistic has a cost after the purchase.

**Logistics and ratings.** Deshpande and Pendem (2023) study how logistics performance and ratings relate to
purchasing behaviour and sales on an e-commerce platform. We cite their study for the question it addresses, the link
between logistics and the ratings customers give, which is the link our detractor alert relies on; we do not cite
specific effects from it. Our own data shows the size of that link for Olist directly (section 4).

**Gap.** None of the audited sources predicts a bad review at the moment a parcel is handed to the carrier, or
separates the seller's dispatch delay from the carrier's transit time. Both are central to this project: the alert
is made at handover, and the new features measure the seller's and the route's delivery history separately
(section 5).

### 2.2 Choosing and comparing models

**Simple models first.** James et al. (2023) and Müller and Guido (2016) set out the practice we follow: start from a
trivial baseline and a simple model, estimate generalisation by resampling, and add complexity only when it improves
held-out performance. Müller and Guido also stress fitting preprocessing inside a pipeline, so that it does not leak
information from the evaluation data. Our
model ladder (section 6.2) starts from a dummy and from plain linear and logistic regression for exactly this reason.

**Tree ensembles.** A random forest averages many randomised trees, and its error depends on the strength of the
individual trees and the correlation between them (Breiman, 2001). On the medium-sized tabular datasets they studied,
tree ensembles remained strong baselines against deep learning (Grinsztajn et al., 2022). We therefore use the forest
as the non-linear comparison for both tasks, alongside a single tree, rather than a neural network.

**Considered and not used.** Stacked generalisation learns a second-stage model from the held-out predictions of
first-stage models (Wolpert, 1992), and gradient-boosted trees are a scalable alternative for tabular data (Chen and
Guestrin, 2016). The project limits the number of model families, and the forest itself did not beat the simpler
models by more than the selection rule requires, so neither was added (section 6.2).

### 2.3 Evaluation without optimism

**Leakage.** Kapoor and Narayanan (2023) show that leakage takes several forms beyond overlap between training and
test rows, propose a taxonomy of leakage types, and find it inflating reported results across many published studies.
Our defences are our own application of that warning: a leakage rule
for each prediction moment, time-ordered folds that purge returning customers, preprocessing fitted inside each fold,
and a test period read once (sections 3 and 6).

**Imbalanced targets.** He and Garcia (2009) review learning with unequal class sizes: accuracy can hide weak
detection of the minority class, evaluation should reflect the class balance and the cost of each error, and
resampling or cost-sensitive learning are options rather than requirements. Detractors are a minority of orders, so we
judge the alert by average precision against the detractor share and set its threshold from an assumed cost ratio.
For logistic risk models, Van den Goorbergh et al. (2022) show that imbalance corrections can harm the calibration of
the predicted risks. Our alert needs calibrated probabilities to apply a cost threshold, so we tested class weighting
as a grid option but did not resample (section 6.3).

### 2.4 What we take from the literature

| Source | What it supports in this project | Section |
| --- | --- | --- |
| Cui et al. (2024) | Treat the lead-time prediction as input to a promise range, set for longer-run value | 9 |
| Deshpande and Pendem (2023) | Logistics performance and ratings are linked; the alert targets that link | 1, 5 |
| James et al. (2023); Müller and Guido (2016) | Baselines first, resampling, preprocessing inside the pipeline | 3, 6 |
| Breiman (2001); Grinsztajn et al. (2022) | The random forest as the non-linear comparison on tabular data | 6 |
| Wolpert (1992); Chen and Guestrin (2016) | Stacking and boosting, considered and not used | 6 |
| Kapoor and Narayanan (2023) | Leakage rules per prediction moment, time-ordered folds, fold-local preprocessing | 3, 6 |
| He and Garcia (2009) | Average precision and a cost threshold instead of accuracy | 1, 6 |
| Van den Goorbergh et al. (2022) | Class weighting tested; no resampling, to keep probabilities calibrated | 6 |
