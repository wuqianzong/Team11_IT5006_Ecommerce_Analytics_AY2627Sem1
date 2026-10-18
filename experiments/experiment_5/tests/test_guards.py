"""Paths, protocol ownership and the population guard."""
import json

import pandas as pd
import pytest

from conftest import write_records


def test_containment(e5):
    from e5lib import paths
    with pytest.raises(paths.ContainmentError):
        paths.assert_inside_e5(e5.parent / "outside.txt")
    assert paths.assert_inside_e5(e5 / "stages" / "x.txt")
    with pytest.raises(ValueError):
        paths.review_dir("s02_data", "common", 0)
    with pytest.raises(ValueError):
        paths.stage_dir("s99_unknown", "common")


def test_protocol_ownership(e5):
    from e5lib import protocol
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-05-01"}, stage="s02_data")
    assert protocol.get("data_dependent.test_cutoffs.values.regression") == "2018-05-01"
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-05-01"}, stage="s02_data")  # same value: ok
    with pytest.raises(protocol.ProtocolError):
        protocol.set_data_dependent("test_cutoffs", {"regression": "2018-06-01"}, stage="s02_data")
    with pytest.raises(protocol.ProtocolError):
        protocol.set_data_dependent("selected_set", ["a"], stage="s03_eda")
    with pytest.raises(protocol.ProtocolError):
        protocol.get("no.such.key")


@pytest.fixture()
def records(e5):
    from e5lib import protocol
    rows = [
        {"order_id": f"o{i}", "customer_unique_id": f"c{i}", "purchase_ts": f"2018-0{1 + i // 3}-15",
         "eligible_regression": True, "eligible_classification": i % 2 == 0, "lead_days": 5.0 + i}
        for i in range(9)
    ]
    write_records(e5, rows)
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-03-01", "classification": "2018-03-01"},
                                stage="s02_data")
    return rows


def test_development_population(records):
    from e5lib import data
    dev = data.load("records", "regression", "development", stage="s03_eda")
    assert dev["purchase_ts"].max() < pd.Timestamp("2018-03-01")
    assert len(dev) == 6
    clf = data.load("records", "classification", "development", stage="s03_eda")
    assert clf["eligible_classification"].all()


def test_test_population_is_guarded(records, e5):
    from e5lib import data
    with pytest.raises(data.PopulationError):
        data.load("records", "regression", "test", stage="s06_training")
    with pytest.raises(data.PopulationError):
        data.load("records", "regression", "test", stage="s08_selection")  # before the freeze
    out = e5 / "stages" / "s08_selection" / "regression" / "outputs"
    out.mkdir(parents=True)
    (out / "frozen_recipe.json").write_text(json.dumps({"frozen": True}))
    s05 = e5 / "stages" / "s05_partition" / "regression" / "outputs"
    s05.mkdir(parents=True)
    pd.DataFrame({"order_id": ["o7", "o8"]}).to_csv(s05 / "test_manifest.csv", index=False)
    test = data.load("records", "regression", "test", stage="s08_selection")
    assert sorted(test["order_id"]) == ["o7", "o8"]


def test_other_guards(records):
    from e5lib import data
    with pytest.raises(data.PopulationError):
        data.load_raw("orders", stage="s03_eda")
    with pytest.raises(data.PopulationError):
        data.load("records", "regression", "all", stage="s03_eda")
    with pytest.raises(data.PopulationError):
        data.upstream("s06_training", "regression", "x.csv", stage="s05_partition")
    assert data.load("records", "regression", "all", stage="s05_partition").shape[0] == 9
    assert any(p.name == "records.csv.gz" for p in data.reads())


def test_data_dependent_write_does_not_stale_other_stages(e5):
    import pandas as pd
    from e5lib import manifest, protocol
    from e5lib.outputs import Writer
    w = Writer("s01_problem", "common")
    w.json("protocol_snapshot", protocol.load(), ids=("1.9",))
    w.finish(seed=42)
    assert manifest.status("s01_problem", "common")[0] == "FRESH"
    protocol.set_data_dependent("test_cutoffs", {"regression": "2018-05-01"}, stage="s02_data")
    assert manifest.status("s01_problem", "common")[0] == "FRESH"  # s01 never read test_cutoffs
    data = protocol.load()
    data["seed"] = 7
    import yaml
    (e5 / "spec" / "protocol.yaml").write_text(yaml.safe_dump(data))
    state, reasons = manifest.status("s01_problem", "common")
    assert state == "STALE" and any("pre_registered" in r for r in reasons)
