# Deliverables audit (B11)

`python pipeline_b/audit_deliverables_B.py --doc <exported report .md> --deck <folder with project/slides> --doc-assets <dir> --deck-assets <dir>`

Rerun on the committed inputs (anyone, no account needed), from `experiments/experiment_5/`, in the Experiment 5
environment (`.venv`, pandas 3.0.1; `requirements-audit.txt` here pins the extra packages the audit, the dashboard
tests and the audit pack need):

```
.venv/Scripts/python.exe pipeline_b/audit_deliverables_B.py --doc pipeline_b/deliverables/audit/inputs/report_export_rev72.md --deck pipeline_b/deliverables/audit/inputs/deck --doc-assets pipeline_b/deliverables/audit/inputs/doc_assets --deck-assets pipeline_b/deliverables/audit/inputs/deck_assets
```

(`.venv/bin/python` on macOS or Linux.)

## Inputs

Inputs are read back from the live artifacts (the report doc exported to Markdown; deck slide files and every chart
asset downloaded), never from local copies. `figure_map.json` records which register figure each chart is.

- `inputs/report_export_rev72.md`: the final report review doc exported to Markdown at rev 72 (2026-10-30).
- `inputs/deck/project/`: the 15 slide files and `deck.json` of deck v2, version 36 (2026-10-30).
- `inputs/doc_assets/` (29) and `inputs/deck_assets/` (20): every chart of the report and the deck. Of the deck's
  20, 18 are presentation renders (`deck/renders/`, register source `DECK/...`, B-CR-43) and 2 are the original
  stage PNGs.

## Last run

2026-10-30 on the committed inputs (report rev 72, deck version 36), after B-CR-44 (third-party audit fixes):
all 9 checks PASS (`audit_result.json`, which records the sha256 of the doc and of each slide).

## Expected differences when re-checking

- `evidence/build/build_manifest.json` records the commit the register was **built** on, which is the parent of the
  commit that stores the build. It is expected to differ from the commit being audited. What must match is the
  registry sha256, the item count and the per-item outputs, which `build_evidence_B.py check` and the tests verify.
- The doc header line (title, date, review note) is not part of the body comparison; the audit prints it as
  "header kept".

## Earlier runs

- 2026-10-26, report rev 28 and deck v1: 9/9; third-party audit V2 answered in `third_party_audit_v2_response.md`.
- 2026-10-27, report rev 29 and deck v1, after B-CR-33: 9/9.
- 2026-10-30, report rev 68 and deck v2 version 35, after B-CR-43: 9/9 (audit run on the live copies).
