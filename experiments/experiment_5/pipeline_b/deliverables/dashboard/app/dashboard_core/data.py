"""Cached, read-only data access for dashboard panels and inference."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import streamlit as st

from dashboard_core import paths

MAX_HELD_OUT_ROWS = 500


@st.cache_data(show_spinner=False)
def read_csv(
    path: str,
    parse_dates: tuple[str, ...] = (),
    usecols: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    return pd.read_csv(
        path,
        parse_dates=list(parse_dates),
        usecols=list(usecols) if usecols else None,
        low_memory=False,
    )


@st.cache_data(show_spinner=False)
def read_gzip_csv(path: str, usecols: tuple[str, ...] | None = None) -> pd.DataFrame:
    return pd.read_csv(
        path,
        usecols=list(usecols) if usecols else None,
        low_memory=False,
    )


@st.cache_data(show_spinner=False)
def load_business_dashboard() -> pd.DataFrame:
    frame = pd.read_csv(paths.BUSINESS_DATA_PATH, low_memory=False)
    date_columns = [column for column in frame.columns if "date" in column or "timestamp" in column]
    for column in date_columns:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_business_complete_months() -> pd.DataFrame:
    frame = load_business_dashboard()
    frame = frame[frame["order_purchase_timestamp"] >= pd.Timestamp("2017-03-01")].copy()
    frame["year_month"] = frame["order_purchase_timestamp"].dt.to_period("M").astype(str)
    periods = pd.PeriodIndex(sorted(frame["year_month"].unique()), freq="M")
    complete = []
    for period in periods:
        month_rows = frame[frame["year_month"] == str(period)]
        last_observed = month_rows["order_purchase_timestamp"].max()
        if pd.notna(last_observed) and last_observed >= period.end_time.normalize():
            complete.append(str(period))
        elif period < periods.max():
            complete.append(str(period))
    return frame[frame["year_month"].isin(complete)].copy()


@st.cache_data(show_spinner=False)
def evidence_table(task: str, stage: str, filename: str) -> pd.DataFrame:
    return pd.read_csv(paths.evidence_output(task, stage, filename), low_memory=False)


def require_evidence_table(
    task: str,
    stage: str,
    filename: str,
    columns: Iterable[str] = (),
) -> pd.DataFrame:
    frame = evidence_table(task, stage, filename)
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{stage}/{task}/{filename} is missing columns: {missing}")
    return frame


@st.cache_data(show_spinner=True)
def build_scoring_rows(task: str) -> pd.DataFrame:
    """Rebuild held-out model inputs with all label columns excluded.

    The row builder is the frozen T1 builder. It is used for inference only; no
    target, metric, threshold or model parameter is fitted here.
    """
    paths.require_task(task)

    from e5lib.paths import raw_data_dir
    from e5b import history
    from e5b.t1_joint_test import EVENTS_UNTIL, b_rows

    label_columns = {
        "lead_days",
        "lead_label_ts",
        "is_detractor",
        "is_detractor_first",
        "review_label_ts",
    }
    records_path = paths.E5 / "stages" / "s02_data" / "common" / "outputs" / "records.csv.gz"
    predictions_path = paths.t1_output(task, "predictions_test.csv.gz")

    predictions = pd.read_csv(
        predictions_path,
        usecols=["order_id", "rows"],
        low_memory=False,
    )
    test_ids = set(predictions.loc[predictions["rows"] == "A test rows", "order_id"])
    records = pd.read_csv(
        records_path,
        usecols=lambda column: column not in label_columns,
        low_memory=False,
    )
    a_test = records[records["order_id"].isin(test_ids)].copy()
    if len(a_test) > MAX_HELD_OUT_ROWS:
        a_test = a_test.sample(n=MAX_HELD_OUT_ROWS, random_state=42).copy()
    a_test["purchase_ts"] = pd.to_datetime(a_test["purchase_ts"], errors="coerce")
    a_test["lead_days"] = np.nan
    a_test["lead_label_ts"] = pd.NaT
    a_test["review_label_ts"] = pd.NaT

    events = history.load_events(raw_data_dir(), EVENTS_UNTIL)
    cap: float | None = None
    if task == "regression":
        import json

        cap = float(
            json.loads(
                paths.evidence_output(
                    "regression", "b02", "feature_build_log.json"
                ).read_text(encoding="utf-8")
            )["lead_cap_days"]
        )

    b_rows_frame, _ = b_rows(task, a_test, events, cap)
    extra_columns = [
        column
        for column in b_rows_frame.columns
        if column not in a_test.columns or column == "order_id"
    ]
    scoring = a_test.merge(
        b_rows_frame[extra_columns].drop_duplicates("order_id"),
        on="order_id",
        how="left",
    )
    return scoring.reset_index(drop=True)


@lru_cache(maxsize=2)
def scoring_order_ids(task: str) -> tuple[str, ...]:
    frame = build_scoring_rows(task)
    return tuple(sorted(frame["order_id"].astype(str).unique()))

