from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: DbSession) -> Asset:
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/", response_model=list[AssetRead])
def list_assets(db: DbSession) -> list[Asset]:
    return db.query(Asset).order_by(Asset.id).all()


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: UUID, db: DbSession) -> Asset:
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: UUID, payload: AssetUpdate, db: DbSession) -> Asset:
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: UUID, db: DbSession) -> None:
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()