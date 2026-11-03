# Deliverables audit (B11)

`python pipeline_b/audit_deliverables_B.py --doc <exported report .md> --deck <folder with project/slides> --doc-assets <dir> --deck-assets <dir>`

Rerun on the committed inputs (anyone, no account needed), from `experiments/experiment_5/`, in the Experiment 5
environment (`.venv`, pandas 3.0.1; `requirements-audit.txt` here pins the extra packages the audit, the dashboard
tests and the audit pack need):

```
.venv/Scripts/python.exe pipeline_b/audit_deliverables_B.py --doc pipeline_b/deliverables/audit/inputs/report_export_rev59.md --deck pipeline_b/deliverables/audit/inputs/deck --doc-assets pipeline_b/deliverables/audit/inputs/doc_assets --deck-assets pipeline_b/deliverables/audit/inputs/deck_assets
```

(`.venv/bin/python` on macOS or Linux.)

## Findings register

`findings.yaml` holds every finding and action item from every audit (ID, source, severity, owner, status, due,
decision, fix, guard, verified by); `runs/` keeps each audit report as received with
its triage. Open on 2026-10-31: T-07, T-08, T-09; T-11 and T-06 (Benson's validation at 54bc6d0) fixed in CR-063 / B-CR-46, awaiting
Benson's recheck.

## Inputs

Inputs are read back from the live artifacts (the report doc exported to Markdown; deck slide files and every chart
asset downloaded), never from local copies. `figure_map.json` records which register figure each chart is.

- `inputs/report_export_rev59.md`: the final report v2.3 review doc at rev 59 (2026-11-03, B-CR-52: figures 20–23 as
  half-width report renders). Built from rev 53's Markdown export with the eight lines revs 54–59 changed (four picture
  alt texts, four captions), each confirmed by a doc read of the changes since rev 53.
- `inputs/deck/project/`: the 18 slide files and `deck.json` of deck v2.3, version 48 (2026-11-03; a version saved by
  the open editor one second later has identical files).
- `inputs/doc_assets/` (29) and `inputs/deck_assets/` (22): every chart of the report and the deck. Of the deck's
  22, 18 are presentation renders (`deck/renders/`, register source `DECK/...`, B-CR-43; the business-case promise
  render replaces the buffer-curve render, B-CR-50), 2 are the original stage PNGs and 2 are app screenshots
  (register source `SHOT/...`, B-CR-48). Report figure 24 is the business-case chart (register source `BCASE/...`); figures 20–23 are half-width report
  renders (`report/renders/`, register source `REPORT/...`, B-CR-52).

## Last run

2026-11-03 on the committed inputs (report v2.3 rev 59, deck v2.3 version 48), after B-CR-52 (figures 20–23 side by
side): all 9 checks PASS (`audit_result.json`).

After B-CR-53 (v2.4 sources, before the doc and deck sync), on the same committed inputs: register recomputation and
both alignment checks PASS; the six checks that compare the live doc and deck with the sources FAIL until Henry
syncs review doc and deck to v2.4, as expected. `audit_result.json` is not updated by this run.

## Expected differences when re-checking

- `evidence/build/build_manifest.json` records the commit the register was **built** on, which is the parent of the
  commit that stores the build. It is expected to differ from the commit being audited. What must match is the
  registry sha256, the item count and the per-item outputs, which `build_evidence_B.py check` and the tests verify.
- The doc header line (title, date, review note) is not part of the body comparison; the audit prints it as
  "header kept".

## Earlier runs

- 2026-11-03, report v2.3 rev 53 and deck v2.3 version 48, after B-CR-51: 9/9.
- 2026-11-03, report v2.3 rev 51 and deck v2.3 version 48, after B-CR-50: 9/9.

- 2026-11-02, report v2.2 rev 48 and deck v2.2 version 44, after B-CR-49: 9/9.

- 2026-11-02, report v2.1 rev 45 and deck v2.1 version 43, after B-CR-48: 9/9.

- 2026-11-02, report v2.1 rev 45 and deck v2.1 version 41, after B-CR-47: 9/9 (number check skips the doc header).
- 2026-11-02, report v2 review doc rev 43 and deck v2 version 40 (live copies), after B-CR-47: 9/9.

- 2026-10-31, report rev 73 and deck version 39, after CR-063 / B-CR-46 (line-ending-safe hashes, encoding guard): 9/9.

- 2026-10-30, report rev 72 and deck version 36, after B-CR-44: 9/9.
- 2026-10-26, report rev 28 and deck v1: 9/9; third-party audit V2 answered in `third_party_audit_v2_response.md`.
- 2026-10-27, report rev 29 and deck v1, after B-CR-33: 9/9.
- 2026-10-30, report rev 68 and deck v2 version 35, after B-CR-43: 9/9 (audit run on the live copies).
