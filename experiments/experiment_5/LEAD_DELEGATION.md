# Lead delegation to Henry (from 2026-10-29 until Benson returns)

Benson (experiment lead, Wu Qianzong) delegates his full authority on Experiment 5 to Henry while Benson is away.

- **Henry may act as the lead:** approve, commit, merge `e5/deliverables-henry` into `milestone-3`, push, tag,
  and decide hosting and release steps.
- **Changing an existing rule** (README, decision logs, CR rules, frozen evidence, T1, tags): be cautious, and
  notify Benson first with what changes and why. Record every lead decision as a CR or B-CR row naming Henry
  as the delegated lead.
- **Not delegated, as before:** never rerun T1, never refit frozen recipes, never move or re-create a tag.
- **Open items at handover:**
  - review and merge `e5/deliverables-henry` (audit passes 9 of 9, `e302e8b`), after the app tests pass and
    every file the app reads is committed;
  - Streamlit hosting: recommended as a second Streamlit Cloud app on `milestone-3`, main file
    `experiments/experiment_5/pipeline_b/deliverables/dashboard/app/app.py` (its own requirements.txt), with
    no root changes;
  - report §8 URL and screenshots, proofreading, the PDF (due 2026-11-08), slides lock 2026-11-04.
