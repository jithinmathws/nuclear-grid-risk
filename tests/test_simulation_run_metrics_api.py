from app.models.scenario import Scenario, ScenarioType
from app.models.simulation_run import SimulationRun


def test_get_simulation_run_metrics(client, db_session):
    scenario = Scenario(
        name="Grid failure scenario",
        scenario_type=ScenarioType.GRID_FAILURE,
        initial_failed_asset_ids=["asset-1"],
    )

    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)

    db_session.add_all(
        [
            SimulationRun(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                parameters_snapshot={},
                total_failed_assets=10,
                critical_assets_failed=2,
                failed_asset_percentage=20.0,
                max_cascade_depth=3,
                earliest_failure_minute=0,
                latest_failure_minute=15,
                risk_score=80.0,
                risk_level="high",
            ),
            SimulationRun(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                parameters_snapshot={},
                total_failed_assets=5,
                critical_assets_failed=1,
                failed_asset_percentage=10.0,
                max_cascade_depth=1,
                earliest_failure_minute=0,
                latest_failure_minute=5,
                risk_score=40.0,
                risk_level="medium",
            ),
            SimulationRun(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                parameters_snapshot={},
                total_failed_assets=3,
                critical_assets_failed=0,
                failed_asset_percentage=5.0,
                max_cascade_depth=2,
                earliest_failure_minute=0,
                latest_failure_minute=8,
                risk_score=20.0,
                risk_level="low",
            ),
            SimulationRun(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                parameters_snapshot={},
                total_failed_assets=15,
                critical_assets_failed=4,
                failed_asset_percentage=35.0,
                max_cascade_depth=4,
                earliest_failure_minute=0,
                latest_failure_minute=20,
                risk_score=100.0,
                risk_level="high",
            ),
        ]
    )

    db_session.commit()

    response = client.get("/api/v1/simulation-runs/metrics")

    assert response.status_code == 200

    data = response.json()

    assert data["total_runs"] == 4
    assert data["average_risk_score"] == 60.0
    assert data["highest_risk_score"] == 100.0
    assert data["most_common_risk_level"] == "high"
    assert data["average_cascade_depth"] == 2.5

    assert data["risk_level_distribution"] == {
        "high": 2,
        "medium": 1,
        "low": 1,
    }