import uuid

from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    criticality: Mapped[int] = mapped_column(Integer, nullable=False)

    safety_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    extra_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    outgoing_dependencies = relationship(
        "Dependency",
        foreign_keys="Dependency.source_asset_id",
        back_populates="source_asset",
    )

    incoming_dependencies = relationship(
        "Dependency",
        foreign_keys="Dependency.target_asset_id",
        back_populates="target_asset",
    )
