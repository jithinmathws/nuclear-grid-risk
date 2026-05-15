from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.failure_simulation import FailureTimelineEvent


class ScenarioType(str, Enum):
    GRID_FAILURE = "grid_failure"
    COMPONENT_FAILURE = "component_failure"
    COMMON_MODE_FAILURE = "common_mode_failure"
    CYBER_EVENT = "cyber_event"
    NATURAL_HAZARD = "natural_hazard"


class ScenarioSimulationRequest(BaseModel):
    scenario_name: str = Field(..., min_length=3, max_length=120)
    scenario_type: ScenarioType

    initial_failed_asset_ids: list[UUID] = Field(
        ...,
        min_length=1,
    )

    assumptions: list[str] = Field(default_factory=list)

    propagation_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )

    max_time_minutes: int = Field(
        default=120,
        gt=0,
    )


class ScenarioResultSummary(BaseModel):
    total_failed_assets: int
    critical_assets_failed: int

    failed_asset_percentage: float

    max_cascade_depth: int

    earliest_failure_minute: int
    latest_failure_minute: int

    risk_score: float
    risk_level: str


class ScenarioSimulationResponse(BaseModel):
    scenario_name: str
    scenario_type: ScenarioType

    initial_failed_asset_ids: list[UUID]

    assumptions: list[str]

    parameters: dict[str, Any]

    timeline: list[FailureTimelineEvent]

    summary: ScenarioResultSummary