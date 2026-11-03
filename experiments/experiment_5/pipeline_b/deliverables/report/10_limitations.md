## 10 Limitations

Table K17 lists every remaining limit and how it is handled; these matter most for reading the results:

- **Scope and moment.** Pipeline B covers only orders whose customer and seller are in the seven states with a known distance; Pipeline A's frozen model serves every other order. Pipeline B's alert acts at handover and Pipeline A's at checkout, so part of the alert gain is the later moment.
- **Post-test threshold.** The operating threshold 4/15 was chosen after the test was read; the frozen 1/6 result is reported as the unbiased one.
- **Drift and late deliveries possibly missing.** The test period was faster and happier than development, and the slowest deliveries for the newest orders may not have arrived when the data was extracted, so the test error may look better than it will in operation.
- **Optimistic validation, unstable alert features.** Features were ranked once on all development orders, so validation scores are slightly optimistic (the test is unaffected); the alert's feature ranks move between folds; and correlation among the new history features was not measured.
- **Recorded deviations.** Sigmoid calibration was kept although the pre-set rule preferred raw probabilities; Pipeline B's fold 1 is below the training minimum; the forest's best configuration sits on its grid edge (section 6).
- **Associations, not causes.** No feature's effect on the outcome was tested; recommendations are labelled by evidence type (section 9).

- **Business case.** The promise comparison, the transit scenario and the freight scenario in section 9 were computed after the test was read; the transit and freight results are scenarios and associations, not effects of an action, and the value of a kept promise or a recovered customer is not known.
- **Missing operational data.** The models need a live feed of carrier handovers to alert in time, and nothing records what customer service did with an alert, so the effect of a contact cannot be measured yet.

**Next steps.** Run a randomised hold-back pilot: contact a random half of the alerted customers and compare their reviews and repeat orders with the other half, which measures the effect of a contact and the break-even. Connect the handover feed and log every action taken on an alert. Reset the promise buffer each month on recent weeks against Olist's late share, and monitor alert precision and late deliveries by state.
