"""B6–B7 blueprint check: the adapter fed A's own inputs reproduces A's accepted outputs.

Slow (reruns A's s06, and s07 for regression); run with E5B_SLOW=1.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

B_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(B_ROOT.parent), str(B_ROOT)]

from e5b import adapter  # noqa: E402
from e5lib import training, tuning  # noqa: E402

E5 = B_ROOT.parent
EQ = B_ROOT / ".equiv"
slow = pytest.mark.skipif(os.environ.get("E5B_SLOW") != "1", reason="slow; set E5B_SLOW=1")


def _strip_b(obj):
    if isinstance(obj, str):
        return obj[1:] if obj[:1] == "B" and obj[1:2].isdigit() else obj
    if isinstance(obj, list):
        return [_strip_b(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _strip_b(v) for k, v in obj.items()}
    return obj


def _same(a_dir: Path, b_dir: Path, csvs, jsons):
    for f in csvs:
        a = pd.read_csv(a_dir / f, keep_default_na=False).drop(columns=["node"], errors="ignore")
        b = pd.read_csv(b_dir / f, keep_default_na=False).drop(columns=["node"], errors="ignore")
        pd.testing.assert_frame_equal(a, b, check_exact=True)
    for f in jsons:
        assert _strip_b(json.loads((b_dir / f).read_text(encoding="utf-8"))) == json.loads((a_dir / f).read_text(encoding="utf-8")), f


@slow
@pytest.mark.parametrize("task", ["regression", "classification"])
def test_s06_equivalence(task):
    out = EQ / "b06" / task
    adapter.run_a_stage(training, task, adapter.a_inputs(task, "b06", out))
    assert adapter.originals_restored()
    _same(E5 / "stages/s06_training" / task / "outputs", out, ["metrics_long.csv", "candidates.csv"], ["decision.json"])


@slow
def test_s07_equivalence_regression():
    task = "regression"
    out = EQ / "b07" / task
    adapter.run_a_stage(tuning, task, adapter.a_inputs(task, "b07", out, s06_dir=E5 / "stages/s06_training" / task / "outputs"))
    assert adapter.originals_restored()
    _same(E5 / "stages/s07_tuning" / task / "outputs", out, ["grid_results.csv", "candidates.csv"], ["decision.json"])


def test_redirect_restores_on_error():
    def boom(*a, **k):
        raise RuntimeError("boom")
    with pytest.raises(RuntimeError):
        with adapter.redirected(boom, boom, boom, boom):
            from e5lib import data
            data.upstream()
    assert adapter.originals_restored()


@slow
@pytest.mark.parametrize("task", ["regression", "classification"])
def test_s08_equivalence_with_a_decisions(task):
    """A's inputs and A's s08 decisions through the adapter give A's frozen recipe, same sha256."""
    from e5lib import paths, selection
    out = EQ / "b08" / task
    orig_out = paths.outputs_dir

    def outputs_dir(stage, task_):
        return out if stage == "s08_selection" else orig_out(stage, task_)

    adapter.run_a_stage(selection, task, adapter.a_inputs(task, "b08", out), (None, outputs_dir))
    assert adapter.originals_restored()
    a = json.loads((E5 / "stages/s08_selection" / task / "outputs/frozen_recipe.json").read_text(encoding="utf-8"))
    b = json.loads((out / "frozen_recipe.json").read_text(encoding="utf-8"))
    assert b["sha256"] == a["sha256"]
    _same(E5 / "stages/s08_selection" / task / "outputs", out, ["candidates.csv", "ladder.csv"], [])
