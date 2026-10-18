"""Experiment 5 technical foundation (README section 13).

Shared code every stage runs on: paths, protocol, data loading with the population guard,
cross-validation folds, candidate IDs, the pipeline factory, metrics and the decision rule,
standard output writers, run manifests and review packs.
"""

STAGE_ORDER = (
    "s01_problem",
    "s02_data",
    "s03_eda",
    "s04_features",
    "s05_partition",
    "s06_training",
    "s07_tuning",
    "s08_selection",
    "s09_conclusion",
    "s10_release",
)
TASKS = ("regression", "classification")


def stage_rank(stage: str) -> int:
    """Position of a stage in the pipeline (0-based); raises on an unknown stage."""
    try:
        return STAGE_ORDER.index(stage)
    except ValueError as exc:
        raise ValueError(f"unknown stage {stage!r}; expected one of {STAGE_ORDER}") from exc
