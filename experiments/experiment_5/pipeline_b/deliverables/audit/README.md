# Deliverables audit (B11)

`python pipeline_b/audit_deliverables_B.py --doc <exported report .md> --deck <folder with project/slides> --doc-assets <dir> --deck-assets <dir>`

Rerun on the committed inputs (anyone, no account needed), from `experiments/experiment_5/`:

```
.venv/bin/python pipeline_b/audit_deliverables_B.py --doc pipeline_b/deliverables/audit/inputs/report_export_rev29.md --deck pipeline_b/deliverables/audit/inputs/deck --doc-assets pipeline_b/deliverables/audit/inputs/doc_assets --deck-assets pipeline_b/deliverables/audit/inputs/deck_assets
```

`inputs/` holds the report doc exported to Markdown at rev 29, the 12 deck slide files at deck version
1793077250-4a3c, and every chart asset of both (16 doc, 6 deck), read back from the live artifacts on 2026-10-27.

Inputs are read back from the live artifacts (report doc exported to Markdown; deck slide files and every chart
asset downloaded), never from local copies. `figure_map.json` records which register figure each chart is.

Last run 2026-10-26 on report doc rev 28 (`report_export_rev28.md`) and deck version 1793007227-4f95, after B-CR-30:
all 9 checks PASS (`audit_result.json`).
- Third-party audit V2: findings verified and answered in `third_party_audit_v2_response.md`.

Last run 2026-10-27 on the committed `inputs/` (report doc rev 29, deck version 1793077250-4a3c), after B-CR-33
(B10 round 3 and A's s03 EDA in the register): all 9 checks PASS (`audit_result.json`). B10-F2 and B11-F1 fixed,
pending Benson's ratification of B-G-10 and B-G-11.
