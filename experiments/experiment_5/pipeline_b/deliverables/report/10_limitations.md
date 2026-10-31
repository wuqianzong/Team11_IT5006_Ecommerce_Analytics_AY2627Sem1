## 10 Limitations

All limitations are collected here. All validation in this project uses time-ordered, customer-purged folds, and the test period was read once; the limits below are what remains.

*Table 22. Limitations and how each is handled.*

| Limit | What it means | How it is handled |
| --- | --- | --- |
| Seven-state scope | Pipeline B covers only orders whose customer and seller are in the seven states with a known distance | Pipeline A's frozen model serves every other order, and each prediction shows which model made it |
| Different prediction moments | Pipeline B's alert acts at handover, Pipeline A's at checkout, so part of the gain is the later moment | Stated wherever the two are compared (section 7) |
| Post-test threshold | The operating threshold 4/15 was chosen after the test was read | The frozen 1/6 result is reported as the unbiased one |
| Calibration override | The pre-set rule would have kept raw probabilities; sigmoid calibration was kept so both pipelines share one scale | Recorded as a deviation (section 6.4) |
| Screening on pooled rows | Features were ranked once on all development orders, so validation scores are slightly optimistic | Ranking stability by fold is reported (section 5.3); the test is unaffected |
| Unstable alert ranking | For the alert, feature ranks move a lot between folds, most in the early folds | The selected set is read as a reasonable choice, not a unique one |
| Unmeasured correlation | Correlation and VIF were not computed for the new history features; full rank rules out only exact dependence | Coefficients of related history features are read with care |
| Grid edge | The forest's best configuration sits on the edge of its grid | The grid was fixed in advance and not extended after the test; the plain model is kept by the selection rule |
| Fold 1 below minimum | Pipeline B's first fold has fewer training orders than the pre-set minimum | Kept so both pipelines are compared on identical periods |
| Drift | The test period was faster and happier than development, and the route history features shifted most | Validation and test are reported separately; the promise buffer should be set on recent weeks |
| Latest deliveries possibly missing | The slowest deliveries for the newest orders may not have arrived when the data was extracted | The test error may look slightly better than it will in operation |
| Reproducibility | The frozen models' predictions reproduce exactly on another machine; refitting gives slightly different numbers across machines | Reproduction compares predictions exactly and refitted scores within a tolerance |
| Associations, not causes | Features describe association with the outcome, not the effect of acting on them | Recommendations are labelled by evidence type (section 9) |

**Next steps.** Deploy the app; monitor alert precision and late deliveries by state each month; set the promise buffer on recent weeks; and test the handover alert with customer service before scaling it.
