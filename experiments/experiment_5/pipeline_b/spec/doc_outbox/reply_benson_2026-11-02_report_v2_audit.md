# Reply to Benson: audit of final report v2 (2026-11-02)

Hi Benson, thank you for the audit. Each point is checked against the evidence and logged in
`deliverables/audit/findings.yaml` (T-12 to T-25). Henry's decisions are B-G-17 and the fixes are B-CR-47.
Triage table: `deliverables/audit/runs/2026-11-02_benson_report_v2_audit.md`.

Done on our side: because the content changed, the report and deck are now **v2.1** (review doc rev 45, deck v2.1
version 41). The committed audit inputs are refreshed to those copies, and the deliverables audit passes 9/9 on
them. The Word copy is `deliverables/exports/2026-11-02/Team11_final_report_v2.1.docx`. One audit-tool change:
the number check now skips the doc's three header lines (title, date, review note), as the text check already did,
because the v2.1 title has a number in it.

## For you to do

1. **§8, hosted app (2.1, T-12).** You were right. §8 now says the hosted app runs the same frozen bundles, and that a
   small prediction API returning the same predictions "is provided for hosting at [API URL to be added]". Please put
   the URL in `deliverables/report/08_deployment.md` once the API has one, then in the review doc (corrected later
   on 2 Nov: a change typed into the doc alone fails the audit; see the v2.1 recheck reply, T-31). If you also set `MODEL_API_URL` on Streamlit Cloud, change
   "runs the same frozen bundles" to say the app calls the API.
2. **Reproduction appendix (T-21).** This is yours, because it means reconciling `main`, and our branch cannot do
   that. Results may not match exactly from one machine to another. Someone has to judge each difference and decide
   whether it affects the final report, the deck or the schedule. Henry suggests reviewing the reproduction result and
   measuring its impact on the report and deck. If our story still holds, we keep the small differences and say so.

## Point 2.2: where the two validation AP values came from, and how to stop it happening again

- **Cause.** The B8 adoption comparison (G-79) was set up at the gate on raw, uncalibrated scores. It writes
  `stages/b08/classification/outputs/population_summary.csv` (raw AP 0.244 / 0.242 / 0.262). B-G-05 came later and
  chose sigmoid. It added sigmoid rows to `metrics_by_population.csv` (column `variant`), but nobody re-pointed the
  register rows `B8.clf.pop_*`, so they kept reading the raw file. B9 and the frozen recipes use sigmoid (0.248,
  0.232). A comment in `e5b/adoption.py` (lines 5–6) says calibration cannot change AP. That holds for one monotone
  rescaling of a single model's scores. Our sigmoid step refits models on time-ordered inner splits and averages them,
  so the ranking and the AP do change. That frozen comment is left as it is and recorded in WORKLOG and B-CR-47.
- **Fix.** `B8.clf.pop_*` now read the sigmoid rows: 0.232 / 0.230 / 0.248, which equal `B9.clf.val_ap_*`. This
  changes §7.3, Table K15 and deck slide 12. The adoption gains (§6.5, Table K13, `B8.clf.adopt_gain_*`) stay raw,
  because that is how the rule decided. The text now says "before calibration". On sigmoid, B still wins every fold
  (+0.011 to +0.025). A comment above the rows in `registry_B.yaml` explains the split.
- **For your agent to note or add, so this does not come back:**
  1. When a decision changes a metric's definition (here: raw to sigmoid), list every register item that reads the old
     definition and re-point each one in the same change.
  2. In the register, any select on a file that has a `variant` column must name the variant. A check in
     `build_evidence_B.py` or the audit could refuse a select that doesn't. (Proposed, not built.)
  3. Any "validation AP" in the report must use the same scale as Table 4, unless the text says otherwise.

## The other points

| Point | What changed |
| --- | --- |
| 2.3 Executive summary | "On the validation folds, most of the lead-time gain comes from the narrower scope …" |
| 2.4 Appendix L caption | `S.06_ml_deployment_alert_list` |
| Seeds | §6.1: seed 42 for every random step (recorded in all 36 stage manifests); forests predict on one thread (CR-051) |
| Data model | Appendix G is now "Data model and population chain". New Table G1 gives each of the nine tables' grain, key, join and use. §3 points to it. The exclusion tables are now G2 and G3 |
| Dashboard tab sources | §8 points to `deliverables/dashboard/app/DATA_AND_MODEL_SOURCES.md` |
| Duplicate indicators | Your two-column list (`total_weight_g; product_photos_qty`) is Pipeline A's s04. Pipeline B's b04 drops one indicator per task: weight for the alert, volume for lead time. §5.2 now says so |
| Appendices B, G, H | Cited in §6.1, §3 and §6.2 |
| §8 local run | "`streamlit run app.py`, from that folder or from the repository root" |
| Figure 4 | The register caption of `F.A3.reg.outcome_trends`, which feeds the alt text, and the doc's alt text both now say "orders and lead time". This mismatch has come up more than once, so captions and alt text should come from one field |

## Waived from the audit (Henry's decision)

- **The PDF file name** (`Team11_Phase3_IT5006_AY2627Sem1.pdf`) and **the Word page count** are taken out of the
  audit. We export only .docx and .pptx. The PDF is the final submission copy, so team members name it and check its
  page count once the report is final. Both are logged as `Waived` (T-24, T-25).

## Still open on our side

- None. The deck copy is `deliverables/exports/2026-11-02/Team11_final_deck_v2.1.pptx`.
