from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)
from app.schemas.scenario_simulation import (
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
)
from app.services.scenario_simulation_service import ScenarioSimulationService
from app.services.scenario_service import ScenarioService
from app.services.simulation_run_service import SimulationRunService


router = APIRouter(
    prefix="/scenarios",
    tags=["Scenario Management"],
)


@router.post(
    "",
    response_model=ScenarioResponse,
)
def create_scenario(
    scenario_data: ScenarioCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ScenarioResponse:
    service = ScenarioService(db)

    return service.create_scenario(scenario_data)


@router.get(
    "",
    response_model=list[ScenarioResponse],
)
def list_scenarios(
    db: Annotated[Session, Depends(get_db)],
) -> list[ScenarioResponse]:
    service = ScenarioService(db)

    return service.list_scenarios()

@router.post(
    "/{scenario_id}/simulate",
    response_model=ScenarioSimulationResponse,
)
def simulate_saved_scenario(
    scenario_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> ScenarioSimulationResponse:
    scenario_service = ScenarioService(db)
    scenario = scenario_service.get_scenario(scenario_id)

    simulation_service = ScenarioSimulationService(db)

    simulation_request = ScenarioSimulationRequest(
        scenario_name=scenario.name,
        scenario_type=scenario.scenario_type,
        initial_failed_asset_ids=scenario.initial_failed_asset_ids,
        assumptions=scenario.assumptions,
        propagation_threshold=scenario.propagation_threshold,
        max_time_minutes=scenario.max_time_minutes,
    )

    simulation_response = simulation_service.simulate_scenario(
        simulation_request,
    )

    run_service = SimulationRunService(db)
    run = run_service.create_run_from_simulation(
        scenario=scenario,
        simulation_response=simulation_response,
    )

    simulation_response.run_id = run.id

    return simulation_response