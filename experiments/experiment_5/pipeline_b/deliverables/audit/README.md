# Deliverables audit (B11)

`python pipeline_b/audit_deliverables_B.py --doc <exported report .md> --deck <folder with project/slides> --doc-assets <dir> --deck-assets <dir>`

Inputs are read back from the live artifacts (report doc exported to Markdown; deck slide files and every chart
asset downloaded), never from local copies. `figure_map.json` records which register figure each chart is.

Last run 2026-10-26 on report doc rev 28 (`report_export_rev28.md`) and deck version 1793007227-4f95, after B-CR-30:
all 9 checks PASS (`audit_result.json`).
- Third-party audit V2: findings verified and answered in `third_party_audit_v2_response.md`.
