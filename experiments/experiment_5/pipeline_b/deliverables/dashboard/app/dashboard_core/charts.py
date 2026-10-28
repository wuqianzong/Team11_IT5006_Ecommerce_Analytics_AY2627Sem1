"""Small chart helpers shared by the dashboard tabs."""
from __future__ import annotations

from dashboard_core import paths

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

COLORS = ["#2563eb", "#dc2626", "#16a34a", "#f59e0b", "#7c3aed"]


def line_chart(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    ylabel: str,
) -> None:
    fig, axis = plt.subplots(figsize=(9, 3.8))
    axis.plot(frame[x], frame[y], marker="o", color=COLORS[0], linewidth=2)
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def bar_chart(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    ylabel: str,
    color: str = COLORS[0],
) -> None:
    fig, axis = plt.subplots(figsize=(9, 3.8))
    axis.bar(frame[x].astype(str), frame[y], color=color)
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def dual_line_chart(
    frame: pd.DataFrame,
    x: str,
    series: list[str],
    title: str,
    ylabel: str,
) -> None:
    fig, axis = plt.subplots(figsize=(9, 3.8))
    for index, column in enumerate(series):
        axis.plot(
            frame[x],
            frame[column],
            marker="o",
            label=column,
            color=COLORS[index % len(COLORS)],
            linewidth=2,
        )
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.tick_params(axis="x", rotation=45)
    axis.legend()
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def horizontal_bar_chart(
    frame: pd.DataFrame,
    label: str,
    value: str,
    title: str,
    xlabel: str,
    top_n: int = 15,
) -> None:
    data = frame.sort_values(value, ascending=False).head(top_n).sort_values(value)
    fig, axis = plt.subplots(figsize=(9, max(3.6, len(data) * 0.32)))
    axis.barh(data[label].astype(str), data[value], color=COLORS[0])
    axis.set_title(title)
    axis.set_xlabel(xlabel)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

