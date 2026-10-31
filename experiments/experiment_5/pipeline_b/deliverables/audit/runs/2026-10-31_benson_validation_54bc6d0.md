# Validation of milestone-3 at 54bc6d0 (Benson, 2026-10-31)

Type: third-party validation after the merge · Auditor: Benson's Claude, on Benson's Mac · Commit: `54bc6d0`
(milestone-3, merge of `e5/deliverables-henry`) · Response owner: Henry, delegated lead (LEAD_DELEGATION.md)

## What passed

- Experiment 5's frozen code and outputs are unchanged since `e5-reproduced`; the tags match origin.
- The dashboard's 21 tests pass on a fresh install.

## Findings and response

Triaged by Henry on 2026-10-31; both findings reproduced on Henry's Windows machine. The register row is in
`../findings.yaml`. Rules for the fix (Benson): change requests on milestone-3; no T1 rerun, no refit, no tag moved.

| Finding | Severity | Evidence | Decision | Fix (planned) | Guard | Status |
| --- | --- | --- | --- | --- | --- | --- |
| T-11 · `business_context/outputs/_manifest.json` records `smartcommerce_consolidated.csv` as `f130077f…`, the hash of the Windows CRLF working copy; git stores the file with LF, so on macOS, Linux, Streamlit Cloud and the teacher's machine `test_biz_sources_match_their_manifest` fails, 6 register tests error and the audit's report-charts check fails on `F.BIZ.revenue_repeat` | High (blocks submission) | Henry's machine: working copy CRLF `f130077f…`, LF-normalised and git blob `32c2f4ee…` (`git ls-files --eol`: `i/lf w/crlf attr/text=auto`) | Accept (B-G-15) | Hash text inputs (.csv, .json, .md, .txt) with CRLF normalised to LF where manifests are written (business_context producer and the other `MANIFEST_ROOTS` producers: M2A, DECK) and in `build_evidence_B.verify_manifest_source`; rerun the business_context producer; rebuild the register | Test that a CRLF and an LF copy of a text input give the same manifest hash; `test_biz_sources_match_their_manifest` on Mac | Fixed, awaiting Benson's recheck |
| T-06 · `tests/test_guards.py::test_text_io_names_an_encoding` fails with 50 text reads and writes without an explicit encoding (or newline); CR-058 deferred the fix to migration step 3, which CR-061 removed | Medium | Henry's machine: 50 violations, 18 in tooling and tests (`build_evidence_B.py` 4, `audit_deliverables_B.py` 1, `tests/test_register_B.py` 5, `test_adapter.py` 4, `test_serving.py` 3, `test_evidence_register.py` 1), 32 in frozen e5b modules | Accept (B-G-16) | Option 1: `encoding="utf-8"` (and `newline="\n"` where missing) in the 18 tooling and test lines. Option 2b: the 8 frozen e5b modules (t1_joint_test, adoption, adapter, b10, b09, b09_extra, doc_support, serving) are excluded by name in `test_guards.py`, with the reason and the CR number; the exclusion list is the only change there | `test_text_io_names_an_encoding` itself, still checking all new code | Fixed, awaiting Benson's recheck |

## Acceptance checks for the fix (from `experiments/experiment_5`)

1. The A suite: all pass.
2. `pipeline_b/tests`: all pass (skips are fine).
3. `build_evidence_B.py build`: only the build_manifest commit line changes.
4. The deliverables audit (command in `../README.md`): 9/9.
5. The normalised hash of `smartcommerce_consolidated.csv` is `32c2f4ee…` on Windows and on the Mac.

Then: one CR in `CHANGELOG.md` and one B-CR in `CHANGELOG_B.md`, commit, push, and the commit goes to Benson's
Claude for the recheck on the Mac (hand-off `../../../spec/doc_outbox/HS-01_benson_validation_fixes_2026-10-31.md`).
VERIFIED is set by Benson's recheck, not by the fixer.

## Result (Henry, 2026-10-31)

Fixed in CR-063 / B-CR-46: code in f460a90, the business_context rerun (run 20261031T150536Z, outputs
byte-identical, input hash `32c2f4ee…`) and the register rebuild in the next commit. On Henry's Windows machine: A suite 59
passed; `pipeline_b/tests` 23 passed, 5 skipped; deliverables audit 9/9; normalised CSV hash `32c2f4ee…`. The register build
changed the commit line, the BIZ items' run id, and the registry sha256 (stale since e35c041). Awaiting Benson's recheck
on the Mac.
