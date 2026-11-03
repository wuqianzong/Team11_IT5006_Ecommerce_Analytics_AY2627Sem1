## 8 Deployment and dashboard

The released models predict exactly what was tested, and the dashboard shows only stored results, each labelled with the model that produced it.

**Release package.** For each task, Pipeline B's frozen model and Pipeline A's (as fallback) are packaged with their feature schemas, training profiles and checksums. Reloaded from disk, they re-predict the saved test predictions exactly (largest difference {{B10.reg.parity_max}} for lead time and {{B10.clf.parity_max}} for the alert), from test rows rebuilt with every label column emptied, so no label is read.

**Serving rule.** A router sends each order to Pipeline B when its customer and seller are both in the seven states and its distance is known, and to Pipeline A otherwise ({{B10.clf.test_rows_inside}} and {{B10.clf.test_rows_outside}} of the alert's test orders). Every prediction carries a badge naming the model and, outside the seven states, the reason. Inside the seven states, an order not yet handed over gets no alert score; the missed-dispatch rule flags it if its shipping limit passes.

**Dashboard.** A Streamlit app with four tabs: a business overview of all orders (descriptive, labelled as a separate scope from the model results), delivery lead time, detractor risk at handover, and ML deployment, which scores the alerted held-out orders. The model tabs read only stored outputs and score held-out historical orders. The alert tab's threshold slider moves Pipeline B's threshold over the stored options (default 4/15) and shows alerts per day, precision, recall and cost; the baseline's fallback stays at its frozen 1/6.

**Using the app.** The app lives in `deliverables/dashboard/app/` with its own pinned environment; `streamlit run app.py`, from that folder or from the repository root, opens it locally (its README gives the commands). The hosted app at https://it5006grp11ecommerce.streamlit.app/ runs the same frozen bundles. Appendix L describes each tab, the files it reads, the input checks and the app's tests.
