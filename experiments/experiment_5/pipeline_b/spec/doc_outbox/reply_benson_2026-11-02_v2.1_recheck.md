# Reply to Benson: recheck of report and deck v2.1 (2026-11-02)

Hi Benson, thank you for the recheck. Every point checked out against the repository. The fixes are B-CR-48 on
`e5/validation-fixes-henry`. The triage is in `deliverables/audit/runs/2026-11-02_benson_v2.1_recheck.md` and the
status of each point in `deliverables/audit/findings.yaml` (T-26 to T-31). T-13 to T-20, T-22 and T-23 are now
`Verified` by your recheck.

Done on our side: deck v2.1 is at version 43 with 16 slides. The deliverables audit passes 9/9 on the refreshed
committed inputs (report rev 45, deck version 43, 22 deck images), and the tests pass (36). The deck copy is
`deliverables/exports/2026-11-02/Team11_final_deck_v2.1.pptx`. The report did not change. We are still waiting for
your check before merging into `milestone-3`.

## Please note first: report text goes through the sources (T-31)

Our first reply asked you to type the API URL into the review doc. That was wrong. The audit compares the doc with a
fresh fill of `deliverables/report/*.md`, line by line and number by number, so text typed only into the doc fails
it. For the §8 API URL (T-12) and your Appendix N (T-21), either change `08_deployment.md` and `12_appendices.md`
and then the doc in the same words, or send us the text and we add it. The first reply now says so too.

## Your findings and what changed

| Your point | Verdict | What changed |
| --- | --- | --- |
| Slide 12 confusion chart doubles every count (T-26) | Correct, and your cause is right: `doc_support.py` found b08's `all` rows only for an object-dtype fold column, and pandas 3.0.1 reads it as str | `pooled_confusion()` compares the fold as text, with tests. The deck render now reads b08's `confusion_comparison.csv` pooled rows directly: A 38,805 / 4,410 / 5,483 / 1,517 and B 39,099 / 4,116 / 5,251 / 1,749, your figures. Only that render changed; the other 17 are byte-identical. Slide 12 shows the new chart |
| No app screenshots, URL or GitHub link (T-28) | Correct | New slide 16, "The same frozen models, live for operations": the two appendix L screenshots, the app URL and the repository link. It also covers us if the live demo is slow. Footers now read n/16. The screenshots are registered (S.05, S.06, source `SHOT/`, manifest written by `record_screenshots.py`), so the audit traces every image on the deck |
| Slide 11 footer (T-29) | Correct, and §5.1 (the history chart) was missing too | "Report sections 3, 5.1, 5.2, 6.2–6.4" |
| Slide 9 wording (T-30) | Consistent with the chart, as you said | No change |
| §8 placeholder (T-12), Appendix N (T-21) | Open, yours | Through the sources, as above. If there is no API URL by 6 Nov, we suggest deleting the clause |
| Page count | Waived (B-G-17) | The team checks it on the final PDF |

## For you: doc_support rerun (T-27)

The committed doc_support outputs `r06_confusion.csv` and `r06_confusion.png` still hold the doubled counts. The code
is fixed, but I could not rerun the stage here: the 25 Oct run used Python 3.13.9 and this machine has 3.13.7. A
rerun changed other doc_support outputs in the last digits and in row order, and failed the check "A's sigmoid refit
per fold reproduces A's s08 calibration AP", so I reverted it. Neither the report nor the deck uses these two files.
Could you rerun doc_support (both tasks) in the run's environment, check that every other output is byte-identical,
and record it? If it does not reproduce there either, we will decide together whether to leave it as a recorded,
unused output.

## For your agent

- Under pandas 3, a CSV column that mixes numbers and text (here `fold`: 1–5 and `all`) reads as `str`, not
  `object`. Checks like `dtype == object` silently fail. Compare as text (`astype(str)`) instead. This is the second
  pandas-3 string-dtype bug after the name stripping (T-01).
- Any image on a slide must trace to a register item backed by a manifest. Screenshots now have one (`SHOT/`). A new
  screenshot means rerunning `record_screenshots.py <folder>` and adding a register row.
