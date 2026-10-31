"""Paths, protocol ownership and the population guard."""
import json

import pandas as pd
import pytest

from conftest import write_records


def test_containment(e5):
    from e5lib import paths
    with pytest.raises(paths.ContainmentError):
        paths.assert_inside_e5(e5.parent / "outside.txt")
    assert paths.assert_inside_e5(e5 / "stages" / "x.txt")
    with pytest.raises(ValueError):
        paths.review_dir("s02_data", "common", 0)
    with pytest.raises(ValueError):
        paths.stage_dir("s99_unknown", "common")


def test_protocol_ownership(e5):
    from e5lib import protocol
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-05-01"}, stage="s02_data")
    assert protocol.get("data_dependent.test_cutoffs.values.regression") == "2018-05-01"
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-05-01"}, stage="s02_data")  # same value: ok
    with pytest.raises(protocol.ProtocolError):
        protocol.set_data_dependent("test_cutoffs", {"regression": "2018-06-01"}, stage="s02_data")
    with pytest.raises(protocol.ProtocolError):
        protocol.set_data_dependent("selected_set", ["a"], stage="s03_eda")
    with pytest.raises(protocol.ProtocolError):
        protocol.get("no.such.key")


@pytest.fixture()
def records(e5):
    from e5lib import protocol
    rows = [
        {"order_id": f"o{i}", "customer_unique_id": f"c{i}", "purchase_ts": f"2018-0{1 + i // 3}-15",
         "eligible_regression": True, "eligible_classification": i % 2 == 0, "lead_days": 5.0 + i}
        for i in range(9)
    ]
    write_records(e5, rows)
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-03-01", "classification": "2018-03-01"},
                                stage="s02_data")
    return rows


def test_development_population(records):
    from e5lib import data
    dev = data.load("records", "regression", "development", stage="s03_eda")
    assert dev["purchase_ts"].max() < pd.Timestamp("2018-03-01")
    assert len(dev) == 6
    clf = data.load("records", "classification", "development", stage="s03_eda")
    assert clf["eligible_classification"].all()


def test_test_population_is_guarded(records, e5):
    from e5lib import data
    with pytest.raises(data.PopulationError):
        data.load("records", "regression", "test", stage="s06_training")
    with pytest.raises(data.PopulationError):
        data.load("records", "regression", "test", stage="s08_selection")  # before the freeze
    out = e5 / "stages" / "s08_selection" / "regression" / "outputs"
    out.mkdir(parents=True)
    (out / "frozen_recipe.json").write_text(json.dumps({"frozen": True}), encoding="utf-8", newline="\n")
    s05 = e5 / "stages" / "s05_partition" / "regression" / "outputs"
    s05.mkdir(parents=True)
    pd.DataFrame({"order_id": ["o7", "o8"]}).to_csv(s05 / "test_manifest.csv", index=False, lineterminator="\n")
    test = data.load("records", "regression", "test", stage="s08_selection")
    assert sorted(test["order_id"]) == ["o7", "o8"]


def test_other_guards(records):
    from e5lib import data
    with pytest.raises(data.PopulationError):
        data.load_raw("orders", stage="s03_eda")
    with pytest.raises(data.PopulationError):
        data.load("records", "regression", "all", stage="s03_eda")
    with pytest.raises(data.PopulationError):
        data.upstream("s06_training", "regression", "x.csv", stage="s05_partition")
    assert data.load("records", "regression", "all", stage="s05_partition").shape[0] == 9
    assert any(p.name == "records.csv.gz" for p in data.reads())


def test_data_dependent_write_does_not_stale_other_stages(e5):
    import pandas as pd
    from e5lib import manifest, protocol
    from e5lib.outputs import Writer
    w = Writer("s01_problem", "common")
    w.json("protocol_snapshot", protocol.load(), ids=("1.9",))
    w.finish(seed=42)
    assert manifest.status("s01_problem", "common")[0] == "FRESH"
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-05-01"}, stage="s02_data")
    assert manifest.status("s01_problem", "common")[0] == "FRESH"  # s01 never read test_cutoffs
    data = protocol.load()
    data["seed"] = 7
    import yaml
    (e5 / "spec" / "protocol.yaml").write_text(yaml.safe_dump(data), encoding="utf-8", newline="\n")
    state, reasons = manifest.status("s01_problem", "common")
    assert state == "STALE" and any("pre_registered" in r for r in reasons)


def test_contract_is_consistent():
    from e5lib import contract
    assert contract.validate() == []
    assert len(contract.PREDICTORS) == 24
    assert "freight_ratio" not in contract.LOG_CANDIDATES
    assert not set(contract.NOT_IN_CONTRACT) & set(contract.PREDICTORS)


# CR-063 (B-G-16): frozen Pipeline B modules, not edited because their code is the tagged code behind accepted
# stages and T1 (CR-058 deferred their fix to the migration, which CR-061 removed). Only these files are skipped;
# all other code, including new code, is still checked.
FROZEN_E5B_EXCLUDED = {f"pipeline_b/e5b/{m}.py" for m in (
    "t1_joint_test", "adoption", "adapter", "b10", "b09", "b09_extra", "doc_support", "serving")}


def test_text_io_names_an_encoding():
    """Every read_text/write_text names encoding="utf-8" (no dependence on the OS locale, e.g. GBK); every
    write_text names newline="\\n" and every to_csv lineterminator="\\n", so output bytes are the same on
    every OS (CR-030, CR-031)."""
    import ast
    from conftest import REAL_E5
    missing = []
    for path in REAL_E5.rglob("*.py"):
        if ".venv" in path.parts:
            continue
        if path.relative_to(REAL_E5).as_posix() in FROZEN_E5B_EXCLUDED:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("read_text", "write_text")
                    and not any(k.arg == "encoding" for k in node.keywords)):
                missing.append(f"{path.relative_to(REAL_E5)}:{node.lineno} encoding")
            needed = {"write_text": "newline", "to_csv": "lineterminator"}
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in needed
                    and not any(k.arg == needed[node.func.attr] for k in node.keywords)):
                missing.append(f"{path.relative_to(REAL_E5)}:{node.lineno} {needed[node.func.attr]}")
    assert not missing, missing


def test_outputs_have_the_same_bytes_on_windows(e5, monkeypatch):
    """Simulate Windows line separators: outputs must still be LF-only, and gzip output reproducible."""
    import os
    import pandas as pd
    from e5lib.outputs import Writer
    monkeypatch.setattr(os, "linesep", "\r\n")

    def run():
        w = Writer("s02_data", "common")
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        w.table("plain", df, ids=("2.1",))
        w.table("packed", df, ids=("2.1",), compress=True)
        w.text("note.md", "line 1\nline 2\n", ids=("2.1",))
        w.json("obj", {"k": [1, 2]}, ids=("2.1",))
        w.finish(seed=42)
        return {p.name: p.read_bytes() for p in w.dir.rglob("*") if p.is_file() and p.name != "_manifest.json"}

    first = run()
    assert not [n for n, b in first.items() if not n.endswith(".gz") and b"\r" in b]
    assert run()["packed.csv.gz"] == first["packed.csv.gz"]


def test_experiment_checks_out_with_lf():
    import subprocess
    from conftest import REAL_E5
    out = subprocess.run(["git", "check-attr", "eol", "--", "e5lib/outputs.py", "stages/s01_problem/common/outputs/task_contract.md"],
                         cwd=REAL_E5, capture_output=True, text=True).stdout
    assert out.count("eol: lf") == 2, out
