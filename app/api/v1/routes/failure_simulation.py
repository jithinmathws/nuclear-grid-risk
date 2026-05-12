from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.failure_simulation import (
    FailureImpactRequest,
    FailureImpactResponse,
    TimeStepFailureRequest,
    TimeStepFailureResponse,
)
from app.services.failure_impact_service import FailureImpactService

router = APIRouter(prefix="/failure-simulation", tags=["Failure Simulation"])


@router.post("/impact", response_model=FailureImpactResponse)
def simulate_failure_impact(
    request: FailureImpactRequest,
    db: Annotated[Session, Depends(get_db)],
) -> FailureImpactResponse:
    service = FailureImpactService(db)

    impacted_assets = service.get_downstream_impact(
        failed_asset_id=request.failed_asset_id,
        propagation_threshold=request.propagation_threshold,
    )

    return FailureImpactResponse(
        failed_asset_id=request.failed_asset_id,
        impacted_asset_count=len(impacted_assets),
        impacted_assets=impacted_assets,
    )

@router.post("/time-step", response_model=TimeStepFailureResponse)
def simulate_time_step_failure(
    request: TimeStepFailureRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TimeStepFailureResponse:
    service = FailureImpactService(db)

    timeline = service.simulate_time_step_failure(
        failed_asset_id=request.failed_asset_id,
        propagation_threshold=request.propagation_threshold,
        max_time_minutes=request.max_time_minutes,
    )

    return TimeStepFailureResponse(
        failed_asset_id=request.failed_asset_id,
        max_time_minutes=request.max_time_minutes,
        event_count=len(timeline),
        timeline=timeline,
    )