from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.simulation_run import SimulationRunResponse
from app.services.simulation_run_service import SimulationRunService
from app.schemas.simulation_run_analytics import SimulationRunMetricsResponse
from app.services.simulation_run_analytics_service import SimulationRunAnalyticsService
from app.schemas.high_risk_simulation_run import HighRiskSimulationRunResponse

router = APIRouter(
    prefix="/simulation-runs",
    tags=["Simulation Runs"],
)

@router.get(
    "",
    response_model=list[SimulationRunResponse],
)
def list_simulation_runs(
    db: Annotated[Session, Depends(get_db)],
) -> list[SimulationRunResponse]:
    service = SimulationRunService(db)
    return service.list_runs()

@router.get("/metrics", response_model=SimulationRunMetricsResponse)
def get_simulation_run_metrics(
    db: Annotated[Session, Depends(get_db)],
) -> SimulationRunMetricsResponse:
    service = SimulationRunAnalyticsService(db)
    return service.get_metrics()

@router.get("/high-risk", response_model=list[HighRiskSimulationRunResponse])
def get_high_risk_simulation_runs(
    db: Annotated[Session, Depends(get_db)],
    min_score: float = 70.0,
    limit: int = 10,
) -> list[HighRiskSimulationRunResponse]:
    service = SimulationRunAnalyticsService(db)
    return service.get_high_risk_runs(
        min_score=min_score,
        limit=limit,
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