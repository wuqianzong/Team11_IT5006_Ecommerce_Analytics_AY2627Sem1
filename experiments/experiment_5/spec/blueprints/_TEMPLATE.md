# sNN_name — blueprint

| Field | Value |
| --- | --- |
| Stage | sNN_name (`../pipeline_design.md` → sNN) |
| Nodes | common / regression, classification |
| Status | NOT STARTED |
| Owner | TBD |
| Last agreed | — |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "sNN" |

## 1. Goal and gate
One line each, from the frozen design and `../stages.json`.

## 2. Inputs
Upstream files (exact paths under `stages/*/outputs/`), data population (development or test),
and the `protocol.yaml` keys read.

## 3. Method
Numbered steps, down to the sklearn objects and settings. Regression and classification
differences in a short subsection.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| sNN-D1 | | | tutorial / literature / M2 evidence | Proposed |

Every row is mirrored in `decision_log.md`.

## 5. Outputs
Each file with its columns or schema (standard shapes: README §5.5).

## 6. Checks
Tests and assertions that prove the gate is met, including leakage checks.

## 7. Milestone 2 reuse
Exact `src/…:line` (or `experiments/…`) to copy into `e5lib/` with a provenance comment,
and what to fix when copying.

## 8. Report hooks
Tables and figures this stage feeds (evidence IDs, report section, slide).

## 9. Open questions
Only genuine forks that need the team.
