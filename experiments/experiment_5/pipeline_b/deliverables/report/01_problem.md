## 1 Problem definition and stakeholders

We frame one delivery-experience problem as two tasks (the brief's dual framing).

| | Regression: delivery lead time | Classification: detractor alert |
| --- | --- | --- |
| Question | How many days from purchase to delivery? | Will the customer leave a 1–2 star review? |
| Target | Lead time in days (log scale in the model) | Detractor = lowest valid review score of the order is 1 or 2 |
| Prediction moment | At checkout (A and B) | A: at checkout; B: at carrier handover |
| Stakeholder and action | Fulfilment and customer service set the delivery promise shown to the customer | Customer service contacts at-risk customers before the review is written |
| Primary metric | MAE (days); also RMSE, R², share within 3 days | Average precision (PR-AUC); also ROC-AUC, Brier, precision and recall at the threshold |
| Error cost | Late promises hurt trust more than early ones; reported as residual buffers | Illustrative cost 5 per missed detractor, 1 per false alert |

**Why handover for classification.** Late delivery is the strongest driver of bad reviews and is unknown at checkout. At handover the seller's dispatch delay is known and there is still time to act. Customer service has no reason to act at checkout. B's alert therefore cannot fire before handover; orders not yet handed over get no score, and a separate rule flags orders whose shipping limit passes without a handover.

**Success criteria (fixed before the test).** A more complex model is kept only if it beats the simpler one by more than one standard error over the validation folds (one-SE rule). B is adopted for a task when its mean validation score beats A's frozen model on the same rows; both are then scored once on the test.
