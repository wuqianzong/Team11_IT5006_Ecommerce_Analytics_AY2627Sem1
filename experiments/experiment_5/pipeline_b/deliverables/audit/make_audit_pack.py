"""Audit pack for a third-party review: the final report, the revised Milestone 2 report, the deck and the dashboard
as standalone Markdown, each filled from the number register, its figures copied beside it, and a data-source index.

    cd experiments/experiment_5/pipeline_b
    python deliverables/audit/make_audit_pack.py <out dir>

Needs deliverables/audit/requirements-audit.txt. Reads only committed sources and the register build
(evidence/build/). deliverables/exports/ is local, not committed."""
import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

from bs4 import BeautifulSoup   # checked before any output is written (requirements-audit.txt)
sys.path.insert(0, '.')
import build_evidence_B as reg
OUT = Path(sys.argv[1]); (OUT / "figures").mkdir(parents=True, exist_ok=True)
nums = json.load(open('evidence/build/numbers_B.json', encoding='utf-8'))
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
TODAY = __import__('datetime').date.today().isoformat()
PH = re.compile(r"\{\{\s*(table:)?([A-Za-z0-9_.\-]+)\s*\}\}")

def src_path(s):
    head = Path(s).parts[0]
    if head == "A":
        return "experiments/experiment_5/stages/" + "/".join(Path(s).parts[1:]) + " (Pipeline A, tag e5-A-frozen)"
    if head == "BIZ":
        return "experiments/experiment_5/pipeline_b/deliverables/business_context/outputs/" + "/".join(Path(s).parts[1:])
    if head == "DECK":
        return "experiments/experiment_5/pipeline_b/deliverables/deck/renders/outputs/" + "/".join(Path(s).parts[1:])
    if head == "M2A":
        return "experiments/experiment_5/pipeline_b/deliverables/m2_report/a_interpretation/outputs/" + "/".join(Path(s).parts[1:])
    return "experiments/experiment_5/pipeline_b/stages/" + s

