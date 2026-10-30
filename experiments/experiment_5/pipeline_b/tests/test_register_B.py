"""B11.1 number register: builds from Current runs only; placeholders fill or fail; superseded evidence is never cited."""
import json
import re
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
        if Path(v["source"]).parts[0] == "A":   # A's frozen tree (B-G-11), checked below
            assert v["run_id"].endswith(f"@ {reg.A_TAG}")
            continue
        if Path(v["source"]).parts[0] in reg.MANIFEST_ROOTS:   # B-CR-41, B-CR-42, checked below
            assert v["run_id"].endswith(")")
            continue
        stage, task = Path(v["source"]).parts[:2]
        assert v["run_id"] == runs[(stage, task)]


def test_a_sources_only_from_the_frozen_tree(numbers):
    a_items = [v for v in numbers.values() if Path(v["source"]).parts[0] == "A"]
    assert a_items, "the report cites A's s03 EDA numbers (B-G-11)"
    assert all(Path(v["source"]).parts[1] in ("s01_problem", "s02_data", "s03_eda", "s04_features", "s05_partition",
                                               "s06_training", "s07_tuning", "s08_selection") for v in a_items)   # B-G-11, B-G-13, B-G-14
    with pytest.raises(ValueError):
        reg.verify_a_source("A/s03_eda/regression/eda_summary.json")          # not under outputs/
    with pytest.raises(ValueError):
        reg.verify_a_source("A/s03_eda/regression/outputs/no_such_file.csv")


def test_a_source_changed_after_the_tag_is_refused(monkeypatch):
    src = "A/s03_eda/regression/outputs/eda_summary.json"
    assert reg.verify_a_source(src)[0].is_file()                       # equals the file at e5-A-frozen
    monkeypatch.setattr(reg, "_sha", lambda p: "0" * 64)                # as if the working copy had changed
    with pytest.raises(ValueError, match="differs from the file at tag"):
        reg.verify_a_source(src)


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


def test_biz_sources_match_their_manifest(monkeypatch):
    """B-CR-41: business-context files are accepted only while they and their input match the manifest."""
    src = "BIZ/summary.json"
    assert reg.verify_biz_source(src)[0].is_file()
    with pytest.raises(ValueError):
        reg.verify_biz_source("BIZ/no_such_file.csv")
    monkeypatch.setattr(reg, "_sha", lambda p: "0" * 64)
    with pytest.raises(ValueError, match="does not match"):
        reg.verify_biz_source(src)


def test_replace_strips_names_under_any_string_dtype():
    """A table item's `replace` must work for object and pandas string dtypes alike (pandas 2 and 3)."""
    import yaml
    items = [i for i in yaml.safe_load(reg.REGISTRY.read_text(encoding="utf-8")) if i.get("replace")]
    assert items, "the feature tables carry a name-stripping replace rule"
    nums = json.loads((reg.BUILD / "numbers_B.json").read_text(encoding="utf-8"))
    for it in items:
        text = (reg.B_ROOT / nums[it["id"]]["file"]).read_text(encoding="utf-8")
        for pat, _ in it["replace"]:
            assert not re.search(pat, text), f"{it['id']} still matches {pat}"

