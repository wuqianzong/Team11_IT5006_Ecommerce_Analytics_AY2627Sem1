"""Cached loaders for the business marts (docs/data_architecture.md §4.4).

The dashboard reads materialized marts from ``data/processed/marts/`` — it does
not re-derive joins or metric logic. Parquet preserves native dtypes (datetimes,
nullable booleans), so no CSV round-trip fixes are needed here.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

MARTS_DIR = Path(__file__).resolve().parent.parent / "data" / "processed" / "marts"


@st.cache_data
def load_orders() -> pd.DataFrame:
    """One row per order, including observed delivery/review outcomes."""
    return pd.read_parquet(MARTS_DIR / "mart_order_dashboard.parquet")


@st.cache_data
def load_items() -> pd.DataFrame:
    """One row per (order, item), for category/seller detail pages."""
    return pd.read_parquet(MARTS_DIR / "mart_order_items.parquet")


@st.cache_data
def load_geo_state() -> pd.DataFrame:
    """One row per state: centroid (lat/lng) + name, for the map."""
    return pd.read_parquet(MARTS_DIR / "mart_state_summary.parquet")


@st.cache_data
def load_category_daily() -> pd.DataFrame:
    """One row per (date, category): additive daily counts for time trends."""
    return pd.read_parquet(MARTS_DIR / "mart_category_daily.parquet")


@st.cache_data
def load_data_quality() -> pd.DataFrame:
    """One row per materialised table: pipeline-health self-check."""
    return pd.read_parquet(MARTS_DIR / "mart_data_quality.parquet")
