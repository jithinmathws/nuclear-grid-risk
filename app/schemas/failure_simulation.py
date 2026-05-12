from uuid import UUID

from pydantic import BaseModel


class FailureImpactRequest(BaseModel):
    failed_asset_id: UUID


class ImpactedAssetResponse(BaseModel):
    asset_id: UUID
    name: str
    asset_type: str
    criticality: float


class FailureImpactResponse(BaseModel):
    failed_asset_id: UUID
    impacted_asset_count: int
    impacted_assets: list[ImpactedAssetResponse]