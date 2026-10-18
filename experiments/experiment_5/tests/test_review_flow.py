"""Outputs with solution-ID tags, manifests, review packs and the run gate."""
import json

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")


def _stage_run(e5, round_=1, value=1):
    import matplotlib.pyplot as plt
    from e5lib.outputs import Writer
    w = Writer("s02_data", "common")
    w.table("exclusions", pd.DataFrame({"rule": ["2.9"], "n": [value]}), ids=("2.8", "2.9"))
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, value])
    w.figure("structure", fig, pd.DataFrame({"x": [1, 2], "y": [3, value]}), ids=("2.12",))
    w.check("rows match", True, ids=("2.4",), detail="orders in = rows out")
    w.check("no test leakage", value < 5, ids=("2.7",))
    w.explain("2.9", expectation="a few extreme lead times", observation=f"{value} removed",
              conclusion="threshold applied", label="observation")
    w.deviation("2.3", "IBGE archive not available; centroid filter skipped")
    w.decision("outlier threshold", rule="max(100, mean+12sd)", candidates=["rule"], chosen="rule",
               files=["exclusions.csv"], ids=("2.9",))
    return w.finish(seed=42)


def test_writer_tags_and_manifest(e5):
    from e5lib import manifest
    path = _stage_run(e5)
    m = json.loads(path.read_text(encoding="utf-8"))
    assert m["node"] == "s02_data/common" and m["seed"] == 42
    index = json.loads((path.parent / "_evidence_index.json").read_text(encoding="utf-8"))
    assert index["files"]["figures/structure.png"]["ids"] == ["2.12"]
    assert manifest.status("s02_data", "common")[0] == "FRESH"
    (path.parent / "exclusions.csv").write_text("tampered\n", encoding="utf-8", newline="\n")
    assert manifest.status("s02_data", "common")[0] == "STALE"


def test_writer_rejects_untagged_and_bad_shapes(e5):
    from e5lib.outputs import Writer
    w = Writer("s06_training", "regression")
    with pytest.raises(ValueError):
        w.table("x", pd.DataFrame({"a": [1]}), ids=())
    with pytest.raises(ValueError):
        w.metrics_long(pd.DataFrame({"metric": ["mae"]}), ids=("6.4",))


def test_review_pack_coverage_and_rounds(e5):
    from e5lib import review
    _stage_run(e5, value=1)
    md = review.build_pack("s02_data", "common", 1)
    pack = json.loads((md.parent / "pack.json").read_text(encoding="utf-8"))
    status = {r["id"]: r["status"] for r in pack["rows"]}
    checks = {r["id"]: r["checks"] for r in pack["rows"]}
    assert status["2.9"] == "IMPLEMENTED" and status["2.3"] == "DEVIATION" and status["2.1"] == "MISSING"
    assert checks["2.4"] == "PASS"
    assert not pack["ready"]  # MISSING rows block acceptance
    text = md.read_text(encoding="utf-8")
    assert "| [2.1](#card-2-1) | Load | MISSING |" in text and "![figures/structure.png]" in text
    _stage_run(e5, value=7)  # round 2: changed evidence and a failed check
    pack2 = json.loads((review.build_pack("s02_data", "common", 2).parent / "pack.json").read_text(encoding="utf-8"))
    rows2 = {r["id"]: r for r in pack2["rows"]}
    assert rows2["2.9"]["changed"] and not rows2["2.1"]["changed"]
    assert rows2["2.7"]["checks"] == "FAIL"


def test_run_gate_refuses_until_upstream_accepted(e5):
    import run_pipeline as rp
    problems = rp.gate("s03_eda/regression")
    assert any("s02_data/common is TODO" in p for p in problems)
    _stage_run(e5)
    rp.set_status("s01_problem/common", "ACCEPTED")
    rp.set_status("s02_data/common", "ACCEPTED")
    problems = rp.gate("s03_eda/regression")
    assert any("s01_problem/common outputs are MISSING" in p for p in problems)
    assert not any("s02_data/common" in p for p in problems)
    assert rp.get_status("s02_data/common") == "ACCEPTED"
