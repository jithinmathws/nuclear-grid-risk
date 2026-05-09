from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DependencyBase(BaseModel):
    source_asset_id: int
    target_asset_id: int
    dependency_type: str
    risk_weight: float = 1.0


class DependencyCreate(DependencyBase):
    pass


class DependencyUpdate(BaseModel):
    dependency_type: str | None = None
    risk_weight: float | None = None


class DependencyRead(DependencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime