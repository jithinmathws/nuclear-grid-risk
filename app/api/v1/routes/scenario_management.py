from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)
from app.services.scenario_service import ScenarioService

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