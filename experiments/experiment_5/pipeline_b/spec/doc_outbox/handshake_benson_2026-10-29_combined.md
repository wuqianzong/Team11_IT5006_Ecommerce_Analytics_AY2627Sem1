# Handshake prompt for Benson: deck v2 and the Pipeline A report (2026-10-29, combined)

Paste this into Benson's Claude session on `milestone-3` after `git fetch origin` and reading
`origin/e5/deliverables-henry`. It replaces `handshake_benson_deck_v2.md` and `m2_rework_handshake.md` (neither was
sent): both asked for a "B-G-14" with overlapping scope, so they are merged into one decision here.

---

Henry has two documents waiting on you, the experiment lead: the final deck v2
(https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc; its sources replace `pipeline_b/deliverables/deck/`, which the
audit reads; v1 stays at https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23 with sources frozen in
`pipeline_b/deliverables/deck_v1/`) and a reworked Phase 2 technical report built only on Pipeline A, which Henry
will send to the instructor himself. Both read stored outputs only: no stage rerun, no refit, no change to `stages/`,
the tags or the release record; every number comes through the register as a `{{id}}` placeholder.

For each decision: agree, change or refuse, and record what you decide in `spec/decision_log_B.md` and
`spec/human_decisions_B.yaml`.

## D1. Read Pipeline A's s01 and s04–s08 outputs (proposed B-G-14)

B-G-11 (s03) and B-G-13 (s02) let B's register read A's files at tag `e5-A-frozen`, sha256 checked by
`build_evidence_B.verify_a_source`, A's evidence ID carried. Extend the same rule, with the same conditions, to A's
s01 and s04–s08 outputs: task contract, feature pool, transforms, reductions, selection ranking, folds, training
ladder and paired differences, learning curves, tuning grids and validation curves, finalists, calibration and
threshold table.

Used first by the deck, where slides 7 and 8 carry "pending" slots:

| Slide | A file (under `stages/`) |
| --- | --- |
| 7 | `s04_features/regression/outputs/figures/selection_cumulative.png`, `s04_features/classification/outputs/figures/selection_cumulative.png` |
| 8 | `s06_training/regression/outputs/figures/family_ladder.png`, `s06_training/classification/outputs/figures/family_ladder.png` |
| 8 (optional) | `s08_selection/regression/outputs/figures/finalists.png`, `s08_selection/classification/outputs/figures/finalists.png` |

The Pipeline A report needs the rest of the list.

## D2. `figure_map.json` deck section for v2

Replace the deck section with the v2 asset map (v2 asset → register figure). `chart_ok` already checks A sources
against `e5-A-frozen` (B-CR-40). Then run the audit against the v2 deck.

```
599ab1acabc2699da29fdc0ffc40a0fe F.A2.data_structure
617e556f7ca00f5865ddcc3d68cef704 F.A3.reg.target_kde
983e32ca72a793c5d24b51528b2c2082 F.A3.clf.target_bar
6bcb1233fa3679606ae16b9ef0ccdd6d F.A3.reg.cumulative_importance
c6a5ce7bcb7b95879aabd101aad62ce9 F.A3.clf.cumulative_importance
8b7e8ad18ab84791e80a1aae513cb35f F.A3.reg.correlation_heatmap
7e345f291b0060d62a700120becf0e1e F.reg.partition
bd1e15a8298a7554b452a240243a88b1 F.A3.clf.screen_promise
1dfd37b6757a1a164bf32cc80f5cfcf2 F.reg.lateness_by_route
37dacf6a99511be9977f23e6ddc7d858 F.A3.clf.screen_region
f89eeaed0b14d65a8f74f1b2bf131063 F.reg.selection
4d42161e111b55bfc22e44fe223f6b57 F.clf.selection
aa6cd5caccd3fe6ac92b480d32d0a4af F.reg.history_coverage
15770975c1fcfe638738965785f128c4 F.reg.population
17485adb61fa036fd3025b33fa621e5e F.clf.confusion
2115d248dad9982981df2fa7b285a8ef F.reg.residuals
26f9c651ce7ea4e5efb4bb0af3d32962 F.reg.by_state
c0167aa70f2b3c125c93c281284b33ee F.clf.test_curves
3c4521d33750d6d01c73aea996074711 F.clf.threshold_options
0b1999c18bfdd5e4c2809437c9e0bb90 F.reg.buffer_curve
```

## D3. Presentation renders of the deck charts, with larger fonts

In presentation mode the text inside several charts cannot be read. Review round 3 (2026-10-29) put every slide on one
type scale (body, tables and chart labels 28 px) and gave each chart the largest box left, so the remaining fix is in
the figures. Request: a presentation render of each chart below, drawn only from the data file saved beside the
existing PNG, with no stage rerun, no refit and no new numbers. The existing PNGs and the report stay as they are; the
renders are new register items beside the originals (for example `F.A3.clf.screen_region.deck`), with the same
evidence ID and a source check that the data file equals the one at its tag (`e5-A-frozen` for A, the B release
record for B). Target: fonts at least 18 pt at the slide box size; figure sized to its box (slide pixels below,
export at 2x).

