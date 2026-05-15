from fastapi.testclient import TestClient

from app.main import app
from app.models.asset import Asset
from app.models.dependency import Dependency

client = TestClient(app)


def test_simulate_scenario_success(client, db_session):
    asset_a = Asset(
        name="External Grid",
        asset_type="grid",
        criticality=0.9,
    )

    asset_b = Asset(
        name="Substation",
        asset_type="substation",
        criticality=0.8,
    )

    db_session.add_all([asset_a, asset_b])
    db_session.commit()

    dependency = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="power",
        strength=1.0,
        failure_delay_minutes=10,
    )

    db_session.add(dependency)
    db_session.commit()

    payload = {
        "scenario_name": "Loss of External Grid",
        "scenario_type": "grid_failure",
        "initial_failed_asset_ids": [
            str(asset_a.id),
        ],
        "assumptions": [
            "External grid connection is unavailable.",
            "Backup systems respond based on dependency strength.",
        ],
        "propagation_threshold": 0.7,
        "max_time_minutes": 120,
    }

    response = client.post(
        "/api/v1/scenarios/simulate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scenario_name"] == payload["scenario_name"]
    assert data["scenario_type"] == payload["scenario_type"]

    assert data["initial_failed_asset_ids"] == [
        str(asset_a.id),
    ]

    assert data["assumptions"] == payload["assumptions"]

    assert data["parameters"]["propagation_threshold"] == 0.7

    assert data["parameters"]["max_time_minutes"] == 120

    assert "timeline" in data
    assert "summary" in data

    timeline = data["timeline"]

    assert len(timeline) == 2

    events_by_asset_id = {
        event["asset_id"]: event
        for event in timeline
    }

    assert events_by_asset_id[str(asset_a.id)]["state"] == "failed"

    assert events_by_asset_id[str(asset_a.id)]["time_minute"] == 0

    assert events_by_asset_id[str(asset_b.id)]["state"] == "failed"

    assert events_by_asset_id[str(asset_b.id)]["time_minute"] == 10

    assert (
        events_by_asset_id[str(asset_b.id)]["caused_by_asset_id"]
        == str(asset_a.id)
    )

    assert (
        events_by_asset_id[str(asset_b.id)]["dependency_type"]
        == "power"
    )

    assert (
        events_by_asset_id[str(asset_b.id)]["propagation_strength"]
        == 1.0
    )

    summary = data["summary"]

    assert "total_failed_assets" in summary
    assert "critical_assets_failed" in summary
    assert "failed_asset_percentage" in summary
    assert "max_cascade_depth" in summary
    assert "earliest_failure_minute" in summary
    assert "latest_failure_minute" in summary
    assert "risk_score" in summary
    assert "risk_level" in summary

    assert isinstance(summary["total_failed_assets"], int)

    assert isinstance(summary["critical_assets_failed"], int)

    assert isinstance(
        summary["failed_asset_percentage"],
        (float, int),
    )

    assert isinstance(summary["max_cascade_depth"], int)

    assert isinstance(summary["earliest_failure_minute"], int)

    assert isinstance(summary["latest_failure_minute"], int)

    assert isinstance(summary["risk_score"], (float, int))

    assert isinstance(summary["risk_level"], str)

    
    assert summary["total_failed_assets"] == 2

    assert summary["critical_assets_failed"] == 2

    assert summary["failed_asset_percentage"] == 100.0

    assert summary["max_cascade_depth"] == 10

    assert summary["earliest_failure_minute"] == 0

    assert summary["latest_failure_minute"] == 10

    assert 0 <= summary["failed_asset_percentage"] <= 100

    assert 0 <= summary["risk_score"] <= 100

    assert summary["risk_level"] in [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]

    assert (
        summary["earliest_failure_minute"]
        <= summary["latest_failure_minute"]
    )