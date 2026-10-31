import pandas as pd

from dashboard_core import paths
from dashboard_core.loaders import (
    load_app_sources,
    load_bundle_paths,
    load_bundle_schema,
    load_task_config,
    missing_app_source_files,
    untagged_app_sources,
)
from dashboard_core.data import load_business_complete_months


def test_task_configs_load() -> None:
    for task in paths.TASKS:
        config = load_task_config(task)
        assert config.task == task
        assert config.serving_config["task"] == task
        assert config.input_validation["task"] == task
        assert config.drift_profile["task"] == task


def test_every_mapped_app_source_exists_and_is_tagged() -> None:
    for task in paths.TASKS:
        assert missing_app_source_files(task) == []
        assert untagged_app_sources(task) == []


def test_bundle_metadata_loads() -> None:
    for task in paths.TASKS:
        bundle_paths = load_bundle_paths(task)
        assert set(bundle_paths) == {"A", "B"}
        for pipeline in ("A", "B"):
            schema = load_bundle_schema(task, pipeline)
            assert schema["task"] == task
            assert schema["pipeline"] == pipeline


def test_app_sources_are_non_empty() -> None:
    for task in paths.TASKS:
        sources = load_app_sources(task)
        assert sources.elements
        assert all(element.evidence_id for element in sources.elements)


def test_business_dashboard_starts_in_march_2017() -> None:
    frame = load_business_complete_months()
    assert not frame.empty
    assert frame["order_purchase_timestamp"].min() >= pd.Timestamp("2017-03-01")

