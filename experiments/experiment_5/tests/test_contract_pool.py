"""The selection pool per task (G-70): one source for the feature set s04 selects from."""
from e5lib import contract


def test_classification_pool_is_24_plus_adopted():
    pool = contract.pool("classification")
    assert len(pool) == 27 and pool[:24] == contract.PREDICTORS
    assert set(pool[24:]) == {"product_photos_qty", "product_description_lenght", "seller_prior_review_mean"}


def test_regression_pool_is_the_contract():
    assert contract.pool("regression") == contract.PREDICTORS


def test_not_adopted_candidates_stay_out():
    pool = set(contract.pool("classification"))
    for c in ("est_delivery_days", "product_name_lenght", "seller_prior_detractor_share",
              "seller_prior_late_share", "region_pair"):
        assert c not in pool
