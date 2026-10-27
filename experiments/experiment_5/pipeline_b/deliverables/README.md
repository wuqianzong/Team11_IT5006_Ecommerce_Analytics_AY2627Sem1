# B11 deliverables (drafts)

- `report/NN_*.md`: report sections with `{{id}}` placeholders (sources). Fill with
  `python pipeline_b/build_evidence_B.py fill <src> <out>`; check with `... check report/*.md`.
- Review copy: Claude Doc "Team 11 final report — delivery time and detractor alerts" in Henry's account,
  https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid (filled text). The team comments there; changes come back
  here first, then the doc is refreshed.
- Open placeholders: app URL and screenshots (section 6). Section 3 cites A's s03 EDA from A's frozen tree (B-G-11).
  Appendices A–F are done (B-CR-28).

## Figures in the report doc (uploaded from evidence/build/figures, 2026-10-26)

Fig 1 F.reg.lateness_by_route (§3) · 2 F.reg.selection, 3 F.reg.partition (§4) · 4 F.reg.validation_and_test,
5 F.reg.population, 6 F.reg.residuals, 7 F.reg.by_state, 8 F.clf.validation_and_test, 9 F.clf.test_curves,
10 F.clf.threshold_options (marks frozen 1/6 and operating 4/15), 11 F.clf.by_state,
12–13 F.*.importance, 14–15 F.*.coefficients (§5) · 16 F.reg.drift (§8).
A figure changes only by re-uploading the rebuilt PNG (blobs are immutable).

## Deck (Claude Slides, B11-D6)

- Sources: `deck/project/deck.json` and `deck/project/slides/*.html` with `{{id}}` placeholders. Fill each slide with
  `build_evidence_B.py fill` into a publish folder, then publish `project/…` to the deck.
- Deck: https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23 (Henry's account, private until shared). 12 slides; titles,
  text and tables are editable; charts are uploaded register PNGs (validation_and_test ×2, population, residuals,
  threshold_options, partition).
- Placeholder: app screenshot and live URL on slide "deploy".
