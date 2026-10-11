# Milestone 2 report and matched two-cycle evidence

The shared Word report and repository Word copy are maintained with tracked changes. The current story is one pipeline containing two modelling cycles, supported by [Experiment 4](../../experiments/experiment_4/README.md). Current final results and the full comparison catalogue appear in Appendix H. Older appendices retain explicitly historical supporting results.

The selected regression model is the transformed 11-feature forest with minimum leaf 50 and no clipping. Classification uses 12-feature regularized Logistic Regression. Its development-selected threshold has higher terminal illustrative loss than no alerts; the report records this negative result and does not recommend deployment.

The report Markdown and existing PDF remain historical versions while human revision is pending. Do not regenerate the tracked Word report from them. Condensation, Markdown synchronization and submission PDF generation remain deferred.

Current evidence: `artifacts/metrics/experiment-4/run-01/`. Active scorer: `src.models.experiment4_score`. Active configuration: `src/models/configs/active_pipeline.json`. Preserve archived v4 receipts.
