# Reply to Benson: report v2.2 and the merge (2026-11-02)

Hi Benson, thanks. Your three items are done as B-CR-49 and recorded as your decision B-G-18
(`spec/decision_log_B.md`). Findings T-12, T-21 and T-31 are `Fixed`, and T-27 is `Won't fix` by your decision.

| Item | What was done |
| --- | --- |
| T-12 | §8 no longer mentions the prediction API or the placeholder: "The hosted app at … runs the same frozen bundles." Changed in `08_deployment.md`, then in the review doc |
| T-21 | Appendix N added as the last appendix, through `12_appendices.md`, then the review doc and the Word copy. Three wording changes, all to match README Appendix A: "The README's own Appendix A" (our report has its own Appendix A, the validation windows); "matches the release byte for byte, apart from seven files made on another machine that differ only by floating-point noise" (the accepted Mac rerun matched 622 of 629 files; the 7 B10 files differ by at most 2.1e-14); "re-predict them to within 1e-9" (the decision check's parity rule) |
| T-27 | No rerun. `doc_support/classification` `r06_confusion.csv/.png` are recorded as a known, unused output with doubled counts, caused by the pandas-3 dtype bug that is fixed in code. Slide 12 reads b08's pooled rows |

Henry named the report **v2.2** (review doc rev 48). The Word copy is
`deliverables/exports/2026-11-02/Team11_final_report_v2.2.docx`; the deck stays v2.1 (version 43, 16 slides).
The register was rebuilt (375 items), the tests pass and the audit passes 9/9 on the committed inputs.

Merge: `e5/validation-fixes-henry` is merged into `milestone-3`, and `main` is fast-forwarded to it, as you asked.
Your root README, REPRODUCE.md and `scripts/reproduce_experiment5.py` are kept. README Appendix A was checked after
the merge: A.1 to A.3 still describe the repository (no stage output changed after `e5-reproduced`; the doc_support
rerun was reverted). A.4 named the audit run on report revision 73 and deck version 39, so it now names report
v2.2 (revision 48) and deck v2.1 (version 43).
