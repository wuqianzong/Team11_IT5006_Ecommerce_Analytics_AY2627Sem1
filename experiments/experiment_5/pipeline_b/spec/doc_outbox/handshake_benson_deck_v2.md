# Handshake prompt for Benson: deck v2 (2026-10-29)

Paste this into Benson's Claude session on `milestone-3` after fetching `origin/e5/deliverables-henry`.

---

Henry reworked the deck after his review. v1 stays as it was (https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23;
sources frozen in `pipeline_b/deliverables/deck_v1/`). v2 is a new deck
(https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc), and its sources replace `pipeline_b/deliverables/deck/`, which the
audit reads. v2 tells the story A first: A's features, multicollinearity and selection, validation and ladder, then A's
three limits, then B. Two decisions are needed from you, as experiment lead.

## Decision 1: extend B-G-13 to Pipeline A's s04–s08 figures (proposed B-G-14)

Slides 7 and 8 show A's own selection, folds and ladder, but those charts sit in A's stages s04–s08, which B-G-11 (s03)
and B-G-13 (s02) do not cover. The slots are marked "pending" on the slides. Proposal, under the same conditions as
B-G-11 and B-G-13 (read only from the file at tag `e5-A-frozen`, sha256 checked by `build_evidence_B.verify_a_source`,
A's evidence ID carried):

| Slide | A file (under `stages/`) |
| --- | --- |
| 7 | `s04_features/regression/outputs/figures/selection_cumulative.png`, `s04_features/classification/outputs/figures/selection_cumulative.png` |
| 8 | `s05_partition/regression/outputs/figures/partition_diagram.png`, `s06_training/regression/outputs/figures/family_ladder.png`, `s06_training/classification/outputs/figures/family_ladder.png` |
| 8 (optional) | `s08_selection/regression/outputs/figures/finalists.png`, `s08_selection/classification/outputs/figures/finalists.png` |

Agree, change or refuse. If you agree, record B-G-14 in `spec/decision_log_B.md` and `spec/human_decisions_B.yaml`;
Henry's Claude then adds the register items and fills the slots.

## Decision 2: `figure_map.json` deck section for v2

The deck charts now live in the v2 artifact. The deck map should be replaced by these asset ids (v2 asset → register
figure):

```
599ab1acabc2699da29fdc0ffc40a0fe F.A2.data_structure
617e556f7ca00f5865ddcc3d68cef704 F.A3.reg.target_kde
6bcb1233fa3679606ae16b9ef0ccdd6d F.A3.reg.cumulative_importance
c6a5ce7bcb7b95879aabd101aad62ce9 F.A3.clf.cumulative_importance
8b7e8ad18ab84791e80a1aae513cb35f F.A3.reg.correlation_heatmap
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

`F.A2.data_structure` and the three `F.A3.clf.screen_*` / `F.A3.*.cumulative_importance` items are new register items
(B-G-13 and B-G-11 sources). `chart_ok` already checks A sources against `e5-A-frozen` (B-CR-40). Then run the audit
against the v2 deck.

Rules unchanged: no stage reruns, no refits; never push to `main`.
