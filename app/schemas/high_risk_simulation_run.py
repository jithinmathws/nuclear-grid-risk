from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HighRiskSimulationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenario_id: UUID
    scenario_name: str

    risk_score: float
    risk_level: str

    total_failed_assets: int
    critical_assets_failed: int
    max_cascade_depth: int

    created_at: datetime