from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.scenario_simulation import (
    ScenarioSimulationRequest,
    ScenarioSimulationResponse,
)
from app.services.scenario_simulation_service import ScenarioSimulationService

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.post("/simulate", response_model=ScenarioSimulationResponse)
def simulate_scenario(
    request: ScenarioSimulationRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ScenarioSimulationResponse:
    service = ScenarioSimulationService(db)
    return service.simulate_scenario(request)