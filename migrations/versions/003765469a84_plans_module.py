"""plans_module

Revision ID: 003765469a84
Revises: a8657ef69ccf
Create Date: 2026-03-19 16:55:05.158823

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '003765469a84'
down_revision: Union[str, Sequence[str], None] = 'a8657ef69ccf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