def pack(name, folder, title, scope):
    out, used, n = [], [], 0
    for f in sorted(Path(folder).glob("*.md")):
        text = f.read_text(encoding="utf-8").replace("\r\n", "\n")
        for m in PH.finditer(text):
            used.append((f.stem, m.group(2), "table" if m.group(1) else "number"))
        for line in reg.fill(text, nums).split("\n"):
            if line.startswith("*Figure"):
                ids = re.findall(r"\((F\.[A-Za-z0-9_.]+)\)", line)
                for i in ids:
                    n += 1
                    fn = f"{i}.png"
                    shutil.copyfile(nums[i]["file"], OUT / "figures" / fn)
                    used.append((f.stem, i, "figure"))
                    out += [f"![{nums[i].get('caption') or i}](figures/{fn})", ""]
                if len(ids) == 1:
                    out.append(line.replace("*Figure:", f"*Figure {n}.", 1))
                else:
                    body = line[len("*Figure: "):].rstrip("*").rstrip(".")
                    parts = [p.strip() for p in re.split(r"(?<=\))\s*(?:and|;)\s*", body)]
                    tail = ""
                    if not parts[-1].endswith(")"):
                        parts[-1], tail = parts[-1].rsplit(")", 1)[0] + ")", parts[-1].rsplit(")", 1)[1]
                    for k, p in enumerate(parts):
                        if k and p[:1].islower():
                            p = (parts[0].split(", lead time")[0] + ", " + p) if p.startswith("detractor alert") else p[0].upper() + p[1:]
                        out += ([""] if k else []) + [f"*Figure {n - len(ids) + 1 + k}. {p}{tail}.*"]
            elif line.startswith("*Screenshots"):
                for k in re.findall(r"\(S\.([A-Za-z0-9_]+)\)", line):
                    shutil.copyfile(f"deliverables/dashboard/app/screenshots/2026-10-29/{k}.png", OUT / "figures" / f"S.{k}.png")
                    out += [f"![App screenshot](figures/S.{k}.png)", ""]
                    used.append((f.stem, f"S.{k}", "screenshot"))
                out.append(line)
            else:
                out.append(line)
        out.append("")
    seen, rows, shots = set(), [], []
    for sec, i, kind in used:
        if i in seen:
            continue
        seen.add(i)
        if kind == "screenshot":
            f = Path(f"deliverables/dashboard/app/screenshots/2026-10-29/{i[2:]}.png")
            shots.append(f"| {i} | experiments/experiment_5/pipeline_b/{f.as_posix()} | 2026-10-29 | `{hashlib.sha256(f.read_bytes()).hexdigest()}` | {sec} |")
            continue
        e = nums[i]
        val = e.get("text", "") if e["kind"] == "number" else (f"{e.get('rows')} rows" if e["kind"] == "table" else "chart")
        rows.append(f"| {i} | {e['kind']} | {str(val).replace('|', '/')} | {src_path(e['source'])} | {e['run_id']} | {e['evidence']} | {sec} |")
    head = [f"# {title}: audit copy", "",
            f"Generated on {TODAY} from repository commit `{commit}` (branch `e5/deliverables-henry`, "
            "https://github.com/wuqianzong/Team11_IT5006_Ecommerce_Analytics_AY2627Sem1).", "",
            "## How this copy was made", "",
            f"- **Scope.** {scope}",
            "- **Text.** The report sources (`" + folder + "/*.md`) with every `{{id}}` placeholder filled from the number register "
            "(`experiments/experiment_5/pipeline_b/evidence/registry_B.yaml`, built into `evidence/build/numbers_B.json`). No number in the text was typed by hand except where noted below.",
            "- **Register rule.** An item is built only if its source file passes a check: a Pipeline B stage file must match the sha256 in its stage's `_manifest.json` for the run listed as Current in `pipeline_b/EVIDENCE.md`; a Pipeline A file must equal its copy at git tag `e5-A-frozen`; a business-context or Milestone 2 analysis file must match the sha256 in its folder's `_manifest.json`, together with its input data.",
            "- **Figures.** Copied byte for byte from the register build (`evidence/build/figures/`) into `figures/`; each is the stored stage output named in the index below.",
            "- **Data.** Olist Brazilian E-Commerce Public Dataset (nine CSV tables). The business-context figures use the dashboard's consolidated copy (`data/business/dashboard/smartcommerce_consolidated.csv`), March 2017 to April 2018 only, before the test period.",
            "- **Typed numbers.** Counts of features and model settings written in the text (for example the 24 checkout predictors, grid ranges, the 1/6 threshold) were checked against the stored outputs but are not register items.",
            "- **How to re-check.** `python experiments/experiment_5/pipeline_b/build_evidence_B.py build` rebuilds every item from the stored outputs and fails on any checksum mismatch; `build_evidence_B.py fill <source.md> <out.md>` reproduces the filled text.",
            "", "---", ""]
    idx = ["", "---", "", "## Data-source index", "",
           "Every register item the report uses, in order of first use: the value as printed, the stored file it is read from, the run that produced the file, and the evidence ID in that stage's documentation.", "",
           "| Item | Kind | Value in the report | Source file | Run | Evidence ID | First used in |", "| --- | --- | --- | --- | --- | --- | --- |"] + rows
    if shots:
        idx += ["", "## Unregistered app captures", "",
                "Screenshots of the dashboard, shown in the appendix to illustrate the app. They are not register items and carry no number the text relies on; each is identified by its stored file, capture date and SHA-256.", "",
                "| Item | Stored file | Captured | SHA-256 | Used in |", "| --- | --- | --- | --- | --- |"] + shots
    (OUT / name).write_text("\n".join(head + out + idx) + "\n", encoding="utf-8", newline="\n")
    print(name, len(rows), "register items,", len(shots), "captures,", n, "figures")

pack("milestone3_final_report_audit.md", "deliverables/report", "Final report (Milestone 3)",
     "The final report: Pipeline B, the delivered model, compared with Pipeline A on the same test orders.")
pack("milestone2_report_audit.md", "deliverables/m2_report", "Revised Phase 2 report (Milestone 2, Pipeline A)",
     "The revised Phase 2 technical report, built only on Pipeline A, the baseline.")


