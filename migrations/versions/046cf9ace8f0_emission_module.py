"""emission_module

Revision ID: 046cf9ace8f0
Revises: 003765469a84
Create Date: 2026-03-19 17:03:12.980092

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '046cf9ace8f0'
down_revision: Union[str, Sequence[str], None] = '003765469a84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
