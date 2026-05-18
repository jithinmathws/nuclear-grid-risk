from app.models.asset import Asset
from app.models.dependency import Dependency
from app.models.scenario import Scenario


def test_create_scenario_api(client, db_session):
    payload = {
        "name": "Loss of External Grid",
        "scenario_type": "grid_failure",
        "initial_failed_asset_ids": [
            "11111111-1111-1111-1111-111111111111",
        ],
        "assumptions": [
            "External grid unavailable.",
        ],
        "propagation_threshold": 0.7,
        "max_time_minutes": 120,
    }

    response = client.post(
        "/api/v1/scenarios",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == payload["name"]

    assert data["scenario_type"] == payload["scenario_type"]

    assert (
        data["initial_failed_asset_ids"]
        == payload["initial_failed_asset_ids"]
    )

    assert data["assumptions"] == payload["assumptions"]

    assert data["propagation_threshold"] == 0.7

    assert data["max_time_minutes"] == 120

    scenario = db_session.query(Scenario).first()

    assert scenario is not None

    assert scenario.name == payload["name"]


def test_list_scenarios_api(client, db_session):
    scenario = Scenario(
        name="Transformer Failure",
        scenario_type="component_failure",
        initial_failed_asset_ids=[
            "11111111-1111-1111-1111-111111111111",
        ],
        assumptions=[
            "Primary transformer failure.",
        ],
        propagation_threshold=0.8,
        max_time_minutes=60,
    )

    db_session.add(scenario)
    db_session.commit()

    response = client.get("/api/v1/scenarios")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1

    scenario_data = data[0]

    assert scenario_data["name"] == "Transformer Failure"

    assert scenario_data["scenario_type"] == "component_failure"

    assert scenario_data["propagation_threshold"] == 0.8

    assert scenario_data["max_time_minutes"] == 60

def test_simulate_saved_scenario_api(client, db_session):
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

    scenario = Scenario(
        name="Saved External Grid Loss",
        scenario_type="grid_failure",
        initial_failed_asset_ids=[
            str(asset_a.id),
        ],
        assumptions=[
            "External grid unavailable.",
        ],
        propagation_threshold=0.7,
        max_time_minutes=120,
    )

    db_session.add(scenario)
    db_session.commit()

    response = client.post(
        f"/api/v1/scenarios/{scenario.id}/simulate",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scenario_name"] == "Saved External Grid Loss"
    assert data["scenario_type"] == "grid_failure"
    assert data["initial_failed_asset_ids"] == [str(asset_a.id)]
    assert data["assumptions"] == ["External grid unavailable."]

    assert data["parameters"]["propagation_threshold"] == 0.7
    assert data["parameters"]["max_time_minutes"] == 120

    assert len(data["timeline"]) == 2

    assert data["summary"]["total_failed_assets"] == 2
    assert data["summary"]["critical_assets_failed"] == 2
    assert data["summary"]["latest_failure_minute"] == 10