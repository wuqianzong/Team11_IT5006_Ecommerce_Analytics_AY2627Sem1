"""Thin routing wrapper around Pipeline B's frozen serving implementation."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from dashboard_core import paths

# Importing paths configures e5lib/e5b import roots before these imports run.
from e5b.serving import FROZEN, NO_SCORE, SCOPE_COLS, Release, in_scope, scope_reason

B_STATES = frozenset({"SP", "MG", "RJ", "PR", "RS", "BA", "SC"})


@lru_cache(maxsize=None)
def load_release(task: str) -> Release:
    return Release.load(paths.require_task(task))


class DashboardRelease:
    """Expose only the serving behaviour the dashboard needs."""

    def __init__(self, task: str, release: Release | None = None):
        self.task = paths.require_task(task)
        self.release = release if release is not None else load_release(self.task)

    @property
    def threshold(self) -> dict[str, float]:
        return dict(self.release.threshold)

    def check(self, frame: pd.DataFrame) -> pd.DataFrame:
        return self.release.check(frame)

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        missing_scope = [column for column in SCOPE_COLS if column not in frame.columns]
        if missing_scope:
            raise ValueError(
                "Cannot route an order without scope columns: "
                + ", ".join(missing_scope)
            )
        return self.release.predict(frame)

    def route_scope(self, frame: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "in_b_scope": in_scope(frame).to_numpy(),
                "scope_reason": scope_reason(frame).to_numpy(),
            },
            index=frame.index,
        )


__all__ = [
    "B_STATES",
    "DashboardRelease",
    "FROZEN",
    "NO_SCORE",
    "SCOPE_COLS",
    "in_scope",
    "load_release",
    "scope_reason",
]

