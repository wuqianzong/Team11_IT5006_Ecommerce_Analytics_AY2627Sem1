"""Filled report .docx -> same .docx with Figures 20-23 as half-width report renders, each pair in a borderless 2x2 table
(pictures in row 1, each caption under its picture). usage: pair_fill.py <in.docx> <figures dir> <out.docx>"""
import re
import struct
import sys
import zipfile
from pathlib import Path

src, figs, dst = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
zin = zipfile.ZipFile(src)
doc = zin.read("word/document.xml").decode()
rels = zin.read("word/_rels/document.xml.rels").decode()
PAIRS = [(("Permutation importance, B regression (test rows)", "F.reg.importance"),
          ("Permutation importance, B classification (test rows)", "F.clf.importance")),
         (("B&apos;s regression coefficients", "F.reg.coefficients"),
          ("B&apos;s classification odds ratios", "F.clf.coefficients"))]
W_EMU = int(3.3 * 914400)
SUFFIX = "(half-width report render)"
media = {}
paras = list(re.finditer(r"<w:p[ >](?:(?!<w:p[ >]).)*?</w:p>", doc, re.S))


def find(alt):
    # the doc's alt text may already carry the render suffix (review doc since v2.3 rev 55)
    return next(k for k, m in enumerate(paras) if re.search(rf'descr="{re.escape(alt)}( {re.escape(SUFFIX)})?"', m.group(0)))


def picture(p, alt, rid):
    png = (figs / f"{rid}.report.png").read_bytes()
    w, h = struct.unpack(">II", png[16:24])
    emb = re.search(r'r:embed="([^"]+)"', p).group(1)
    target = re.search(rf'Id="{emb}"[^>]*Target="([^"]+)"', rels).group(1)
    media["word/" + target] = png
    p = re.sub(r'cx="\d+" cy="\d+"', f'cx="{W_EMU}" cy="{int(W_EMU * h / w)}"', p)
    return re.sub(rf'descr="{re.escape(alt)}( {re.escape(SUFFIX)})?"', f'descr="{alt} {SUFFIX}"', p)


def cell(p):
    return f'<w:tc><w:tcPr><w:tcW w:w="2500" w:type="pct"/></w:tcPr>{p}</w:tc>'


NONE = "".join(f'<w:{s} w:val="nil"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
TBL = ('<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:jc w:val="center"/><w:tblBorders>' + NONE +
       '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/>'
       '<w:right w:w="0" w:type="dxa"/></w:tblCellMar><w:tblLook w:val="0000"/></w:tblPr>'
       '<w:tblGrid><w:gridCol w:w="4819"/><w:gridCol w:w="4819"/></w:tblGrid>'
       '<w:tr><w:trPr><w:cantSplit/></w:trPr>{}{}</w:tr><w:tr><w:trPr><w:cantSplit/></w:trPr>{}{}</w:tr></w:tbl>')
edits = []
for (alt_a, id_a), (alt_b, id_b) in PAIRS:
    ka, kb = find(alt_a), find(alt_b)
    ca, cb = kb + 1, kb + 2
    assert kb == ka + 1, (ka, kb)
    pa, pb = picture(paras[ka].group(0), alt_a, id_a), picture(paras[kb].group(0), alt_b, id_b)
    capa, capb = paras[ca].group(0), paras[cb].group(0)
    assert f"({id_a}" in capa and f"({id_b}" in capb, (capa, capb)   # "(F.x)" or "(F.x.report)"
    capa, capb = capa.replace(f"({id_a})", f"({id_a}.report)"), capb.replace(f"({id_b})", f"({id_b}.report)")
    edits.append((paras[ka].start(), paras[cb].end(), TBL.format(cell(pa), cell(pb), cell(capa), cell(capb))))
for s, e, new in sorted(edits, reverse=True):
    doc = doc[:s] + new + doc[e:]
zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for i in zin.infolist():
    data = {"word/document.xml": doc.encode()}.get(i.filename) or media.get(i.filename) or zin.read(i.filename)
    zo.writestr(i, data)
zo.close()
print("pairs", len(edits), "media replaced", len(media), "drawings", doc.count("<w:drawing>"))
