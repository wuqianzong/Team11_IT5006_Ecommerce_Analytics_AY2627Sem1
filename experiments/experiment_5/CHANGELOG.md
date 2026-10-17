# Experiment 5 change log

Every change to `spec/`, `e5lib/`, or an ACCEPTED node is recorded here
(README §9.2). Newest first.

| Date | ID | Change | Why | Files | Affected nodes (rerun from) | Approved by | Decisions changed? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-17 | CR-002 | Work directly on `milestone-3` instead of `e5/<node>` branches and PRs; commit only own node folder and sandbox, pull before push, no force-push, gate reviews cite a commit hash | Small team coordinating directly; containment already keeps changes inside experiments/experiment_5 | README.md (§3, §3.1, §8 rule 15, §9.2), AGENT_INIT_PROMPT.md | None (process only) | Team, experiment lead (Wu Qianzong) | — |
| 2026-10-17 | CR-001 | Pipeline design frozen at v1.0: 13-stage two-cycle draft replaced by one 10-stage textbook pass (s01_problem → s10_release); confirmation window dropped (chronological CV + one test); 27-feature baseline reduced in s04 and chosen per model on folds; target-cap value no longer fixed (candidates in protocol.yaml); class weight moved to tuning; Milestone 2 TA comments no longer a gate (teacher's M2 note is the rubric) | Team design review 2026-10-17 (doc "Milestone 3 pipeline stages", tab "Pipeline v2"); textbook order of Tutorials 7–8 | spec/pipeline_design.md, spec/stages.json, spec/sources.md, README.md, AGENT_INIT_PROMPT.md, stages/* (cards regenerated, empty draft cards removed) | All (no node implemented yet) | Team, experiment lead (Wu Qianzong) | — |
| 2026-10-16 | CR-000 | Protocol draft v0.1 created | Clean M3 baseline | README.md, spec/ | — | pending kickoff | — |
