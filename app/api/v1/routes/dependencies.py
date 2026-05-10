from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import Asset
from app.models.dependency import Dependency
from app.schemas.dependency import DependencyCreate, DependencyRead, DependencyUpdate

router = APIRouter(prefix="/dependencies", tags=["dependencies"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_asset_or_404(asset_id: UUID, db: Session) -> Asset:
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.post("/", response_model=DependencyRead, status_code=status.HTTP_201_CREATED)
def create_dependency(payload: DependencyCreate, db: DbSession) -> Dependency:
    if payload.source_asset_id == payload.target_asset_id:
        raise HTTPException(
            status_code=400,
            detail="Source and target assets must be different",
        )

    _get_asset_or_404(payload.source_asset_id, db)
    _get_asset_or_404(payload.target_asset_id, db)

    dependency = Dependency(**payload.model_dump())
    db.add(dependency)
    db.commit()
    db.refresh(dependency)

    return dependency


@router.get("/", response_model=list[DependencyRead])
def list_dependencies(db: DbSession) -> list[Dependency]:
    return db.query(Dependency).order_by(Dependency.id).all()


@router.get("/{dependency_id}", response_model=DependencyRead)
def get_dependency(dependency_id: UUID, db: DbSession) -> Dependency:
    dependency = db.get(Dependency, dependency_id)

    if dependency is None:
        raise HTTPException(status_code=404, detail="Dependency not found")

    return dependency


@router.patch("/{dependency_id}", response_model=DependencyRead)
def update_dependency(dependency_id: UUID, payload: DependencyUpdate, db: DbSession) -> Dependency:
    dependency = db.get(Dependency, dependency_id)

    if dependency is None:
        raise HTTPException(status_code=404, detail="Dependency not found")

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(dependency, field, value)

    db.commit()
    db.refresh(dependency)

    return dependency


@router.delete("/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dependency(dependency_id: UUID, db: DbSession) -> None:
    dependency = db.get(Dependency, dependency_id)

    if dependency is None:
        raise HTTPException(status_code=404, detail="Dependency not found")

    db.delete(dependency)
    db.commit()