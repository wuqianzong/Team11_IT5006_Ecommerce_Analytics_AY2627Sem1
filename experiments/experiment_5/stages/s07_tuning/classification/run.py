"""s07_tuning/classification: bounded grids per family on the s05 folds (blueprint spec/blueprints/s07_tuning.md).

Steps 7.1-7.7; the shared logic is in e5lib/tuning.py.
"""
from e5lib.tuning import run

if __name__ == "__main__":
    run("classification")
