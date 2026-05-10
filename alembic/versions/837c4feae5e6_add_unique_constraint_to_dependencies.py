"""add unique constraint to dependencies

Revision ID: 837c4feae5e6
Revises: 75484be13d27
Create Date: 2026-05-10 15:12:33.380111

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "837c4feae5e6"
down_revision: str | Sequence[str] | None = "75484be13d27"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_dependency_edge",
        "dependencies",
        ["source_asset_id", "target_asset_id", "dependency_type"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_dependency_edge",
        "dependencies",
        type_="unique",
    )