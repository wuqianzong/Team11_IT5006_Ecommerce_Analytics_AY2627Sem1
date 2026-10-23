"""s08_selection/classification: finalists, recommendation and gate on the s05 folds (blueprint spec/blueprints/s08_selection.md).

Steps 8.1-8.4; the run stops at the gate (G-39, G-78). The shared logic is in e5lib/selection.py.
"""
from e5lib.selection import run

if __name__ == "__main__":
    run("classification")
