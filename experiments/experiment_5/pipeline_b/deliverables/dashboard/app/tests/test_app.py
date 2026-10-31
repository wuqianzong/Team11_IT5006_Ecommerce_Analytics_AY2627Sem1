from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_renders_four_tabs_without_exception() -> None:
    app = AppTest.from_file(str(APP), default_timeout=120).run()
    assert not app.exception
    assert len(app.tabs) == 4
    threshold_slider = next(
        slider
        for slider in app.select_slider
        if slider.label == "B threshold (seven states)"
    )
    assert abs(float(threshold_slider.value) - 4 / 15) < 1e-9


def test_kpi_shares_of_order_value_show_as_percent() -> None:
    """The price and freight shares of order value are fractions shown as percentages, not as R$ amounts."""
    import sys

    import pandas as pd

    sys.path.insert(0, str(APP.parent))
    from dashboard_core.business_tab import _styled

    table = pd.DataFrame({"2018-05": [985521.0, 0.867, 0.133]},
                         index=["Total Revenue (R$)", "Price to Order Value (%)", "Freight to Order Value (%)"])
    shown = _styled(table, {}, "index").data["2018-05"].tolist()
    assert shown == ["R$ 985,521", "86.7%", "13.3%"]


def test_promise_buffer_opens_on_the_adopted_pipeline() -> None:
    """Panel 2.4 starts on B's validation curve, the one the report's buffers are chosen from."""
    app = AppTest.from_file(str(APP), default_timeout=120).run()
    box = next(b for b in app.selectbox if b.key == "buffer_series")
    assert box.value == "B on B's validation rows (out-of-fold)"

