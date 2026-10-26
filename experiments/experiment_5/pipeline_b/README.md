# Pipeline B — improved (Pipeline A + change request CR-054)

Pipeline B is Pipeline A plus the change list of CR-054 (B-C1 to B-C13) and nothing else
(decision G-79, `../spec/blueprints/decision_log.md`). Everything not in that list is inherited
from Pipeline A as frozen at tag `e5-A-frozen`.

| | Pipeline A – baseline | Pipeline B – improved |
| --- | --- | --- |
| Folder | `../stages/` | `pipeline_b/stages/` |
| Scope | all states | customer and seller in SP, MG, RJ, PR, RS, BA, SC |
| Regression predicts | at checkout | at checkout |
| Classification predicts | at checkout | at carrier handover |
| Evidence IDs | 6.2, 8.4, … | B6.2, B8.4, … |
| Change log | `../CHANGELOG.md` | `CHANGELOG_B.md` |
| Decision log | `../spec/blueprints/decision_log.md` | `spec/decision_log_B.md` |
| Team decisions | `../spec/human_decisions.yaml` | `spec/human_decisions_B.yaml` |
| Tags | `e5-A-frozen` | `e5-B-sNN-accepted`, `e5-B-frozen` |

## Rules

1. **A is never touched.** Nothing in `../stages/`, `../e5lib/`, `../spec/` (apart from the one
   G-79 / CR-054 entry), `../tests/` or `../run_pipeline.py` is written by Pipeline B. A's
   foundation hash and run IDs never change because of B.
2. **B calls A's code, it does not copy it.** Inherited steps (factory, training, tuning,
   selection, metrics) are imported read-only from `e5lib`. B's own package `e5b/` holds only
   what is new: B's population rules, history features, the B4 ranking call and B's stage
   runners. B's runner refuses to run when A's foundation hash differs from the one at
   `e5-A-frozen`.
3. **Blueprint first.** A B stage is implemented only when its blueprint in `spec/blueprints/`
   is AGREED, as in A.
4. **Reviews.** The experiment lead reviews each B stage; the team reviews B6–B8 together at
   the B8 gate (as G-78 for A). Reviews happen in the doc tab group "Pipeline B (A + change
   request)".
5. **Test.** No B stage reads the test cohort. A and B are scored on the test once, together,
   after both are frozen (G-79).
6. **Citations.** The report cites B's numbers only from B's outputs, by file and B evidence
   ID, and only from the runs listed as current in `EVIDENCE.md` (checked by
   tests/test_evidence_register.py). Superseded rounds and probes are never cited.

## Status

| Stage | Blueprint | Build |
| --- | --- | --- |
| B2 Population and history features | AGREED | ACCEPTED round 2 (runs 20261023T154814Z regression, 20261023T154822Z classification; tag e5-B-s02-accepted-r2) |
| B4 Features | AGREED | ACCEPTED round 2 (runs 20261023T154827Z regression, 20261023T154833Z classification; tag e5-B-s04-accepted) |
| B5 Partition | AGREED | ACCEPTED round 1 (runs 20261023T160529Z regression, 20261023T160533Z classification; tag e5-B-s05-accepted) |
| B6–B7 Training and tuning | AGREED | ACCEPTED round 1 (runs b06 20261023T162830Z / 20261023T162918Z, b07 20261023T163311Z / 20261023T164241Z; tags e5-B-s06-accepted, e5-B-s07-accepted) |
| B8 Selection (gate, freeze) | AGREED | FROZEN (runs 20261024T042516Z regression, 20261024T042619Z classification; tag e5-B-frozen) |
| Joint test run T1 (A and B, one test read; A's 8.6–8.8 and B8.6–B8.8) | AGREED (spec/blueprints/joint_test.md; J-1 = (a)) | TEST READ ONCE (runs 20261024T044531Z regression, 20261024T044555Z classification; all checks pass; never rerun; tag e5-T1-tested) |
| B9 Conclusion (B primary, A as baseline; A's s09 does not run separately, G-79) | AGREED (spec/blueprints/b09_conclusion.md) | ACCEPTED (confirmed by Henry and the lead 2026-10-25; runs 20261025T132406Z regression, 20261025T132538Z classification on b09c396; tag e5-B-s09-accepted; B-G-06, B-G-07) |
| Doc support (charts and tables for the tabs and the report; DOC_GAPS) | not a stage blueprint (B-CR-19) | ACCEPTED with B9 (runs 20261025T132541Z, 20261025T132552Z on b09c396; tag e5-B-s09-accepted) |
| B10 Release (B10.1–B10.7; report, deck, dashboard and reproduction later) | AGREED 2026-10-26 (spec/blueprints/b10_release.md; B-G-08, B-G-09) | NOT STARTED (Henry on branch e5/b10-henry; see HANDOVER.md, WORKLOG.md) |
