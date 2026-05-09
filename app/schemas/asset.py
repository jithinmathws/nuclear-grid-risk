from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetBase(BaseModel):
    name: str
    asset_type: str
    criticality: int
    status: str = "active"


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    criticality: int | None = None
    status: str | None = None


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID