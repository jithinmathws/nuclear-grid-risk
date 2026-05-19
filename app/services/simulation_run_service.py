from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.simulation_run import SimulationEvent, SimulationRun
from app.schemas.scenario_simulation import ScenarioSimulationResponse


class SimulationRunService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_run_from_simulation(
        self,
        scenario: Scenario,
        simulation_response: ScenarioSimulationResponse,
    ) -> SimulationRun:
        run = SimulationRun(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            parameters_snapshot=simulation_response.parameters,
            total_failed_assets=simulation_response.summary.total_failed_assets,
            critical_assets_failed=simulation_response.summary.critical_assets_failed,
            failed_asset_percentage=simulation_response.summary.failed_asset_percentage,
            max_cascade_depth=simulation_response.summary.max_cascade_depth,
            earliest_failure_minute=simulation_response.summary.earliest_failure_minute,
            latest_failure_minute=simulation_response.summary.latest_failure_minute,
            risk_score=simulation_response.summary.risk_score,
            risk_level=simulation_response.summary.risk_level,
        )

        self.db.add(run)
        self.db.flush()

        for event in simulation_response.timeline:
            simulation_event = SimulationEvent(
                run_id=run.id,
                asset_id=event.asset_id,
                name=event.name,
                asset_type=event.asset_type,
                criticality=event.criticality,
                state=event.state,
                time_minute=event.time_minute,
                caused_by_asset_id=event.caused_by_asset_id,
                dependency_type=event.dependency_type,
                propagation_strength=event.propagation_strength,
            )

            self.db.add(simulation_event)

        self.db.commit()
        self.db.refresh(run)

        return run

    def get_run(self, run_id: UUID) -> SimulationRun:
        run = (
            self.db.query(SimulationRun)
            .filter(SimulationRun.id == run_id)
            .first()
        )

        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation run not found",
            )

        return run