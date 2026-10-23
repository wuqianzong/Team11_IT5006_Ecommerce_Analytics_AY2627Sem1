"""B6: A's s06 training ladder on B's inputs (B6–B7 blueprint; G-79). Evidence IDs B6.x = A's 6.x."""
from __future__ import annotations

from e5lib import training

from .adapter import b_inputs, originals_restored, run_a_stage
from .env import assert_a_frozen

STAGE = "b06"


def run(task: str) -> None:
    assert_a_frozen()
    run_a_stage(training, task, b_inputs(task, STAGE))
    if not originals_restored():
        raise SystemExit("B6: A's input functions were not restored")
    assert_a_frozen()
