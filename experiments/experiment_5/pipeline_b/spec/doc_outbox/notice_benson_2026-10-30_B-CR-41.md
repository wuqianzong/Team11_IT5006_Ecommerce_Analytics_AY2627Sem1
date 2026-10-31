# Notice to Benson: B-CR-41 and dashboard revision 2.3 (2026-10-30)

Henry, as delegated lead (LEAD_DELEGATION.md), changed two things you own. The delegation asks that you hear of
rule changes first; this is that notice.

1. **Register and audit (B-CR-41).** `build_evidence_B.py` accepts a new source prefix `BIZ/<file>`, read from
   `deliverables/business_context/outputs/` and accepted only if the file and its input data match that folder's
   `_manifest.json`. `audit_deliverables_B.py`'s `chart_ok` checks `BIZ/` charts the same way. The data is the
   dashboard's Business overview file (monthly revenue and customer repeat rate, March 2017 to April 2018, before
   the test period), computed with the dashboard's own code. No stage, model, T1 output or tag is touched.
2. **figure_map.json doc section** rebuilt for review doc rev 58 (29 figures; the new one is figure 1). This
   replaces D8 of the combined handshake.
3. **Dashboard revision 2.3.** Panels 2.8 and 3.9 (score pointers) removed; data health is now 2.8 and 3.9; tab 4
   is named "ML deployment". App tests pass.

If you disagree with any of it, tell Henry; each step is its own commit and can be reverted alone.
