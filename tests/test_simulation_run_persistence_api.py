from app.models.asset import Asset
from app.models.dependency import Dependency
from app.models.scenario import Scenario


def test_saved_scenario_simulation_persists_run_and_events(client, db_session):
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

    assert "run_id" in data

    run_id = data["run_id"]

    run_response = client.get(
        f"/api/v1/simulation-runs/{run_id}",
    )

    assert run_response.status_code == 200

    run_data = run_response.json()

    assert run_data["id"] == run_id
    assert run_data["scenario_id"] == str(scenario.id)
    assert run_data["scenario_name"] == "Saved External Grid Loss"

    assert run_data["risk_score"] == data["summary"]["risk_score"]
    assert run_data["risk_level"] == data["summary"]["risk_level"]

    assert run_data["total_failed_assets"] == 2
    assert run_data["critical_assets_failed"] == 2
    assert run_data["max_cascade_depth"] == 10

    assert len(run_data["events"]) == 2

    events_by_asset_id = {
        event["asset_id"]: event
        for event in run_data["events"]
    }

    assert events_by_asset_id[str(asset_a.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_a.id)]["time_minute"] == 0

    assert events_by_asset_id[str(asset_b.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_b.id)]["time_minute"] == 10
    assert events_by_asset_id[str(asset_b.id)]["caused_by_asset_id"] == str(asset_a.id)
    assert events_by_asset_id[str(asset_b.id)]["dependency_type"] == "power"
    assert events_by_asset_id[str(asset_b.id)]["propagation_strength"] == 1.0

def test_list_simulation_runs_api(client, db_session):
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

    simulate_response = client.post(
        f"/api/v1/scenarios/{scenario.id}/simulate",
    )

    assert simulate_response.status_code == 200

    run_id = simulate_response.json()["run_id"]

    response = client.get("/api/v1/simulation-runs")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    run_ids = [
        run["id"]
        for run in data
    ]

    assert run_id in run_ids