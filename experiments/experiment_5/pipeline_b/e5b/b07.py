"""B7: A's s07 tuning on B's inputs (B6–B7 blueprint; G-79). Evidence IDs B7.x = A's 7.x."""
from __future__ import annotations

from e5lib import tuning

from .adapter import b_inputs, originals_restored, run_a_stage
from .env import assert_a_frozen

STAGE = "b07"


def run(task: str) -> None:
    assert_a_frozen()
    run_a_stage(tuning, task, b_inputs(task, STAGE))
    if not originals_restored():
        raise SystemExit("B7: A's input functions were not restored")
    assert_a_frozen()
