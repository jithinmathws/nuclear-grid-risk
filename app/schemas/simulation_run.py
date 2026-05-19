from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SimulationEventResponse(BaseModel):
    id: UUID
    asset_id: str
    name: str
    asset_type: str
    criticality: float
    state: str
    time_minute: int
    caused_by_asset_id: str | None = None
    dependency_type: str | None = None
    propagation_strength: float | None = None

    model_config = ConfigDict(from_attributes=True)


class SimulationRunResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    scenario_name: str

    parameters_snapshot: dict

    total_failed_assets: int
    critical_assets_failed: int
    failed_asset_percentage: float
    max_cascade_depth: int
    earliest_failure_minute: int
    latest_failure_minute: int

    risk_score: float
    risk_level: str

    created_at: datetime

    events: list[SimulationEventResponse]

    model_config = ConfigDict(from_attributes=True)