from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DependencyBase(BaseModel):
    source_asset_id: UUID
    target_asset_id: UUID
    dependency_type: str
    strength: float = Field(default=1.0, ge=0)

    redundancy_group: str | None = None
    common_mode_group: str | None = None

    failure_delay_minutes: int = Field(default=0, ge=0)

    extra_metadata: dict = Field(default_factory=dict)


class DependencyCreate(DependencyBase):
    pass


class DependencyUpdate(BaseModel):
    dependency_type: str | None = None
    strength: float | None = Field(default=None, ge=0)

    redundancy_group: str | None = None
    common_mode_group: str | None = None

    failure_delay_minutes: int | None = Field(default=None, ge=0)

    extra_metadata: dict | None = None


class DependencyRead(DependencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID