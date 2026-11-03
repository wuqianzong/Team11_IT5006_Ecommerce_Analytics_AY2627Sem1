"""Docs export result -> .docx with every picture: the pictures the export left out ([image: ...] paragraphs) are
inserted from the local PNGs, matched by position in the doc's picture order (report_v2_3_figs.tsv).
PNG paths in the .tsv are relative to experiments/experiment_5/ unless [root] says otherwise.
usage: docx_fill.py <saved export result> <figs.tsv> <out.docx> [root]
"""
import re
import struct
import sys
import zipfile
from pathlib import Path

res, tsv, dst = sys.argv[1:4]
root = Path(sys.argv[4]) if len(sys.argv) > 4 else Path(__file__).resolve().parents[4]
pngs = [root / line.split(chr(9))[1] for line in open(tsv, encoding="utf-8").read().split(chr(10)) if line.strip()]
zin = zipfile.ZipFile(res)
doc = zin.read("word/document.xml").decode()
rels = zin.read("word/_rels/document.xml.rels").decode()
tpl = re.search(r"<w:drawing>.*?</w:drawing>", doc, re.S).group(0)
items = list(re.finditer(r'<w:drawing>.*?</w:drawing>|<w:r><w:t xml:space="preserve">\[image: ([^<]*)\]</w:t></w:r>', doc, re.S))
assert len(items) == len(pngs), (len(items), len(pngs))
nr = max(int(r) for r in re.findall(r'Id="rId(\d+)"', rels))
nd = max(int(i) for i in re.findall(r'<wp:docPr id="(\d+)"', doc))
nm = len([n for n in zin.namelist() if n.startswith("word/media/")])
out, last, new = [], 0, {}
for k, m in enumerate(items):
    if m.group(0).startswith("<w:drawing>"):
        continue
    nr, nd, nm = nr + 1, nd + 1, nm + 1
    b = open(pngs[k], "rb").read()
    w, h = struct.unpack(">II", b[16:24])
    cx = 6 * 914400
    dr = re.sub(r'r:embed="[^"]+"', f'r:embed="rId{nr}"', tpl)
    dr = re.sub(r'cx="\d+" cy="\d+"', f'cx="{cx}" cy="{int(cx * h / w)}"', dr)
    dr = re.sub(r'(<wp:docPr|<pic:cNvPr) id="\d+"', lambda q: f'{q.group(1)} id="{nd}"', dr)
    dr = re.sub(r'(<wp:docPr|<pic:cNvPr)([^>]*?) descr="[^"]*"', lambda q: f'{q.group(1)}{q.group(2)} descr="{m.group(1)}"', dr)
    out.append(doc[last:m.start()] + f"<w:r>{dr}</w:r>")
    last = m.end()
    rels = rels.replace("</Relationships>", f'<Relationship Id="rId{nr}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{nm}.png"/></Relationships>')
    new[f"word/media/image{nm}.png"] = b
doc = "".join(out) + doc[last:]
zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for i in zin.infolist():
    zo.writestr(i, {"word/document.xml": doc.encode(), "word/_rels/document.xml.rels": rels.encode()}.get(i.filename) or zin.read(i.filename))
for n, b in new.items():
    zo.writestr(n, b)
zo.close()
print("inserted", len(new), "left", doc.count("[image:"), "drawings", doc.count("<w:drawing>"))
