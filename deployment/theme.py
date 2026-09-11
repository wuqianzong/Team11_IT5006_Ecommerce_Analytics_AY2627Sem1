"""Design tokens + shared Plotly layout for the SmartCommerce dashboard.

Palette is the validated default instance of the data-viz method (light surface).
Color rules applied throughout:
  - single series  -> one hue (blue) for every mark
  - ordinal buckets (1..5 stars) -> blue, light -> dark
  - magnitude on a map -> sequential blue
  - polarity -> blue <-> red (not used here, reserved)
"""

# categorical — fixed order, assign in sequence, never cycle
CATEGORICAL = [
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]
BLUE = CATEGORICAL[0]

# sequential (blue, light -> dark) for continuous magnitude
SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef",
    "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
    "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

# ordinal (blue, light -> dark) for discrete ordered marks, e.g. 1..5 stars
ORDINAL_BLUE_5 = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6"]

# review-score traffic light (1=red .. 5=green) — executive style, team preference
REVIEW_TRAFFIC_5 = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"]

# polarity (gain/loss) — red/green, executive style
GAIN = "#22c55e"
LOSS = "#ef4444"

# executive palette — PowerBI style (teammate's preference)
BLUE_PRIMARY = "#2563eb"   # lines / primary
BLUE_BAR = "#3b82f6"       # bars
BLUE_BOX = "#60a5fa"       # box fill
BUYER_BLUE = "#1e40af"     # buyer geography
SELLER_ORANGE = "#c2410c"  # seller geography

# status — reserved meaning, always icon + label
STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

# surfaces & ink
SURFACE = "#ffffff"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
FONT = "Segoe UI, system-ui, -apple-system, sans-serif"


def apply_layout(fig, *, height=360, title=None, legend=None,
                 xaxis_title=None, yaxis_title=None):
    """Apply the shared quiet chrome: recessive grid, muted axes, system sans.

    A single series gets no legend box (the title names it); a legend appears
    automatically once there are two or more series, top-right, so it never
    collides with the top-left title or the x-axis labels.
    """
    if legend is None:
        legend = len(fig.data) > 1

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=INK_PRIMARY),
                   x=0.0, xanchor="left"),
        height=height,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT, size=12, color=INK_SECONDARY),
        margin=dict(l=8, r=8, t=44 if title else 12, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(size=11, color=INK_SECONDARY)),
        hoverlabel=dict(bgcolor="white", font=dict(color=INK_PRIMARY,
                                                   family=FONT, size=12)),
    )
    fig.update_xaxes(
        gridcolor=GRIDLINE, zeroline=False, linecolor=BASELINE, linewidth=1,
        tickfont=dict(color=INK_MUTED), ticks="outside",
        title=dict(text=xaxis_title, font=dict(color=INK_SECONDARY, size=12))
        if xaxis_title else None,
    )
    fig.update_yaxes(
        gridcolor=GRIDLINE, zeroline=False, linecolor=BASELINE, linewidth=1,
        tickfont=dict(color=INK_MUTED), ticks="outside",
        title=dict(text=yaxis_title, font=dict(color=INK_SECONDARY, size=12))
        if yaxis_title else None,
    )
    return fig
