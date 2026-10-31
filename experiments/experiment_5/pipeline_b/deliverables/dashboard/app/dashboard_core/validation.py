"""Input-validation summaries built from the frozen release router."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from dashboard_core.routing import DashboardRelease


@dataclass(frozen=True)
class ValidationSummary:
    issues: pd.DataFrame

    @property
    def errors(self) -> pd.DataFrame:
        return self.issues[self.issues["level"] == "error"]

    @property
    def warnings(self) -> pd.DataFrame:
        return self.issues[self.issues["level"] == "warning"]

    @property
    def rejected_order_ids(self) -> frozenset[object]:
        return frozenset(self.errors["order_id"].tolist())

    @property
    def warning_order_ids(self) -> frozenset[object]:
        return frozenset(self.warnings["order_id"].tolist())


def validate_inputs(
    frame: pd.DataFrame,
    release: DashboardRelease,
) -> ValidationSummary:
    return ValidationSummary(issues=release.check(frame))

