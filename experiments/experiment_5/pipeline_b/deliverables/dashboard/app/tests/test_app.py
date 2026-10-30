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


def test_promise_buffer_opens_on_the_adopted_pipeline() -> None:
    """Panel 2.4 starts on B's validation curve, the one the report's buffers are chosen from."""
    app = AppTest.from_file(str(APP), default_timeout=120).run()
    box = next(b for b in app.selectbox if b.key == "buffer_series")
    assert box.value == "B on B's validation rows (out-of-fold)"

