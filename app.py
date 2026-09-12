"""SmartCommerce — Root Streamlit Application Launcher.

Delegates execution directly to the authoritative dashboard implementation in
deployment/app.py.
"""
from pathlib import Path
import runpy

TARGET_APP = Path(__file__).resolve().parent / "deployment" / "app.py"

runpy.run_path(str(TARGET_APP), run_name="__main__")
