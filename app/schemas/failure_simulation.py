from uuid import UUID

from pydantic import BaseModel, Field


class FailureImpactRequest(BaseModel):
    failed_asset_id: UUID
    propagation_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class ImpactedAssetResponse(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    criticality: float
    caused_by_asset_id: str | None = None
    dependency_type: str | None = None
    propagation_strength: float | None = None


class FailureImpactResponse(BaseModel):
    failed_asset_id: UUID
    impacted_asset_count: int
    impacted_assets: list[ImpactedAssetResponse]