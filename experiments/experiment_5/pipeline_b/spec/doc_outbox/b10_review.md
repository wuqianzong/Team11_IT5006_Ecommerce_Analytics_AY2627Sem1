# B10 Release — for team review

**Built · clean runs 20261026T024749Z (regression), 20261026T024858Z (classification) on 1e36f0a, all checks PASS; byte-identical on a second run.** Built by Henry's Claude on branch e5/b10-henry while Benson is away (pipeline\_b/HANDOVER.md). Approved by Henry on Benson's behalf; tag e5-B-s10-accepted-r2.

## Points for review

1. **Parity (B10.1).** The T1 bundles reload and re-predict T1's saved test predictions within 1e-9 on Python 3.13.7, from test rows rebuilt with every label column blanked (B-G-08). This is the acceptance test of Henry's environment.
2. **Operating threshold 4/15 (B-G-07), round 2.** Round 1 used 5/14 (B-G-09); Henry confirmed 5/14 was a typo, so B-G-09 is withdrawn and B10 is rerun with 4/15. The frozen 1/6 and its T1 result stay the unbiased result. Round 1 is superseded (tag e5-B-s10-accepted stays on it); round 2 approved by Henry for Benson, tag e5-B-s10-accepted-r2.
3. **Alert volumes (B10-D2), re-confirmed by the team (Henry, 2026-10-26).** Test (post-test view): B 5.6/day at 4/15 plus A 14.9/day at 1/6 outside B's scope = 20.5/day. Validation: B 4.0/day plus A 6.5/day. Most alerts come from A's fallback outside the seven states (classification sub-tab, threshold\_results.csv).
4. **No refit (B10-D10).** Refitting the frozen logistic recipe is not bit-reproducible across machines: on Henry's machine the out-of-fold rebuild differs from B8's calibration step by up to about 1.5e-3 AP per fold. B10 therefore restates B9's stored files (1/6 and 4/15 exactly). This also matters for the later reproduction check (A's s10 10.4).
5. **Before handover (B10-D9).** In-scope orders not yet handed over get no score; the missed-dispatch rule flags them.
6. **Out-of-profile limit (B10-D11):** the app warns when a numeric input is more than 4 SD from the training mean; warning only.

## Coverage

| Task | Evidence | Status | Review |
| --- | --- | --- | --- |
| regression | B10.1 | IMPLEMENTED | Open |
| regression | B10.2 | IMPLEMENTED | Open |
| regression | B10.3 | IMPLEMENTED | Open |
| regression | B10.4 | IMPLEMENTED | Open |
| regression | B10.5 | IMPLEMENTED | Open |
| regression | B10.6 | IMPLEMENTED | Open |
| regression | B10.7 | IMPLEMENTED | Open |
| classification | B10.1 | IMPLEMENTED | Open |
| classification | B10.2 | IMPLEMENTED | Open |
| classification | B10.3 | IMPLEMENTED | Open |
| classification | B10.4 | IMPLEMENTED | Open |
| classification | B10.5 | IMPLEMENTED | Open |
| classification | B10.6 | IMPLEMENTED | Open |
| classification | B10.7 | IMPLEMENTED | Open |

## Next

On approval: tag e5-B-s10-accepted on the branch. Then, each only when ordered: sign-off and e5-release-1, migration (lead), reproduction check, app and dashboard build, report and slides.
