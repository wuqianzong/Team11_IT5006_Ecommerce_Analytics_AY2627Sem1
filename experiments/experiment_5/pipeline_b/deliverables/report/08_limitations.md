## 8 Limitations and next steps

- **Scope.** B covers only orders whose customer and seller are in the seven states; other orders get A's baseline model.
- **Different prediction moments.** B's classifier acts at handover and A's at checkout, so part of B's gain is the later moment.
- **Post-test threshold.** 4/15 was chosen after reading the test; the frozen 1/6 result is the unbiased one.
- **Alert capacity.** The {{B10.clf.review_cap}} alerts a day asked for at the B9 review applies to B only; with A's fallback at 1/6 the combined volume is higher (section 7), which the team accepted.
- **Calibration override.** The pre-set calibration rule kept raw probabilities for B's classifier; the team chose sigmoid calibration instead (decision B-G-05) so that A and B share one probability scale at the test. This is a recorded deviation from the rule.
- **Drift.** The test period is faster and happier than development; scores may move as the business changes.
- **Fold 1** has fewer training rows than the pre-set minimum for B; it was kept so A and B are compared on the same periods.
- **Reproducibility.** Predictions of the frozen models reproduce exactly on another machine; refitting the unregularised logistic model gives slightly different numbers across machines, so the reproduction check compares predictions, and refitted results within a tolerance.
- **No causal claims.** Features describe association, not the effect of an intervention.

Next steps: deploy the app, monitor alert precision and late deliveries by state each month, and test the promise buffer and the handover alert with customer service.
