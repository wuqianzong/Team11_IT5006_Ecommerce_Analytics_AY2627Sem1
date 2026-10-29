"""Score an order tab (plan revision 2, 4.1-4.4): alert list, no labels, scenarios."""
import pandas as pd

from dashboard_core import alerts, model_client, score_tab


def test_alert_list_matches_the_stored_serving_rule() -> None:
    queue = alerts.alert_queue()
    counts = queue.groupby("pipeline").size()
    # B at 4/15 on B's test rows; A at 1/6 outside B's scope (report 5.6 and 14.9 a day).
    assert counts["B"] == 540
    assert counts["A"] == 1428
    assert queue["review_position"].tolist() == list(range(1, len(queue) + 1))
    assert (queue.loc[queue["pipeline"] == "B", "review_position"] <= 540).all()


def test_no_label_or_outcome_column_reaches_the_tab() -> None:
    rows = alerts.model_rows("classification", tuple(alerts.alert_queue()["order_id"].head(3)))
    # The frozen row builder needs the label columns to exist; they are added back empty.
    present = alerts.LABEL_COLUMNS & set(rows.columns)
    assert all(rows[column].isna().all() for column in present)
    assert not {"y_true", "delivered_ts", "review_score", "is_detractor", "is_detractor_first"} & set(rows.columns)
    assert "y_true" not in alerts._stored_alert_predictions().columns


def test_live_scores_equal_the_stored_t1_predictions() -> None:
    queue = alerts.alert_queue().head(5)
    rows = alerts.model_rows("classification", tuple(queue["order_id"]))
    scored = model_client.predict("classification", rows).merge(queue[["order_id", "stored_risk"]], on="order_id")
    assert (scored["prediction"] - scored["stored_risk"]).abs().max() < 1e-9


def test_scenarios_are_labelled_and_freight_lowers_the_risk() -> None:
    order = alerts.alert_queue().iloc[1]
    row = alerts.model_rows("classification", (order["order_id"],))
    scenarios = score_tab._scenario_rows(row, order["pipeline"], transit_saving=0.5)
    assert set(scenarios["scenario"]) == {
        "As is", "Logistics −10%", "Freight −20%", "Freight −30%", "Freight −50%", "Free shipping"
    }
    scored = model_client.predict("classification", scenarios).assign(scenario=scenarios["scenario"].to_numpy())
    risk = scored.set_index("scenario")["prediction"]
    assert risk["Free shipping"] < risk["As is"]
    assert scenarios.loc[scenarios["scenario"] == "As is", "total_freight"].iloc[0] == row["total_freight"].iloc[0]
