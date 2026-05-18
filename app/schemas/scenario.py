from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.scenario import ScenarioType


class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)

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


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioResponse(ScenarioBase):
    id: UUID

    model_config = ConfigDict(
        from_attributes=True,
    )