import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Dependency(Base):
    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id"),
        nullable=False,
    )

    target_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id"),
        nullable=False,
    )

    dependency_type: Mapped[str] = mapped_column(String(50), nullable=False)
    strength: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    redundancy_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    common_mode_group: Mapped[str | None] = mapped_column(String(100), nullable=True)

    failure_delay_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    extra_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    source_asset = relationship(
        "Asset",
        foreign_keys=[source_asset_id],
        back_populates="outgoing_dependencies",
    )

    target_asset = relationship(
        "Asset",
        foreign_keys=[target_asset_id],
        back_populates="incoming_dependencies",
    )
