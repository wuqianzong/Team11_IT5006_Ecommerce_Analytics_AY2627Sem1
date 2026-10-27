# Response to the third-party audit V2 (2026-10-26, HEAD b6a24f1)

Every finding was checked against the repository before any change (read-only); all 15 are valid. Henry approved
fixing the documentation and disclosure items (B-CR-30). Data, models, stage outputs and the pipeline code were not
changed. The audit's register count (17 tables) was stale: the register has 57 numbers, 24 tables and 16 figures
after the appendices (B-CR-28), and 58 numbers after B-CR-30.

| ID | Finding | Verified | Action (B-CR-30) | Status |
| --- | --- | --- | --- | --- |
| B11-F1 | Report §3 open item: A's s03 EDA numbers | Yes | B-G-11 (Henry, 2026-10-27; Benson to ratify), B-CR-33: the register reads A's s03 outputs at e5-A-frozen (sha256 against the tag); §3 cites 11 A3 numbers, open-item line removed | Fixed (pending ratification) |
| B11-F2 | App URL and screenshots are placeholders | Yes | None: needs migration (lead only, README §12) | Open |
| B11-F3 | No final PDF / PPTX exports | Yes | None: scheduled 3–7 Nov (B11 §8) | Open (planned) |
| B11-F4 | B11 not accepted; README says NOT STARTED | Yes | README row now "DRAFTS BUILT, under review"; acceptance/tag still pending | Partly fixed |
| B10-F1 / B11-F6 | Combined 20.5/day vs the 6/day review cap not stated | Yes (cap absent from report and deck) | Report §7 item 2 and §8 "Alert capacity"; deck alerts slide footer and notes: the cap applies to B only; combined is higher; team accepted | Fixed |
| B10-F2 | A fallback test cost NaN | Yes | B-G-10 (Henry, 2026-10-27; Benson to ratify), B-CR-32: B10 round 3 computes A's fallback TP/FP/FN and costs from T1's saved predictions and a combined serving-rule line; report §7 and deck slide 8 cite them | Fixed (pending ratification) |
| B11-F5 | B-G-05 calibration override not in limitations | Yes | Report §8 "Calibration override"; deck limitations row | Fixed |
| B11-F7 | References abbreviated | Yes | None: full metadata must be looked up from the publisher records | Open |
| B11-F8 | B11 blueprint frozen input tag is round 1 | Yes | Now `e5-B-s10-accepted-r2`; outbox copy regenerated | Fixed |
| B11-F9 | Deliverables README lists appendices as open | Yes | Updated (appendices A–F done) | Fixed |
| B10-F4 | serving_config note says "to re-confirm" | Yes | Not rerun (stage output); correction recorded in the decision log (B-G-07 note) | Recorded |
| M-01 | Fold-1 deviation | Already disclosed | None | Closed |
| M-02 | Tree design matrix not full rank | Yes (tree condition number about 7.8e16) | Appendix C sentence: rank matters for the selected linear/logistic models, not trees | Fixed |
| M-03 | T1 dirty / no rerun | By design | Already in §8 Reproducibility | Closed |
| (extra) | Report §7 item 4 and deck notes labelled the route and recent-speed features as literature-supported | Found during verification | Split: seller dispatch literature-supported; route and recent speed an unmeasured mechanism (Report notes §6) | Fixed |

After the fixes the deliverables audit was rerun on the live report (rev 28) and deck (version 1793007227-4f95):
9/9 PASS (`audit_result.json`).
