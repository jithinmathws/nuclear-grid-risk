import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id"),
        nullable=False,
    )

    scenario_name: Mapped[str] = mapped_column(String(120), nullable=False)

    parameters_snapshot: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    total_failed_assets: Mapped[int] = mapped_column(Integer, nullable=False)
    critical_assets_failed: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_asset_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    max_cascade_depth: Mapped[int] = mapped_column(Integer, nullable=False)
    earliest_failure_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    latest_failure_minute: Mapped[int] = mapped_column(Integer, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    events = relationship(
        "SimulationEvent",
        back_populates="run",
        cascade="all, delete-orphan",
    )


class SimulationEvent(Base):
    __tablename__ = "simulation_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("simulation_runs.id"),
        nullable=False,
    )

    asset_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    criticality: Mapped[float] = mapped_column(Float, nullable=False)
    state: Mapped[str] = mapped_column(String(30), nullable=False)
    time_minute: Mapped[int] = mapped_column(Integer, nullable=False)

    caused_by_asset_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dependency_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    propagation_strength: Mapped[float | None] = mapped_column(Float, nullable=True)

    run = relationship(
        "SimulationRun",
        back_populates="events",
    )