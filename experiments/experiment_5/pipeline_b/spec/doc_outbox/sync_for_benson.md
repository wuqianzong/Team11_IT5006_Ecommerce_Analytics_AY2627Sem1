# Sync note for Benson (B10 and B11 on branch e5/b10-henry)

Written 2026-10-26 by Henry's Claude. Read with `../../HANDOVER.md` and `../../WORKLOG.md`. Everything is on branch
`e5/b10-henry`, starting from 85822c8 (= `e5-B-s09-accepted`); nothing is merged into `milestone-3`.

## 1. What you need to publish to the team doc

| Outbox file | Doc tab | Note |
| --- | --- | --- |
| b10_blueprint_tab.md | B blueprints → new section "B10 — release" | round 2 (4/15) |
| b10_review.md | B implementation reviews → new sub-tab "B10 Release" | round 2 |
| b10_review_regression.md | B10 Release › regression | round 2 |
| b10_review_classification.md | B10 Release › classification | round 2 |
| b11_blueprint_tab.md | B blueprints → new section "B11 — report and deck" | AGREED |

Then refresh the read-only mirror `spec/team_doc/` from the doc, as at every acceptance.

The report draft is a separate Claude Doc in Henry's account (B11-D5), shared by link:
https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid. Your Claude cannot read it (different account); its source is
`pipeline_b/deliverables/report/`.

## 2. Decisions taken while you were away

| ID | Decision | Status |
| --- | --- | --- |
| B-G-08 | Release parity may re-predict T1's test rows without labels or scoring | Agreed (you) |
| B-G-09 | Operating threshold 5/14 | **Withdrawn** 2026-10-26: Henry confirmed 5/14 was a typo |
| B-G-07 | Operating threshold 4/15 (post-test; frozen 1/6 stays the unbiased result) | Agreed, reinstated |
| B10-D1 to D7 | Scope of B10 as you approved | Agreed (you) |
| B10-D8 | Threshold value: 4/15 | Agreed (Henry) |
| B10-D9 | In-scope orders before handover get no score; missed-dispatch rule flags them | Agreed (Henry) |
| B10-D10 | No refit in B10: refits are not bit-reproducible across machines (out-of-fold AP differs by up to about 1.5e-3 on Henry's machine); B10 restates B9's stored files | Agreed (Henry) |
| B10-D11 | Out-of-profile warning at 4 SD from the training mean | Agreed (Henry) |
| B10-D2 | A's fallback at its frozen 1/6; alert volumes | Agreed; volumes accepted for 5/14, **to re-confirm for 4/15** |
| B11-D1 to D9 | Report and deck drafted before migration (deviation from s10-D3, slides lock 4 Nov); B number register; report as Claude Doc; deck as Claude Slides; ensemble wording; Team 11; Claude drafts, team edits | Agreed (Henry) |

## 3. Change log entries (CHANGELOG_B.md)

| ID | Commit | What |
| --- | --- | --- |
| B-CR-22 | 60a6c3c | B10 code: e5b/b10.py, e5b/serving.py, tests |
| B-CR-23 | adf23d6 | Out-of-profile 4 SD (B10-D11) |
| B-CR-24 | 058f7d9 | B10 round 1 accepted (Henry for you); tag `e5-B-s10-accepted` on 058f7d9 (5/14) |
| B-CR-25 | aaf6ccd | B11.1 number register `build_evidence_B.py`, `evidence/registry_B.yaml` |
| B-CR-26 | 1e36f0a | B10 round 2: 4/15 (B-G-07), B-G-09 withdrawn; register ids B_4_15 |

## 4. Current B10 evidence

Round 2 clean runs 20261026T024749Z (regression) and 20261026T024858Z (classification) on 1e36f0a, byte-identical on
a second run, 13 + 15 checks pass. Round 1 runs are listed as superseded in EVIDENCE.md. The tag `e5-B-s10-accepted`
stays on round 1 (tags are never moved); round 2 gets `e5-B-s10-accepted-r2` once approved.

## 5. Open for you

1. Approve B10 round 2 (then tag `e5-B-s10-accepted-r2`).
2. Re-confirm the alert volumes at 4/15 (B10-D2): see b10_review.md point 3.
3. Note B11-D1: report and deck drafts before migration and reproduction (s10-D3 deviation).
4. Migration (README §12) is still yours to order; the app, its URL and screenshots wait for it.
5. The reproduction check should compare predictions exactly and refitted results within a tolerance (B10-D10).
