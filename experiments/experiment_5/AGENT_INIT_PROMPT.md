# Agent initialization prompt — Experiment 5

Paste the block below as the **first message** of a new agent session (Claude Code, Codex,
etc.) opened at the repository root. Only `<YOUR NAME>` needs filling. What the agent
works on is decided later in the conversation and may change; the rules do not.

---

```text
You are working with <YOUR NAME> on IT5006 Group 11, Milestone 3, Experiment 5.

WHAT EXPERIMENT 5 IS
A clean, textbook-ordered replay of our Milestone 2 pipeline (Olist; delivery lead-time
regression and low-review classification at checkout), run as one ten-stage pass
(s01_problem → s10_release; design frozen v1.0, 2026-10-17). Its code, data and evidence must
be consistent and fully regenerable, so the Milestone 3 report, deck and app can be
rebuilt from one command after any change.

START OF SESSION (do this now, before anything else)
1. Read completely: experiments/experiment_5/README.md (binding protocol), then
   spec/pipeline_design.md, spec/sources.md and spec/stages.json in that folder.
   Read spec/protocol.yaml if it exists.
2. Run `git status` and `git branch --show-current`; report the branch and whether the
   tree is dirty. Do not switch branches or pull until I say so.
3. If experiments/experiment_5/run_pipeline.py exists, run its `status` command and
   summarise it; otherwise say it is not built yet.
4. Reply with a short confirmation: the rules you will follow (in your own words, max 8
   bullets) and the current pipeline state. Then wait for me to give you a task.

SCOPE
I will tell you what to work on (a node, a review, the design, a question). It may change
during our conversation. Before each new piece of work, restate the scope in one line —
which node(s)/files you will touch and which upstream outputs you will read — and check
it is a node I own (STAGE.md `owner`) or that I explicitly asked for. If not, ask.

RULES THAT NEVER CHANGE (full list: README sections 0.1 and 8)
- CONTAINMENT: write only inside experiments/experiment_5/. Never write, move or delete
  anything outside it (src/, artifacts/, deployment/, data/, docs/, notebooks/, root
  files, other experiments). Reading outside is fine. All code, outputs, models, figures,
  evidence, app code and report/deck drafts stay in experiments/experiment_5/.
- NO MIGRATION: never copy or promote Experiment 5 work into the working folders, even
  partially, unless the experiment lead explicitly orders the migration (README section
  12). If asked by anyone else, decline and point to section 12.
- Inside Experiment 5, edit only the node folder(s) in scope and sandbox/<my name>/.
  Changes to spec/, e5lib/, tools/ or other members' nodes: propose a change request
  (README section 9.2), do not make them.
- Never import from src/ or other experiments; reused logic is copied into e5lib/ with a
  provenance comment (via a change request). Resolve paths through e5lib/paths.py; no
  absolute paths.
- Data only via e5lib.data.load (population guard); models only via
  e5lib.factory.build(spec); seeds, folds, grids, thresholds and costs only from
  spec/protocol.yaml.
- Learned preprocessing inside training folds. EDA and features use only orders before
  the test cutoff; test-cohort labels are read once, in s08, after the recipe and
  threshold are frozen. IDs are never predictors.
- Simplest model first; one change at a time on the same rows and folds; keep the simpler
  variant unless the protocol's decision rule says otherwise. Do not assume the
  Milestone 2 winner wins.
- run.py regenerates all of outputs/ deterministically; never hand-edit outputs/. Use the
  standard output files and write _manifest.json (README sections 5.5 and 6.1).
- Never type a metric from memory into STAGE.md, a report or slides; cite the output file
  or evidence ID.
- Work on a branch named e5/<node-or-topic>; PRs go into milestone-3. Do not commit or
  push without my go-ahead.
- At the end of a node: run_pipeline.py run --node <node>, then run_pipeline.py check;
  fill Review summary / Deviations / Open questions in STAGE.md; set READY_FOR_REVIEW.
  Then STOP at the gate: do not start the next stage, change upstream nodes, or tune
  results to look better. Report weak or negative results honestly.
- If the spec is unclear, wrong, or conflicts with what I ask, quote the conflicting text
  (file and section) and ask me. Do not invent a method or interpretation, and do not
  resolve a conflict between my request and these rules by yourself.
```

---

## Example first tasks (send after the agent confirms)

- **Implement a node:** `Work on s06_training/regression. Show me your plan before writing code.`
- **Review a node:** `Review s03_eda/classification at commit <sha> against its gate criteria,
  the pipeline_design.md stage, the spec/sources.md rows for S03 and README sections 5 and 8.
  Rerun it and confirm outputs/manifest hashes match. Do not edit it; give me findings for
  its "Gate check" section.`
- **Change request (design is frozen at v1.0):** `Draft a CHANGELOG entry for <change>
  per README section 9.2: which spec/ files change, which nodes rerun from where, and
  whether it breaks a teacher/TA requirement or the textbook order. Do not edit spec/
  until the experiment lead approves.`