# ---------------------------------------------------------------------------------------------------------------

DECK_URL = "https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc"


def _md_table(tbl):
    rows = [[c.get_text(" ", strip=True).replace("|", "/") for c in tr.find_all(["th", "td"])] for tr in tbl.find_all("tr")]
    if not rows:
        return []
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return (["| " + " | ".join(rows[0]) + " |", "| " + " | ".join("---" for _ in rows[0]) + " |"]
            + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def deck_pack():
    fmap = json.loads(Path("deliverables/audit/figure_map.json").read_text(encoding="utf-8"))["deck"]
    order = json.loads(Path("deliverables/deck/project/deck.json").read_text(encoding="utf-8"))["order"]
    out, used, imgs = [], [], []
    for k, sid in enumerate(order, 1):
        src = Path(f"deliverables/deck/project/slides/{sid}.html").read_text(encoding="utf-8")
        for m in PH.finditer(src):
            used.append((sid, m.group(2), "table" if m.group(1) else "number"))
        sec = BeautifulSoup(reg.fill(src, nums), "html.parser").find("section")
        notes = sec.find("aside")
        notes_text = notes.get_text(" ", strip=True) if notes else ""
        if notes:
            notes.decompose()
        footer = [x for x in sec.find_all("p", recursive=False) if "position:absolute" in (x.get("style") or "")]
        foot = footer[0].get_text(" ", strip=True) if footer else ""
        for x in footer:
            x.decompose()
        out += [f"## Slide {k}: {sid}", ""]
        for el in sec.find_all(["h1", "h2", "p", "table", "img"]):
            if el.name != "table" and el.find_parent("table") is not None:
                continue
            if el.name in ("h1", "h2"):
                out += [f"### {el.get_text(' ', strip=True)}", ""]
            elif el.name == "table":
                out += _md_table(el) + [""]
            elif el.name == "img":
                aid = el["src"].rsplit("/", 1)[-1]
                rid = fmap.get(aid)
                if rid:
                    shutil.copyfile(nums[rid]["file"], OUT / "figures" / f"{rid}.png")
                    used.append((sid, rid, "figure"))
                    imgs.append(rid)
                    out += [f"![{el.get('alt', '')}](figures/{rid}.png)", "", f"*Image: {el.get('alt', '')} (register {rid}).*", ""]
                else:
                    out += [f"*Unmapped image {aid}.*", ""]
            elif el.find_parent("p") is None:
                txt = el.get_text(" ", strip=True)
                if txt:
                    out += [txt, ""]
        if foot:
            out += [f"*Footer: {foot}*", ""]
        if notes_text:
            out += [f"> **Speaker notes.** {notes_text}", ""]
    seen, rows = set(), []
    for sid, i, kind in used:
        if i in seen:
            continue
        seen.add(i)
        e = nums[i]
        val = e.get("text", "") if e["kind"] == "number" else (f"{e.get('rows')} rows" if e["kind"] == "table" else "chart")
        rows.append(f"| {i} | {e['kind']} | {str(val).replace('|', '/')} | {src_path(e['source'])} | {e['run_id']} | {e['evidence']} | {sid} |")
    head = ["# Deck v2 (Milestone 3 presentation): audit copy", "",
            f"Generated on {TODAY} from repository commit `{commit}`; live deck {DECK_URL} (version 36).", "",
            "## How this copy was made", "",
            "- **Source.** The slide templates in `experiments/experiment_5/pipeline_b/deliverables/deck/project/slides/*.html`, in the order of `deck.json`, with every `{{id}}` filled from the number register. The deliverables audit checks that each live slide equals a fresh fill of its template.",
            "- **Images.** Each slide image is mapped to a register figure by `deliverables/audit/figure_map.json` (deck section) and copied here byte for byte. Fourteen of the twenty are presentation renders (register ids ending `.deck`, B-CR-43): the chart redrawn from its stored data file at the slide box size; the other six are the stored originals.",
            "- **Per slide.** Eyebrow, title, tables and cards as on the slide, then the footer and the speaker notes (10-minute script).",
            "", "---", ""]
    idx = ["", "---", "", "## Data-source index", "", "Every register item the deck uses, in order of first use.", "",
           "| Item | Kind | Value on the slide | Source file | Run | Evidence ID | First used on |",
           "| --- | --- | --- | --- | --- | --- | --- |"] + rows
    (OUT / "deck_v2_audit.md").write_text("\n".join(head + out + idx) + "\n", encoding="utf-8", newline="\n")
    print("deck_v2_audit.md", len(rows), "register items,", len(imgs), "images")


ROLES = {"Henry": "report owner", "Solomon": "dashboard developer", "Benson": "experiment lead"}


def dashboard_pack():
    app = Path("deliverables/dashboard/app")
    shots = sorted((app / "screenshots/2026-10-30").glob("*.png"))
    demote = lambda md: re.sub(r"(?m)^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", md)  # noqa: E731
    rows = []
    body = ["# Dashboard (Streamlit app, plan revision 2.3): audit copy", "",
            f"Generated on {TODAY} from repository commit `{commit}`.", "",
            "## How this copy was made", "",
            "- **App.** `experiments/experiment_5/pipeline_b/deliverables/dashboard/app/` (entry `app.py`, panels in `dashboard_core/`, tests in `tests/`). Four tabs: Business overview, Delivery lead time, Detractor risk at handover, ML deployment.",
            "- **What it reads.** Only committed files: the dashboard's business data (`data/business/dashboard/`), stored Pipeline B stage outputs (b09, b10, b12, T1) and the frozen model bundles in T1. No model is fitted and no test label is read to choose a model or threshold (sources document below).",
            "- **Tests.** `python -m pytest -q` in the app folder, with its own environment (`requirements.txt`): 20 passed on this commit.",
            "- **Hosting.** Not yet hosted; planned as a Streamlit Community Cloud app on the merged branch. Locally: `streamlit run app.py` from the app folder.",
            "- **Names.** The three project documents below record who decided what; in this copy each team member's name is replaced by their role (report owner, dashboard developer, experiment lead).",
            "- **Screenshots.** Captured 2026-10-30 at 1600 x 1000 with headless Edge, after revision 2.3 (old score pointers 2.8 and 3.9 removed, tab 4 renamed ML deployment, promise buffer opening on Pipeline B). The final report's appendix uses two captures from the 2026-10-29 set (05 and 06), byte-identical to 05 and 06 here.",
            "- **Environment.** The audit, the dashboard tests and this pack need `deliverables/audit/requirements-audit.txt` on top of the app's `requirements.txt`.",
            "", "---", "", "## Screenshots", ""]
    for s in shots:
        shutil.copyfile(s, OUT / "figures" / f"dashboard_{s.name}")
        rows.append(f"| {s.name} | experiments/experiment_5/pipeline_b/deliverables/dashboard/app/screenshots/2026-10-30/{s.name} | `{hashlib.sha256(s.read_bytes()).hexdigest()}` |")
        body += [f"![{s.stem}](figures/dashboard_{s.name})", "", f"*{s.stem}*", ""]
    body += ["| Screenshot | Stored file | SHA-256 |", "| --- | --- | --- |"] + rows
    for title, f in (("Dashboard plan (panels, questions and sources)", "deliverables/dashboard/DASHBOARD_PLAN.md"),
                     ("Data and model sources", "deliverables/dashboard/app/DATA_AND_MODEL_SOURCES.md"),
                     ("App README", "deliverables/dashboard/app/README.md")):
        text = Path(f).read_text(encoding="utf-8")
        for name, role in ROLES.items():
            text = re.sub(r"\b" + name + r"'s\b", f"the {role}'s", text)
            text = re.sub(r"\b" + name + r"\b", f"the {role}", text)
        body += ["", "---", "", f"## {title}", "", demote(text)]
    (OUT / "dashboard_audit.md").write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
    print("dashboard_audit.md", len(shots), "screenshots")


deck_pack()
dashboard_pack()
