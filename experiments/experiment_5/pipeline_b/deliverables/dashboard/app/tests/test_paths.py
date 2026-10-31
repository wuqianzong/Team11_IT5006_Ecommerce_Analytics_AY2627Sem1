from dashboard_core import paths


def test_business_dashboard_data_exists() -> None:
    assert paths.BUSINESS_DATA_PATH.is_file()


def test_required_task_manifests_exist() -> None:
    for task in paths.TASKS:
        assert paths.app_sources_path(task).is_file()
        assert paths.serving_config_path(task).is_file()
        assert paths.input_validation_path(task).is_file()
        assert paths.drift_profile_path(task).is_file()


def test_all_frozen_bundles_exist() -> None:
    for task in paths.TASKS:
        for pipeline in ("A", "B"):
            model, schema, profile = paths.bundle_files(task, pipeline)
            assert model.is_file()
            assert schema.is_file()
            assert profile.is_file()

