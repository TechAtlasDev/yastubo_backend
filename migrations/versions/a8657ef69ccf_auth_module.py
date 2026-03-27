"""auth_module

Revision ID: a8657ef69ccf
Revises: 45de20cdff89
Create Date: 2026-03-19 16:42:43.682737

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a8657ef69ccf"
down_revision: Union[str, Sequence[str], None] = "45de20cdff89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
