"""Audit the report doc and the deck against Pipeline B's repository results (B11).

    python pipeline_b/audit_deliverables_B.py --doc <exported report.md> --deck <dir with project/slides/*.html>
                                              --doc-assets <dir> --deck-assets <dir> [--out <json>]

Checks, each PASS/FAIL with detail:
1. charts: every chart in the doc and deck (figure_map.json) is byte-identical to its register figure, which is
   byte-identical to the stage output listed in that run's manifest;
2. deck text: every live slide equals a fresh fill of its template from numbers_B.json;
3. report numbers: every number in the live doc appears in a fresh fill of the report sources (evidence IDs,
   figure numbers and dates are allowed);
4. independent recomputation: headline numbers recomputed from T1's saved test predictions, not via the register;
5. alignment: register ids used in both report and deck; numbers on the deck that the report does not carry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

import build_evidence_B as reg

B = reg.B_ROOT
DELIV = B / "deliverables"
ID_PAT = re.compile(r"\b(?:B\d+(?:\.\d+|\.[A-Z])?|T1\.\d|DS\.\d|B-G-\d+|B-C\d+|B10-D\d+|G-\d+|CR-\d+|s0\d)\b")
NUM_PAT = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?(?:e-?\d+)?%?")


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _tokens(text: str) -> set[str]:
    text = re.sub(r"&#\d+;", " ", text.replace("\\", ""))   # export's image placeholders (&#91;image: …])
    text = ID_PAT.sub(" ", text)
    return {t.rstrip(".,") for t in NUM_PAT.findall(text)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True)
    ap.add_argument("--deck", required=True)
    ap.add_argument("--doc-assets", required=True)
    ap.add_argument("--deck-assets", required=True)
    ap.add_argument("--out", default=str(DELIV / "audit" / "audit_result.json"))
    a = ap.parse_args()
    nums = json.loads((reg.BUILD / "numbers_B.json").read_text(encoding="utf-8"))
    fmap = json.loads((DELIV / "audit" / "figure_map.json").read_text(encoding="utf-8"))
    res = []

    def check(name, ok, detail=""):
        res.append({"check": name, "passed": bool(ok), "detail": detail})

    # 1 charts ------------------------------------------------------------------------------------------
    def chart_ok(asset: Path, fid: str) -> tuple[bool, str]:
        e = nums[fid]
        regfile = B / e["file"]
        if e["source"].startswith("A/"):
            # Pipeline A source (B-G-11, B-G-13): no B manifest; the file must equal its copy at tag e5-A-frozen
            try:
                src, _ = reg.verify_a_source(e["source"])
            except ValueError as err:
                return False, f"{asset.name} -> {fid} -> {err}"
            ok = asset.exists() and _sha(asset) == _sha(regfile) == _sha(src)
            return ok, f"{asset.name} -> {fid} -> {e['source']} ({e['run_id']})"
        if e["source"].startswith("BIZ/"):
            # business context (B-CR-41): no stage manifest; the file must match business_context's manifest
            try:
                src, _ = reg.verify_biz_source(e["source"])
            except ValueError as err:
                return False, f"{asset.name} -> {fid} -> {err}"
            ok = asset.exists() and _sha(asset) == _sha(regfile) == _sha(src)
            return ok, f"{asset.name} -> {fid} -> {e['source']} ({e['run_id']})"
        src = reg.STAGES / e["source"]
        stage, task = Path(e["source"]).parts[:2]
        man = json.loads((reg.STAGES / stage / task / "outputs" / "_manifest.json").read_text())
        mrel = src.relative_to(B.parents[2]).as_posix()
        ok = asset.exists() and _sha(asset) == _sha(regfile) == _sha(src) == man["outputs"].get(mrel)
        return ok, f"{asset.name} -> {fid} -> {e['source']} ({e['run_id']})"
    bad = [d for n, m in fmap["doc"].items() for ok, d in [chart_ok(Path(a.doc_assets) / f"{m['asset']}.png", m["register"])] if not ok]
    # the expected count comes from the map, and the doc's figure captions must number exactly the map's keys
    captions = sorted(int(n) for n in re.findall(r"^\*Figure (\d+)\.", Path(a.doc).read_text(encoding="utf-8"), re.M))
    unmapped = sorted(set(captions) ^ {int(n) for n in fmap["doc"]})
    check(f"report charts: the doc's {len(captions)} figure captions match the map's {len(fmap['doc'])} entries, and each "
          "chart equals its register figure and the stage output in its manifest",
          not bad and not unmapped and len(captions) == len(fmap["doc"]),
          "; ".join(bad + ([f"figure numbers in only one of doc and map: {unmapped}"] if unmapped else [])))
    deck_srcs = set()
    for f in sorted(Path(a.deck, "project", "slides").glob("*.html")):
        deck_srcs |= set(re.findall(r'src="/_blob/([0-9a-f]{32})"', f.read_text(encoding="utf-8")))
    bad = [d for aid, fid in fmap["deck"].items() for ok, d in [chart_ok(Path(a.deck_assets) / f"{aid}.png", fid)] if not ok]
    check("deck charts: every <img> on a slide is mapped, and equals its register figure and stage output",
          not bad and deck_srcs == set(fmap["deck"]), "; ".join(bad) or f"{len(deck_srcs)} images")

    # 2 deck text ---------------------------------------------------------------------------------------
    diff = []
    for t in sorted((DELIV / "deck" / "project" / "slides").glob("*.html")):
        live = Path(a.deck, "project", "slides", t.name)
        if not live.exists() or live.read_text(encoding="utf-8").strip() != reg.fill(t.read_text(encoding="utf-8"), nums).strip():
            diff.append(t.name)
    check("deck slides: each live slide equals a fresh fill of its template (no hand-typed or stale number)", not diff, ", ".join(diff))

    # 3 report numbers ----------------------------------------------------------------------------------
    filled = "\n".join(reg.fill(p.read_text(encoding="utf-8"), nums) for p in sorted((DELIV / "report").glob("*.md")))
    doc = Path(a.doc).read_text(encoding="utf-8")
    doc_body = re.sub(r"\*Figure \d+\.", "", doc)          # figure numbers
    doc_body = re.sub(r"^Oct \d+, \d{4}.*$", "", doc_body, flags=re.M)   # as-of date line
    extra = sorted(_tokens(doc_body) - _tokens(filled))
    check("report numbers: every number in the live doc is in the filled report sources", not extra, ", ".join(extra))
    missing = sorted(_tokens(filled) - _tokens(doc_body))
    check("report completeness: every number in the filled sources appears in the live doc", not missing, ", ".join(missing))

    def lines(t):
        t = t.replace("\\", "").replace("’", "'").replace("“", '"').replace("”", '"')
        out = []
        for ln in t.splitlines():
            ln = re.sub(r"\s+", " ", ln).strip()
            if ln and not ln.startswith(("&#91;image", "*Figure")) and not re.match(r"^\|( ?-+ ?\|)+$", ln):
                out.append(ln.strip("*"))
        return out
    src_lines, doc_lines = lines(filled), lines(doc)
    head = doc_lines[:3]   # title, as-of line, review note: written in the doc only, no results
    extra_lines = [ln for ln in doc_lines[3:] if ln not in set(src_lines)]
    check("report text: the live doc's body equals the filled sources line for line (beyond its title, date and review note)",
          not extra_lines and not [ln for ln in src_lines if ln not in set(doc_lines)],
          "; ".join(extra_lines)[:500] or "header kept: " + " / ".join(head))

    # 4 independent recomputation from T1's saved predictions ----------------------------------------------
    rec = []
    pr = pd.read_csv(reg.STAGES / "t1_joint_test/regression/outputs/predictions_test.csv.gz")
    g = lambda d, m, r: d[(d.model == m) & (d.rows == r)]
    b, ab = g(pr, "B frozen", "B test rows"), g(pr, "A frozen", "B test rows")
    mae_b, mae_a = np.mean(np.abs(b.y_pred - b.y_true)), np.mean(np.abs(ab.y_pred - ab.y_true))
    rec += [("B9.reg.test_mae_B", mae_b), ("B9.reg.test_mae_A_on_B", mae_a),
            ("B9.reg.test_within3_B", np.mean(np.abs(b.y_pred - b.y_true) <= 3)), ("T1.reg.test_rows_B", len(b))]
    pc = pd.read_csv(reg.STAGES / "t1_joint_test/classification/outputs/predictions_test.csv.gz")
    cb, cab = g(pc, "B frozen", "B test rows"), g(pc, "A frozen", "B test rows")
    rec += [("B9.clf.test_ap_B", average_precision_score(cb.y_true, cb.y_pred)),
            ("B9.clf.test_ap_A_on_B", average_precision_score(cab.y_true, cab.y_pred)),
            ("T1.clf.test_rows_B", len(cb)), ("T1.clf.test_detractors_B", int(cb.y_true.sum()))]
    for name, t in (("B_1_6", 1 / 6), ("B_4_15", 4 / 15)):
        f = cb.y_pred >= t
        tp = int((f & (cb.y_true == 1)).sum())
        rec += [(f"B10.clf.{name}_test_precision", tp / f.sum()), (f"B10.clf.{name}_test_recall", tp / cb.y_true.sum())]
    bad = []
    for k, v in rec:
        ref = nums[k]["value"]
        if not np.isclose(float(v), float(ref), rtol=0, atol=1e-9):
            bad.append(f"{k}: recomputed {v} vs register {ref}")
    check("independent recomputation from T1's saved predictions matches the register (" + str(len(rec)) + " numbers)", not bad, "; ".join(bad))

    # 5 alignment ------------------------------------------------------------------------------------------
    used = lambda paths: {m for p in paths for m in reg.PLACEHOLDER.findall(p.read_text(encoding="utf-8"))}
    rep_ids = used(sorted((DELIV / "report").glob("*.md")))
    deck_ids = used(sorted((DELIV / "deck" / "project" / "slides").glob("*.html")))
    only_deck = sorted(deck_ids - rep_ids)
    check("alignment: every number on the deck is also in the report (same register id, same text)", not only_deck, ", ".join(only_deck))
    check("alignment: deck and report share the headline ids", {"B9.reg.test_mae_B", "B9.clf.test_ap_B", "B10.clf.B_4_15_test_alerts_day"} <= rep_ids & deck_ids)

    out = {"checks": res, "passed": all(r["passed"] for r in res), "doc_sha256": _sha(a.doc),
           "deck_slides": {p.name: _sha(p) for p in sorted(Path(a.deck, "project", "slides").glob("*.html"))}}
    Path(a.out).write_text(json.dumps(out, indent=2), encoding="utf-8", newline="\n")
    for r in res:
        print("PASS" if r["passed"] else "FAIL", "|", r["check"], "|", r["detail"][:300])
    return 0 if out["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