| Slide | Register figure | Data file next to the source PNG | Slide box (px) | Main problem |
| --- | --- | --- | --- | --- |
| 6 | `F.A3.reg.cumulative_importance`, `F.A3.clf.cumulative_importance` | `A/s03_eda/*/.../cumulative_importance.csv` | 836 x 470 each | 24 rotated tick labels, small legend |
| 7 | `F.A3.reg.correlation_heatmap` | `A/s03_eda/regression/.../numeric_correlation_heatmap.csv` | 820 x 700 | 20 x 20 labels and cell values |
| 9 | `F.A3.clf.screen_promise` | `A/s03_eda/classification/.../candidate_screen_promise.csv` | 560 x 260 | chart drawn small inside a large canvas |
| 9 | `F.reg.lateness_by_route` | `doc_support/regression/.../b2_lateness_by_route.csv` | 1112 x 260 | route labels |
| 9 | `F.A3.clf.screen_region` | `A/s03_eda/classification/.../candidate_screen_region.csv` | 1112 x 250 | three small panels; region-pair labels |
| 10 | `F.reg.selection`, `F.clf.selection` | `doc_support/*/.../b4_selection.csv` | 836 x 330 each | 25+ rotated feature names |
| 12 | `F.reg.population`, `F.clf.confusion` | `doc_support/*/.../r05_population.csv`, `r06_confusion.csv` | 836 x 480 each | legend, cell values |
| 13 | `F.reg.residuals`, `F.reg.by_state` | `b09/regression/.../residuals.csv`, `by_customer_state.csv` | 872 x 350 each | legend, threshold labels |
| 15 | `F.reg.buffer_curve`, `F.clf.threshold_options` | `b12/regression/.../buffer_curve.csv`, `b09/classification/.../threshold_options.csv` | 700 x 300, 972 x 300 | legends, line labels; two panels |

Readable already: `F.A3.reg.target_kde`, `F.A3.clf.target_bar`, `F.reg.partition`, `F.reg.history_coverage`,
`F.clf.test_curves`. If you agree, Henry's Claude swaps the renders into the same slots and updates the D2 map.

## D4. Where the Pipeline A report lives

Proposed: `pipeline_b/deliverables/m2_report/` (markdown sections, same fill as the final report), Henry as owner,
new register items in `evidence/registry_B.yaml` under an `M2.` prefix. Or name another place inside
`experiments/experiment_5/`.

## D5. Audit coverage for the Pipeline A report

Should `audit_deliverables_B.py` also check the Pipeline A report (doc export against the filled sources, charts byte
for byte), or is `build_evidence_B.py fill/check` enough for it?

## D6. Test results in the Pipeline A report

The report would show A's frozen, plain and dummy models on A's own test rows (T1 `metrics_test.csv`, `A test rows`),
labelled as read once in the joint test read. Agree?

## D7. New stored outputs for the Pipeline A report (from the frozen A models; no refit)

In a small A-side stage of your choosing (for example `pipeline_b/stages/m2a/`) with `EVIDENCE.md` entries, so the
register can read them as a Current run:

1. **Interpretation.** For A's frozen regression and classification models on A's test rows: permutation importance
   (same method and scoring as B9's `permutation_importance.csv`) and coefficients / odds ratios (as B9's
   `coefficients.csv`), each with a figure.
2. **Error analysis.** On A's test rows: errors by customer state (MAE and share within 3 days; precision and recall
   at 1/6) with B9's judged-slice rule (at least 100 test orders, or 100 detractors), and a residuals figure for A on
   A's rows (T1's `test_errors` covers B's rows only).
3. **A-only test charts.** Every T1 chart draws A and B together, so none can go in an A-only report. Redrawn from the
   stored T1 and s06 data with A's rows only: validation folds and test for A (MAE; AP); precision–recall, ROC and
   reliability curves on A's test rows; A's confusion matrix at 1/6; train, validation and test side by side for A's
   dummy, plain and frozen models.

Already stored, not needed: T1 has A's test metrics, confusion matrix at 1/6 and fold-and-test table on A's rows; B9's
`train_val_test.csv` and `threshold_options.csv` carry A's rows.

## D8. `figure_map.json` doc section for the report at rev 56 (added later on 2026-10-29)

**Superseded 2026-10-30:** Henry, as delegated lead, rebuilt the doc section for rev 58 (B-CR-41 notice); no action needed.

Henry moved four charts from the report body to the appendices (drift, ROC-AUC/Brier by population, ranking
stability pair, A's correlation heatmap) and added table labels, a cover page, RMSE, R² and F1. The doc still has 28
charts with the same assets, but 23 of them now carry a different figure number. The audit still passes, because
`chart_ok` compares each asset with its register figure and not with its position, so the map's numbers are stale
without the audit noticing. The corrected doc section is in
`spec/doc_outbox/figure_map_doc_rev56_proposed.json` (same blob and asset ids, renumbered in reading order). Please
replace the `doc` section with it. Audit on rev 56 (export in `deliverables/audit/inputs/report_export_rev56.md`):
8 of 9 pass; the ninth is the deck map (D2).

The report also shows two app screenshots in section 8, captioned "Screenshots 1–2." rather than "Figure", because
they are not register charts; the audit's chart check does not cover them. Tell us if you want them handled
differently.

Rules unchanged: no stage reruns, no refits; never push to `main`.
