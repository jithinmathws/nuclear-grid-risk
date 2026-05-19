from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.simulation_run import SimulationRunResponse
from app.services.simulation_run_service import SimulationRunService

router = APIRouter(
    prefix="/simulation-runs",
    tags=["Simulation Runs"],
)


@router.get(
    "/{run_id}",
    response_model=SimulationRunResponse,
)
def get_simulation_run(
    run_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> SimulationRunResponse:
    service = SimulationRunService(db)
    return service.get_run(run_id)