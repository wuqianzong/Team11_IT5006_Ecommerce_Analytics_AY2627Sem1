# Deliverables audit (B11)

`python pipeline_b/audit_deliverables_B.py --doc <exported report .md> --deck <folder with project/slides> --doc-assets <dir> --deck-assets <dir>`

Inputs are read back from the live artifacts (report doc exported to Markdown; deck slide files and every chart
asset downloaded), never from local copies. `figure_map.json` records which register figure each chart is.

Last run 2026-10-26 on report doc rev 25 (`report_export_rev25.md`) and deck version 1792983799-0158:
all 9 checks PASS (`audit_result.json`).
