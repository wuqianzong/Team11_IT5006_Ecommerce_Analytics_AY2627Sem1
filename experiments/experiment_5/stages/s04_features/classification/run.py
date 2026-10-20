"""s04_features/classification: feature definition without fitting (blueprint spec/blueprints/s04_features.md).

Steps 4.1 (baseline pool), 4.2 (transforms), 4.3 (reduction), 4.4 (selection), 4.6 (feature
dictionary), 4.7 (selected set) and 4.8 (pipeline recipes); the shared logic is in e5lib/features.py.
"""
from e5lib.features import run

if __name__ == "__main__":
    run("classification")
