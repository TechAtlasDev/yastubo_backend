"""payments_module

Revision ID: 32b4fc9d61a1
Revises: 046cf9ace8f0
Create Date: 2026-03-19 17:14:04.557552

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '32b4fc9d61a1'
down_revision: Union[str, Sequence[str], None] = '046cf9ace8f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
