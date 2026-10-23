# Pipeline B decision log

Decisions that apply to Pipeline B only. Newest first. The decision that created B is G-79 in
`../../spec/blueprints/decision_log.md`; the change list is CR-054 (doc tab "CR-054 change
request"). Status: Proposed · Agreed · Superseded.

| ID | Date | Stage | Decision | Raised by | Basis | Status |
| --- | --- | --- | --- | --- | --- | --- |
| B-G-01 | 2026-10-23 | B5, B8 | Fold 1 below A's 10,000-training-row minimum: keep A's five folds unchanged and accept the shortfall as a recorded deviation, so A and B are compared on identical periods and G-79's 5-fold mean is unchanged. Safeguard: B5 stops if fold 1 has fewer than 5,000 training rows or (classification) fewer than 300 training detractors; the 100-detractor minimum stays a hard check. B8 also shows the adoption comparison on folds 2-5, as description only. Not chosen: dropping fold 1, merging folds 1-2 for B | Experiment lead (Wu Qianzong) | protocol cv.minimums (G-53, G-74); G-75 precedent; G-79 | Agreed |
