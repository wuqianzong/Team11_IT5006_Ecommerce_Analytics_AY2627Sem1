## 8 Deployment and dashboard

The released models predict exactly what was tested, and the dashboard shows only stored results, each labelled with
the model that produced it.

**Release package.** For each task, the improved pipeline's frozen model and the baseline's (as fallback) are
packaged with their feature schemas, training profiles and checksums. Reloaded from disk, they re-predict the saved
test predictions exactly (largest difference {{B10.reg.parity_max}} for lead time and {{B10.clf.parity_max}} for the
alert), from test rows rebuilt with every label column emptied, so no label is read.

**Serving rule.** A router sends each order to the improved pipeline when its customer and seller are both in the
seven states and its distance is known, and to the baseline otherwise ({{B10.clf.test_rows_inside}} and
{{B10.clf.test_rows_outside}} of the alert's test orders). Every prediction carries a badge naming the model and,
outside the seven states, the reason. Inside the seven states, an order not yet handed over gets no alert score; the
missed-dispatch rule flags it if its shipping limit passes.

**Input checks.** Unknown states, impossible distances, orders without items and missing instalments are rejected
with a clear message. Missing values, unseen categories and numeric inputs more than 4 standard deviations from the
training mean are accepted with a warning.

**Dashboard.** A Streamlit app with three tabs: a business overview of all orders (descriptive, labelled as a
separate scope from the model results), delivery lead time and detractor risk at handover. The model tabs read only
stored outputs and score held-out historical orders. The alert tab's threshold slider moves the improved pipeline's
threshold over the stored options (default 4/15) and shows alerts per day, precision, recall and cost; the baseline's
fallback stays at its frozen 1/6.

Placeholder: live URL, usage instructions and screenshots, added once the app is deployed.
