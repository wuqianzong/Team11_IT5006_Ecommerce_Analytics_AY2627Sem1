# Report Word copy build (v2.3)

Turns a Word export of the review doc into the submission .docx. Until 2026-11-03 these four files lived only in
Henry's session scratchpads (named `export_fill.py` in earlier WORKLOG entries); copied here with the absolute paths
made relative (HS-02). Run from `experiments/experiment_5/`.

| File | What it does |
| --- | --- |
| `docx_fill.py` | The doc's Word export leaves some pictures out (`[image: …]` paragraphs); inserts them from the local PNGs by position in the doc's picture order |
| `report_v2_3_figs.tsv` | Picture order of report v2.3: number, PNG path (relative to `experiments/experiment_5/`), caption. Add, drop or reorder rows when the doc's pictures change |
| `pair_fill.py` | Figures 20–23: swaps in the half-width renders (`*.report.png`) and puts each pair in a borderless 2×2 table (B-CR-52) |
| `format_submission_docx.ps1` | Word (COM, Windows only): A4, 2 cm margins, Times New Roman 12 pt, chart widths, cover page; prints the body page range. The body must end on or before page 20 |

```
.venv/Scripts/python.exe pipeline_b/deliverables/report/build/docx_fill.py <export.docx> pipeline_b/deliverables/report/build/report_v2_3_figs.tsv <filled.docx>
.venv/Scripts/python.exe pipeline_b/deliverables/report/build/pair_fill.py <filled.docx> pipeline_b/evidence/build/figures <paired.docx>
powershell -File pipeline_b/deliverables/report/build/format_submission_docx.ps1 -Src <paired.docx> -Docx pipeline_b/deliverables/exports/<date>/Team11_final_report_v2.3.docx [-Pdf <out.pdf>]
```

`<export.docx>` is the review doc's Word export, downloaded in a browser (not returned inline). Checked on
2026-11-03: rev 53's export gives the same `document.xml` as the filled copy used for the v2.3 export, and
`pair_fill.py` reports 2 pairs, 4 pictures replaced, 31 pictures.
