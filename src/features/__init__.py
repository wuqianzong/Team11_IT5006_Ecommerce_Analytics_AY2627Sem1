"""Feature engineering and split manifest modules (feature_contract.md v1.2).

This package implements the deterministic ``data/preprocessed`` -> ``data/business/ml``
lineage described in ``data/business/ml/feature_contract.md`` and
``data/business/ml/README.md``. Entrypoints:

    python -m src.features.build_features   # base table + schema + manifests + quality report
    python -m src.features.create_splits    # outer holdout + inner CV manifests
"""
