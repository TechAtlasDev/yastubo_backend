"""add_reconciliation_status_to_batch_logs

Revision ID: de5c8d34c5bc
Revises: cb69a9898ec4
Create Date: 2026-03-31 14:00:16.250152

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "de5c8d34c5bc"
down_revision: Union[str, Sequence[str], None] = "cb69a9898ec4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "capitados_batch_logs",
        sa.Column(
            "reconciliation_status",
            sa.String(length=32),
            nullable=False,
            server_default="pendiente",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("capitados_batch_logs", "reconciliation_status")
