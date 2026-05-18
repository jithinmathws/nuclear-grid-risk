import uuid
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScenarioType(str, Enum):
    GRID_FAILURE = "grid_failure"
    COMPONENT_FAILURE = "component_failure"
    COMMON_MODE_FAILURE = "common_mode_failure"
    CYBER_EVENT = "cyber_event"
    NATURAL_HAZARD = "natural_hazard"


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    scenario_type: Mapped[ScenarioType] = mapped_column(
        SqlEnum(ScenarioType, name="scenario_type"),
        nullable=False,
    )

    initial_failed_asset_ids: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    assumptions: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    propagation_threshold: Mapped[float] = mapped_column(
        Float,
        default=0.7,
        nullable=False,
    )

    max_time_minutes: Mapped[int] = mapped_column(
        Integer,
        default=120,
        nullable=False,
    )