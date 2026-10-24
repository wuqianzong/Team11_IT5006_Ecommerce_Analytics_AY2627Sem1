"""B8: A's s08 gate on B's inputs, then B's adoption comparison, SE decomposition and missed-dispatch
rule (B8 blueprint; G-79, B-C10, B-G-01). Evidence IDs B8.1–B8.5 = A's 8.1–8.5; B8.A adoption and
SE decomposition; B8.M missed-dispatch rule.
"""
from __future__ import annotations

import json

from e5lib import selection

from . import adoption
from .adapter import b08_extras, b_inputs, originals_restored, run_a_stage
from .env import assert_a_frozen

STAGE = "b08"


def run(task: str) -> None:
    assert_a_frozen()
    fns = b_inputs(task, STAGE)
    run_a_stage(selection, task, fns, b08_extras(task))
    if not originals_restored():
        raise SystemExit("B8: A's input functions were not restored")
    adoption.run(task)
    assert_a_frozen()
