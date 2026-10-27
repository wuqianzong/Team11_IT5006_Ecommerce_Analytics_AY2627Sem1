"""B11.1 number register: builds from Current runs only; placeholders fill or fail; superseded evidence is never cited."""
import json
import sys
from pathlib import Path

import pytest
import yaml

B_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(B_ROOT))

import build_evidence_B as reg  # noqa: E402


@pytest.fixture(scope="module")
def numbers(tmp_path_factory):
    # build into a temporary folder: running the tests must not rewrite the tracked evidence/build/ (B-CR-31)
    return reg.build(tmp_path_factory.mktemp("register_build"))


def test_every_item_resolves(numbers):
    items = yaml.safe_load(reg.REGISTRY.read_text(encoding="utf-8"))
    assert set(numbers) == {i["id"] for i in items}
    assert all(v["text"] for v in numbers.values() if v["kind"] == "number")


def test_sources_are_current_runs(numbers):
    runs = reg.current_runs()
    for v in numbers.values():
        stage, task = Path(v["source"]).parts[:2]
        assert v["run_id"] == runs[(stage, task)]


def test_superseded_threshold_never_cited():
    text = reg.REGISTRY.read_text(encoding="utf-8")
    assert "5/14" not in text and "5_14" not in text   # B-G-09 withdrawn


def test_fill_and_missing(numbers):
    assert reg.fill("MAE {{B9.reg.test_mae_B}} days", numbers) == f"MAE {numbers['B9.reg.test_mae_B']['text']} days"
    assert reg.missing("{{no.such.id}} and {{B9.reg.test_mae_B}}", numbers) == ["no.such.id"]
    with pytest.raises(SystemExit):
        reg.fill("{{no.such.id}}", numbers)


def test_tampered_source_is_refused(tmp_path, monkeypatch):
    runs = reg.current_runs()
    src = "b09/regression/outputs/train_val_test.csv"
    fake = tmp_path / "stages"
    for p in ("b09/regression/outputs",):
        (fake / p).mkdir(parents=True)
    (fake / src).write_text("changed\n")
    (fake / "b09/regression/outputs/_manifest.json").write_text((reg.STAGES / "b09/regression/outputs/_manifest.json").read_text())
    monkeypatch.setattr(reg, "STAGES", fake)
    with pytest.raises(ValueError):
        reg.verify_source(src, runs)


def test_table_placeholder(numbers):
    out = reg.fill("{{table:APX.windows}}", numbers)
    assert out.splitlines()[0].startswith("| period |") and len(out.splitlines()) == numbers["APX.windows"]["rows"] + 2
    assert reg.missing("{{table:no.such}}", numbers) == ["table:no.such"]


def test_build_leaves_tracked_register_untouched(numbers):
    assert all(not Path(v["file"]).is_relative_to(reg.BUILD) for v in numbers.values() if "file" in v)
