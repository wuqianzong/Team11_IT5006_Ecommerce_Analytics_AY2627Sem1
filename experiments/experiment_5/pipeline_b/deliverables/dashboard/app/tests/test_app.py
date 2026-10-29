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

