# B10 Release — for team review

**Built · clean runs 20261026T020904Z (regression), 20261026T021016Z (classification) on adf23d6, all checks PASS; byte-identical on a second run.** Built by Henry's Claude on branch e5/b10-henry while Benson is away (pipeline\_b/HANDOVER.md). Not tagged: e5-B-s10-accepted waits for Benson's or the lead's approval.

## Points for review

1. **Parity (B10.1).** The T1 bundles reload and re-predict T1's saved test predictions within 1e-9 on Python 3.13.7, from test rows rebuilt with every label column blanked (B-G-08). This is the acceptance test of Henry's environment.
2. **Operating threshold 5/14 (B-G-09).** Replaces 4/15 as a second post-test change; the frozen 1/6 and its T1 result stay the unbiased result. Benson to confirm B-G-09.
3. **Alert volumes (B10-D2), accepted by the team.** Test (post-test view): B 2.4/day at 5/14 plus A 14.9/day at 1/6 outside B's scope = 17.3/day. Validation: B 1.5 to 1.7/day plus A 6.5/day. Most alerts now come from A's fallback outside the seven states (classification sub-tab, threshold\_results.csv).
4. **No refit (B10-D10).** Refitting the frozen logistic recipe is not bit-reproducible across machines: on Henry's machine the out-of-fold rebuild differs from B8's calibration step by up to about 1.5e-3 AP per fold. B10 therefore restates B9's stored files; 5/14 on validation is bracketed by the stored 0.36 and 0.35 rows. This also matters for the later reproduction check (A's s10 10.4).
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
