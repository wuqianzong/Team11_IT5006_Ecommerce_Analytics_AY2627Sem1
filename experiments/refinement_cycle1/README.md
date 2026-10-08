# Milestone 2: one refinement cycle

The **current applied state** is `refinement-selected-v3`: a 13-input delivery
decision tree and a 14-input regularised review-risk logistic classifier.
The reusable base table still has 27 predictors. Earlier notebooks 04–07 and
stage3/4/5 artifacts are the historical grouped-random baseline, not this model.
Notebook 08 reviews the current model and can rebuild its fixed choices.

## Read the evidence without fitting

`artifacts/metrics/refinement-selected-v3/` publishes selected trusted scoring
bundles, final tables and charts. `artifacts/metrics/refinement-cycle1-evidence/`
contains the complete compact trial evidence, including unsuccessful candidates.
These lossless archives contain configurations, predictions, cohort IDs, warnings,
pipeline states and numerical audits. Repeated validation metadata is stored once
per cohort, then reconstructed byte-for-byte by the unpack command. Intermediate
pickles and repeated per-job training-ID lists are regenerated; training digests,
membership and complete-case rules remain recorded.
`execution_issues/` also retains the zero-fit membership-dtype preflight failure,
its correction and the named regression test; it is not counted as a model trial.

From the repository root, with Python 3.13.9:

```bash
python -m pip install -r requirements.txt -r src/models/requirements-stage3.txt
python -m experiments.refinement_cycle1.evidence unpack --output artifacts/generated/accepted-evidence
python -m experiments.refinement_cycle1.report_evidence --run artifacts/generated/accepted-evidence/final --verify
```

Choose a new output directory every time. Archive/input/member checksums are
checked before inspection. The folders unpack as:

| Folder | Scientific phase | Original predictive fits |
| --- | --- | ---: |
| initial_reference/results and audit | E01 model comparison; E02 count removal; E03 calendar-only; E04 no-payment; E05 full features; E06 count removal in rich inputs; E07 rare-state grouping; E08 complete-case training | 255 |
| core | Initial 11-input final/reference fits and frozen policy | 8 |
| core_terminal | Initial previously inspected later-period diagnostic | 0 |
| screen | Five feature blocks, two tasks, five windows | 50 |
| combinations | Six regression and four classification combinations | 50 |
| model_gate | Plain-family baseline comparison, plus 15 reused results | 50 |
| final | Ten confirmation-fold fits, nine final/reference fits and final diagnostic | 19 |

Total original predictive fits: **432**. Verification/permutation/terminal scoring
are not predictive fits. A full reproduction repeats those calculations; it is
not additional feature exploration. Reused results are not counted twice.

## Reproduce all phases from Git alone

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.refinement_cycle1.reproduce --output artifacts/generated/full-check-01 --acknowledge-previously-inspected-terminal
```

This command regenerates all intermediate models and scientific audits, checks
training-only preprocessing and memberships, recomputes paired comparisons, and
compares every candidate's validation predictions and numerical tables against
the accepted compressed evidence. It also checks the final decisions and report
numbers. Completion is recorded in `reproduction_verification.json`; failed
attempts remain in place with `reproduction_failure.json`. Never delete a failed
run and call a retry the original attempt. No private document, report, old model,
external data download or teaching-material folder is needed.

The `initial_reference/` code is the original diagnostic algorithm with portable
paths and stable class imports. Later trial runners retain frozen scientific
protocols; `paths.py` relocates evidence/output bindings only. Original source
hashes, archived run identities and original warnings remain historical
provenance; they are not promises that portable source bytes equal old source
bytes. Fresh runs create and verify their own source/config/input identities.
Private report/worktree preservation checks are not scientific gates in a new
checkout. Numerical mismatches stop the run; do not weaken tolerances or retune.

## Short route: reproduce only the applied choices

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m src.models.refinement_selected build --output artifacts/generated/final-check-01
python -m src.models.refinement_selected_verify --run artifacts/generated/final-check-01
python -m src.models.refinement_diagnostics --run artifacts/generated/final-check-01
python -m src.models.refinement_selected_terminal --run artifacts/generated/final-check-01 --acknowledge-previously-inspected-terminal
python -m src.models.refinement_selected_terminal_verify --run artifacts/generated/final-check-01
python -m experiments.refinement_cycle1.report_evidence --run artifacts/generated/final-check-01 --verify
```

This route uses 19 fixed-choice fits. It confirms the final choices, **not** the
full search that selected them. Original raw/preprocessed data, deterministic
features, split assignments and pinned IBGE geography are already tracked.
Feature construction is executable through `src.features.build_features` and
`src.features.create_splits`; do not overwrite accepted inputs during verification.

## Verify the separately supplied report

`report_evidence.json` maps claim IDs, sections, selectors, fields and full-precision
values to final files. It records the authoritative external Markdown SHA-256.
Provide that exact Markdown version optionally:

```bash
python -m experiments.refinement_cycle1.report_evidence --run artifacts/generated/accepted-evidence/final --verify --report /path/to/the/final-report.md
```

The report itself is shared separately. Git reproduces its calculations, not its
prose or Word layout. Section 4 uses initial audits; section 5 uses block,
incremental-combination and model-comparison tables. Sections 6–7 and appendices
B–C use current final/development tables and charts. Human review must still
check interpretation, citations, assumptions and rounding.

## Chronology and limitations

This cycle was adaptive, **not entirely preplanned**. Initial terminal evidence
was examined before expansion was proposed; each later catalogue froze before
its own fits. Both terminal assessments are previously inspected diagnostics,
not independent tests. The original 20% random holdout is excluded here.
No terminal result selected a replacement model or threshold. The selected tree
does worse than simple references on the later-period cohort; classification
has modest ranking value. Keep those negative results in the report.

The 5:1 false-negative/false-positive cost ratio is illustrative, not measured.
Inputs reconstruct order-placement snapshots, not certified live availability.
Exact numerical parity is checked with relative/absolute tolerance `1e-10`;
timings, output paths, timestamps and serialized bytes are not cross-platform
parity claims. Only load trusted joblib files; checksums do not make pickle safe.
