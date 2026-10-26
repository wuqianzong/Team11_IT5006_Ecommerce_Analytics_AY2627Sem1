## 6 Model deployment and application

**Release package.** The two frozen models of each task (B, and A as fallback) are packaged with their schemas, training profiles and checksums. Reloaded from disk, they re-predict the saved test predictions exactly (largest difference {{B10.reg.parity_max}} for regression, {{B10.clf.parity_max}} for classification), from test rows rebuilt with every label column emptied.

**Serving rule.** A router sends each order to B when the customer and seller are both in the seven states and the distance is known, otherwise to A ({{B10.clf.test_rows_inside}} and {{B10.clf.test_rows_outside}} classification test orders respectively). B's alert uses the operating threshold 4/15; A's fallback uses its frozen 1/6. Orders inside B's scope that are not yet handed over get no score.

**Input checks.** Unknown states, impossible distances, orders without items and missing instalments are rejected with a clear message; missing values (imputed) and unseen categories are accepted with a warning, and so is any numeric input more than 4 standard deviations from the training mean.

**Application.** A Streamlit app with three tabs: the business dashboard from Phase 1, delivery lead time and detractor risk. The model tabs read only stored outputs and score held-out historical orders, as the brief allows.

Placeholder: the live URL, usage instructions and screenshots will be added once the app is deployed.
