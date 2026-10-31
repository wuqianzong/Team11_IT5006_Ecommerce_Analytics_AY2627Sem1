# Literature audit, 2026-10-29

Second audit of every citation in the final report sources (`00`–`12_*.md`), made before the reworked Phase 2
report reuses them. Three checks per source: the source exists and its metadata is right (publisher record), the
link resolves, and each claim made from it is supported by the audited summary
(`ML_Ecommerce_Literature_AUDITED.md`, 2026-10-28, kept outside the repository). Nothing was taken from memory.

## 1. Identity and links

Read from Crossref (`https://api.crossref.org/works/<DOI>`) for the nine DOIs, from the NeurIPS proceedings page for
Grinsztajn et al., and from the Open Library ISBN record (9781449369415) for Müller and Guido.

| Source | Publisher record | Link | Result |
| --- | --- | --- | --- |
| James, Witten, Hastie, Tibshirani & Taylor (2023), ISLP, Springer | Five authors; Springer Texts in Statistics, 2023 | doi.org/10.1007/978-3-031-38747-0 | **Error in our reference list: Taylor missing** |
| Müller & Guido (2016), O'Reilly | First edition, 25 Sep 2016 | O'Reilly page returns 403 to scripts; ISBN record checked | OK |
| Breiman (2001) | *Machine Learning* 45(1), 5–32 | doi.org/10.1023/A:1010933404324 | OK (issue 1 can be added) |
| Wolpert (1992) | *Neural Networks* 5(2), 241–259 | doi.org/10.1016/S0893-6080(05)80023-1 | OK |
| Chen & Guestrin (2016) | Proc. 22nd ACM SIGKDD, 785–794 | doi.org/10.1145/2939672.2939785 | OK |
| He & Garcia (2009) | *IEEE TKDE* 21(9), 1263–1284 | doi.org/10.1109/TKDE.2008.239 | OK |
| Cui, Lu, Sun & Golden (2024) | *MSOM* 26(1), 233–251 | doi.org/10.1287/msom.2021.0174 | OK |
| Deshpande & Pendem (2023) | *MSOM* 25(3), 827–845 | doi.org/10.1287/msom.2021.1045 | OK |
| Kapoor & Narayanan (2023) | *Patterns* 4(9), 100804 | doi.org/10.1016/j.patter.2023.100804 | OK |
| van den Goorbergh, van Smeden, Timmerman & Van Calster (2022) | *JAMIA* 29(9), 1525–1534 | doi.org/10.1093/jamia/ocac093 | **Reference list says "et al.": give all four authors** |
| Grinsztajn, Oyallon & Varoquaux (2022) | NeurIPS 35, Datasets and Benchmarks Track | proceedings PDF returns 200 | **Error in our reference list: page range 507–520 is not on the proceedings page; remove it** |

Correction to this table: the three reference-list errors and the missing initials were already fixed on
2026-10-28 (commit 7f1bad0); this audit first read an older copy. The current reference list matches the publisher
records; only Breiman's issue number (45(1)) was added. Kandula et al. (2021) is not cited.

## 2. Claims

| Where | Claim | Supported by the audited summary? | Fix |
| --- | --- | --- | --- |
| 01 §1, "Why MAE and AP" | AP is judged against the detractor share, "which is what a random ranking would achieve (He and Garcia, 2009)" | **No.** The summary supports "accuracy can conceal weak minority detection" and "evaluation must reflect prevalence"; the random-ranking baseline of AP is not in it | Cite He and Garcia for the accuracy point; state the AP baseline as a property of the metric, uncited |
| 02 §2.1, 05 §5.2, 09 §9 | Deshpande and Pendem study "the link between logistics and the ratings customers give"; "slower logistics goes with worse ratings is a literature-supported hypothesis" | **No.** Only title, venue and context were checked; the summary says the study relates logistics performance *and* ratings to purchasing and sales, and that detailed results, including the direction of effects, are not verified. Which ratings it means is not established | Cite only for the question it studies ("how logistics performance and ratings relate to purchasing and sales"); drop "literature-supported hypothesis" in §9 and label the slow-seller point an observation from our data |
| 02 §2.2, 06 §6.2 | "start from a trivial baseline … add complexity only when it improves held-out performance" and "each started from its simplest form (James et al., 2023)" | **Partly.** Müller and Guido: build simple baselines, keep train and test apart, fit preprocessing in pipelines. ISLP: flexibility trades bias against variance, resampling estimates generalisation. Neither summary says "simplest form first"; that rule is the course brief's | Attribute baselines to Müller and Guido, resampling and the bias–variance trade-off to ISLP; cite the simplest-first rule to the project description or state it as our rule |
| 06 §6.1 | A random or stratified split would train on later orders and put one customer on both sides "(Kapoor and Narayanan, 2023)" | **Partly.** Verified: leakage takes several forms beyond train–test overlap, and inflates results. Temporal and group separation is the audit's *application (inference)*, not a stated finding | "Leakage takes several forms beyond row overlap (Kapoor and Narayanan, 2023); for dated orders with returning customers, we apply this as …" |
| 06 §6.3 | Imbalance corrections can distort calibration "(Van den Goorbergh et al., 2022; He and Garcia, 2009)" | **Partly.** Supported by Van den Goorbergh et al. only (logistic risk models); He and Garcia is a survey that lists resampling as an option | Drop He and Garcia from that sentence |
| 02 §2.2 | Gradient-boosted trees are "a scalable alternative for tabular data" (Chen and Guestrin, 2016) | Mostly. The paper is a scalable boosting system; "for tabular data" is the audit's inference | "a scalable gradient tree boosting system" |

Supported as written: Cui et al. (promise, not actual speed; sales and profit up, returns up, retention down), Breiman
(strength and correlation of trees), Grinsztajn et al. (tree ensembles strong on the medium-sized tabular datasets
studied), Wolpert (second-stage learner on held-out predictions), Kapoor and Narayanan (taxonomy; leakage inflating
results across many studies), He and Garcia (accuracy can hide weak minority detection; resampling and cost-sensitive
learning are options), Van den Goorbergh et al. (scope stated as logistic risk models), Müller and Guido with Kapoor
and Narayanan for fold-local preprocessing (03 §3).

## 3. Outside the 12 sources

- Pipeline A's stored outputs cite sources that are not among the 12: the task contract (Willmott and Matsuura 2005,
  Saito and Rehmsmeier 2015, Brier 1950, Elkan 2001, Breiman et al. 1984, Hastie et al. 2009, Friedman et al. 2010) and
  the feature dictionary (Leite et al. 2024). None may be carried into a report.
- The one-standard-error rule and the VIF are stated as the project's own rules, uncited (ISLP not cited for them).

## 4. Status

Section 2 fixes applied to the report sources on 2026-10-29 (see records/CHANGES.md) and to the review doc; the
literature register's claim rows were updated to match.
