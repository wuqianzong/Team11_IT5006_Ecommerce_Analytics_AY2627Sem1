# Notice to Benson: B-CR-43, deck v2 chart map and presentation renders (2026-10-30)

Henry, as delegated lead (LEAD_DELEGATION.md), closed D2 and D3 of the combined handshake.

1. **D3, renders.** `deliverables/deck/renders/make_deck_renders.py` redraws 14 deck charts from the data file saved
   beside each stored PNG (plus A's stored cut points and B12's buffer choice), sized to its slide box with text of at
   least 18 pt. No stage rerun, no fit, no new number; the original PNGs and the report are unchanged. Run
   20261030T100629Z on 94eb47a. Two charts are redesigned rather than enlarged: the correlation heatmap is shown as the
   ranked list of the 10 predictor pairs with |rho| >= 0.5 (flag line at 0.9), and the selection charts show the top 8
   features with the kept count. The register reads the renders as `DECK/<file>` (the manifest check of B-CR-41/42);
   each carries its original's evidence ID.
2. **D2, map.** `figure_map.json` deck section maps the 20 images of deck v2 (version 35): the 6 originals, verified
   byte-identical to the deck's uploaded assets, and the 14 renders. The deliverables audit passes all 9 checks
   (report export rev 68, deck version 35).

Still open from the combined handshake: nothing on the deck; D1 and D4–D7 were settled by B-CR-42.
