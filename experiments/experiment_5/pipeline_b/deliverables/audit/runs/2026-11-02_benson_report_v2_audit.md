# Benson's audit of final report v2, 2026-11-02, and its triage

Audited: `Team11_Milestone3__final_report_v2.docx` against the repository at `main` (`b01bd4a`).
Consistent: all 31 charts byte-identical to register figures or dashboard screenshots; 12 headline results recomputed
from T1's saved predictions within 1e-9; every number in a fresh fill except 16 three-decimal roundings checked against
B6-B8 evidence; decisions match the records; course requirements present.

Triage: Henry's decisions of 2026-11-02 (B-G-17); fixes in B-CR-47. Findings register rows T-12 to T-25.

| Audit point | Finding | Verdict | Action | Register |
| --- | --- | --- | --- | --- |
| 2.1 | §8 says the hosted app is served by the prediction API; the hosted sidebar reads "local frozen bundles" (`MODEL_API_URL` not set) | Correct | §8 reworded: the hosted app runs the same frozen bundles; the API is provided for hosting at "[API URL to be added]", for Benson to fill once the API has its URL | T-12 |
| 2.2 | Two validation AP values per pipeline: B9 sigmoid (0.248, 0.232) vs B8 population summary raw (0.262 / 0.244 / 0.242) | Correct | `B8.clf.pop_*` re-pointed to the sigmoid rows of b08 `metrics_by_population.csv` (0.232 / 0.230 / 0.248), report §7.3, Table K15 and deck slide 12; the adoption gains (§6.5, Table K13) stay raw and say so, because the adoption rule (G-79) was applied to raw scores | T-13 |
| 2.3 | Executive summary's scope-vs-features split sits beside test results but is measured on validation rows | Correct | "On the validation folds, ..." | T-14 |
| 2.4 | Appendix L caption cites `S.06_score_alert_list` | Correct | `S.06_ml_deployment_alert_list` | T-15 |
| 3 | Random seeds not in the report | Correct | §6.1: seed 42 for every random step, single-threaded forest prediction (CR-051) | T-16 |
| 3 | Data model only in prose | Correct | Appendix G becomes "Data model and population chain" with Table G1 (grain, key, join, use of each raw table); §3 points to it; exclusion tables become G2 and G3 | T-17 |
| 3 | What each dashboard tab reads not in §8 | Correct | §8 points to `deliverables/dashboard/app/DATA_AND_MODEL_SOURCES.md` | T-18 |
| 3 | Duplicate missing-value indicators not mentioned | Partly: the two-column list is Pipeline A's s04; Pipeline B drops one per task (weight for the alert, volume for lead time; b04 `design_matrix_B.csv`) | §5.2 names B's dropped indicator | T-19 |
| 3 | Appendices B, G, H uncited | Correct | Cited in §6.1 (B), §3 (G), §6.2 (H) | T-20 |
| 3 | Reproduction appendix | Handed back | Benson owns `main` and its reconciliation; a cross-machine rerun may differ, and a person judges the differences and their impact on the report, deck and schedule | T-21 |
| 4 | §8 local-run sentence predates the root launcher (e53fca1) | Correct | "from that folder or from the repository root" | T-22 |
| 4 | Figure 4 caption "orders and lead time" vs alt text "orders and outcomes" (recurring) | Correct | Register caption of `F.A3.reg.outcome_trends` (the alt-text source) and the doc's alt text now say "orders and lead time" | T-23 |
| 5 | Course file name `Team11_Phase3_IT5006_AY2627Sem1.pdf` | Waived from the audit (Henry) | Team members name the PDF after the report is final; our side exports .docx and .pptx only | T-24 |
| 5 | Page count in Word | Waived from the audit (Henry) | Not remeasured; checked by the team on the final PDF | T-25 |

Recheck (after B-CR-47): deliverables audit 9/9 on review doc rev 43 and deck v2 version 40 (live copies), and again
on the refreshed committed inputs after the rename to v2.1 (doc rev 45, deck version 41).
