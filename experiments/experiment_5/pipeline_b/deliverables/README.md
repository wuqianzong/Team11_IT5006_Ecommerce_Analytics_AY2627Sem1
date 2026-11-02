# B11 deliverables (drafts)

- `report/NN_*.md`: report sections with `{{id}}` placeholders (sources). Fill with
  `python pipeline_b/build_evidence_B.py fill <src> <out>`; check with `... check report/*.md`.
- Review copy: Claude Doc "Team 11 final report v2.2 — delivery time and detractor alerts" in Henry's account,
  https://claude.ai/artifact/USWnVhiKr35AqXwc4zQHAw (filled text; v1, rev 118, stays at
  https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid with its sources frozen in `report_v1/`). The team comments there; changes come back
  here first, then the doc is refreshed.
- No open placeholders (app URL in the cover and §8, screenshots in appendix L; B-CR-49). Section 3 cites A's s03 EDA from A's frozen tree (B-G-11).
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
- Deck: v2.2 https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc (current; v2 until 2 Nov, then v2.1 (B-CR-47) and v2.2 (B-CR-49)); v1 https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23 (Henry's account, private until shared). 12 slides; titles,
  text and tables are editable; charts are uploaded register PNGs (validation_and_test ×2, population, residuals,
  threshold_options, partition).
- Slide 16 "app" carries the app screenshots (appendix L files, register S.05/S.06), the live URL and the repository
  link (B-CR-48); 16 slides.
