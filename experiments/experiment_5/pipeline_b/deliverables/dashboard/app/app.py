"""Team 11 delivery and detractor dashboard."""
from __future__ import annotations

import streamlit as st

from dashboard_core import business_tab as business_panel
from dashboard_core import classification_tab as classification_panel
from dashboard_core import regression_tab as regression_panel
from dashboard_core.loaders import load_task_config
from dashboard_core.paths import TASKS

st.set_page_config(
    page_title="Team 11 Delivery and Detractor Dashboard",
    page_icon="📦",
    layout="wide",
)

st.title("Team 11 Delivery and Detractor Dashboard")
st.caption("Descriptive business view plus Pipeline B results, with Pipeline A fallback.")

# Load and validate the lightweight configuration once per task. No metrics are computed.
configs = {task: load_task_config(task) for task in TASKS}
source_counts = {
    task: len(cfg.app_sources.elements)
    for task, cfg in configs.items()
}

with st.sidebar:
    st.subheader("Evidence configuration")
    for task in TASKS:
        st.caption(
            f"{task.title()}: {source_counts[task]} mapped app-source elements"
        )
    st.caption("No model is fitted and no test label is read.")

business_tab, lead_time_tab, detractor_tab = st.tabs(
    [
        "Business overview",
        "Delivery lead time",
        "Detractor risk at handover",
    ]
)

with business_tab:
    business_panel.render()

with lead_time_tab:
    regression_panel.render()

with detractor_tab:
    classification_panel.render()

