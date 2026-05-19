from app.models.scenario import Scenario, ScenarioType
from app.models.simulation_run import SimulationRun


def _create_scenario(db_session) -> Scenario:
    scenario = Scenario(
        name="High risk analytics scenario",
        scenario_type=ScenarioType.GRID_FAILURE,
        initial_failed_asset_ids=["asset-1"],
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario


def _create_run(
    db_session,
    scenario: Scenario,
    risk_score: float,
    risk_level: str,
    max_cascade_depth: int,
) -> SimulationRun:
    run = SimulationRun(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        parameters_snapshot={},
        total_failed_assets=10,
        critical_assets_failed=2,
        failed_asset_percentage=20.0,
        max_cascade_depth=max_cascade_depth,
        earliest_failure_minute=0,
        latest_failure_minute=15,
        risk_score=risk_score,
        risk_level=risk_level,
    )
    db_session.add(run)
    return run


def test_get_high_risk_simulation_runs_empty(client):
    response = client.get("/api/v1/simulation-runs/high-risk")

    assert response.status_code == 200
    assert response.json() == []


def test_get_high_risk_simulation_runs(client, db_session):
    scenario = _create_scenario(db_session)

    _create_run(db_session, scenario, 20.0, "low", 1)
    _create_run(db_session, scenario, 50.0, "medium", 2)
    _create_run(db_session, scenario, 85.0, "high", 3)
    _create_run(db_session, scenario, 95.0, "critical", 4)

    db_session.commit()

    response = client.get("/api/v1/simulation-runs/high-risk")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["risk_score"] == 95.0
    assert data[1]["risk_score"] == 85.0


def test_get_high_risk_simulation_runs_with_custom_min_score(client, db_session):
    scenario = _create_scenario(db_session)

    _create_run(db_session, scenario, 72.0, "high", 2)
    _create_run(db_session, scenario, 88.0, "high", 3)
    _create_run(db_session, scenario, 96.0, "critical", 4)

    db_session.commit()

    response = client.get("/api/v1/simulation-runs/high-risk?min_score=90")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["risk_score"] == 96.0


def test_get_high_risk_simulation_runs_limit(client, db_session):
    scenario = _create_scenario(db_session)

    _create_run(db_session, scenario, 80.0, "high", 2)
    _create_run(db_session, scenario, 90.0, "high", 3)
    _create_run(db_session, scenario, 100.0, "critical", 4)

    db_session.commit()

    response = client.get("/api/v1/simulation-runs/high-risk?limit=1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["risk_score"] == 100.0