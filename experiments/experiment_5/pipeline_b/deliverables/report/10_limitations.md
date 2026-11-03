## 10 Limitations

Table K17 lists every remaining limit and how it is handled; these matter most for reading the results:

- **Scope and moment.** Pipeline B covers only orders whose customer and seller are in the seven states with a known distance; Pipeline A's frozen model serves every other order. Pipeline B's alert acts at handover and Pipeline A's at checkout, so part of the alert gain is the later moment.
- **Post-test threshold.** The operating threshold 4/15 was chosen after the test was read; the frozen 1/6 result is reported as the unbiased one.
- **Drift and late deliveries possibly missing.** The test period was faster and happier than development, and the slowest deliveries for the newest orders may not have arrived when the data was extracted, so the test error may look better than it will in operation.
- **Optimistic validation, unstable alert features.** Features were ranked once on all development orders, so validation scores are slightly optimistic (the test is unaffected); the alert's feature ranks move between folds; and correlation among the new history features was not measured.
- **Recorded deviations.** Sigmoid calibration was kept although the pre-set rule preferred raw probabilities; Pipeline B's fold 1 is below the training minimum; the forest's best configuration sits on its grid edge (section 6).
- **Associations, not causes.** No feature's effect on the outcome was tested; recommendations are labelled by evidence type (section 9).

- **Business case.** Section 9's comparisons were computed after the test, its scenarios are associations, the buffer rule was set on one window, and with no handover feed or action log the effect of a contact is unmeasured.

**Next steps.** Run a randomised hold-back pilot (contact a random half of alerted customers and compare reviews and repeat orders), log every action on an alert, backtest the buffer rule on rolling months before resetting it monthly, and monitor alert precision and late deliveries by state.
