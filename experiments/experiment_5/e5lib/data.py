"""Data loading with the population guard (README sections 5.4 and 13.1).

The only way a stage gets data:

- load_raw(table, stage): the nine Canvas CSVs, s02_data only;
- load(name, task, population, stage): the s02 records, filtered to a population;
- upstream(source_stage, source_task, filename, stage): a file from an earlier stage's outputs.

The guard raises PopulationError when a stage asks for rows it may not see:
test rows before s08, or in s08 before frozen_recipe.json exists. Every file read is
recorded, so the run manifest lists exactly what the stage used.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import TASKS, stage_rank
from . import protocol
from .paths import outputs_dir, raw_data_dir

RAW_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}
POPULATIONS = ("development", "test", "all")
FIRST_TEST_STAGE = "s08_selection"
ALL_ROWS_STAGES = ("s05_partition",)  # builds the test manifest and size checks (G-46)

_READS: list[Path] = []


class PopulationError(RuntimeError):
    """A stage asked for rows the population guard does not allow it to see."""


def reads() -> list[Path]:
    """Files read through this module in the current process (for the manifest)."""
    return list(dict.fromkeys(_READS))


def _record(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(path)
    _READS.append(path.resolve())
    return path


def load_raw(table: str, stage: str, **read_csv_kwargs) -> pd.DataFrame:
    if stage != "s02_data":
        raise PopulationError(f"only s02_data reads the raw tables, not {stage}")
    if table not in RAW_FILES:
        raise KeyError(f"unknown raw table {table!r}; expected one of {sorted(RAW_FILES)}")
    path = _record(raw_data_dir() / RAW_FILES[table])
    return pd.read_csv(path, **read_csv_kwargs)


def upstream(source_stage: str, source_task: str, filename: str, stage: str) -> Path:
    """Path of an upstream output; only earlier stages may be read."""
    if stage_rank(source_stage) >= stage_rank(stage):
        raise PopulationError(f"{stage} may read only earlier stages, not {source_stage}")
    return _record(outputs_dir(source_stage, source_task) / filename)


def _cutoff(task: str) -> pd.Timestamp:
    cutoffs = protocol.get("data_dependent.test_cutoffs.values")
    if task not in cutoffs:
        raise protocol.ProtocolError(f"no test cutoff recorded for {task}")
    return pd.Timestamp(cutoffs[task])


def _check_test_access(task: str, stage: str) -> None:
    if stage_rank(stage) < stage_rank(FIRST_TEST_STAGE):
        raise PopulationError(f"{stage} may not see the test cohort (first allowed: {FIRST_TEST_STAGE})")
    if stage == FIRST_TEST_STAGE:
        frozen = outputs_dir(FIRST_TEST_STAGE, task) / "frozen_recipe.json"
        if not frozen.exists():
            raise PopulationError("s08 reads the test cohort only after frozen_recipe.json is written")


def load(name: str, task: str, population: str, stage: str) -> pd.DataFrame:
    """Load the s02 records for one task and population.

    development: eligible orders purchased before the task's test cutoff;
    test: the orders frozen in the s05 test manifest (s08 after the freeze, and later);
    all: every eligible order (s05_partition only, to build the test manifest).
    """
    if name != "records":
        raise KeyError("load() serves 'records'; use upstream() for other stage outputs")
    if task not in TASKS:
        raise KeyError(f"unknown task {task!r}")
    if population not in POPULATIONS:
        raise KeyError(f"unknown population {population!r}; expected one of {POPULATIONS}")
    if stage_rank(stage) <= stage_rank("s02_data"):
        raise PopulationError(f"{stage} cannot load records; s02_data produces them")
    if population == "all" and stage not in ALL_ROWS_STAGES:
        raise PopulationError(f"population 'all' is reserved for {ALL_ROWS_STAGES}")
    if population == "test":
        _check_test_access(task, stage)

    df = pd.read_csv(upstream("s02_data", "common", "records.csv.gz", stage),
                     parse_dates=["purchase_ts"], low_memory=False)
    df = df[df[f"eligible_{task}"].astype(bool)].copy()
    if population == "development":
        df = df[df["purchase_ts"] < _cutoff(task)]
    elif population == "test":
        manifest = pd.read_csv(upstream("s05_partition", task, "test_manifest.csv", stage))
        df = df[df["order_id"].isin(manifest["order_id"])]
    return df.reset_index(drop=True)
