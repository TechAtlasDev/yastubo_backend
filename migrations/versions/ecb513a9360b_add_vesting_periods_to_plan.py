"""add_vesting_periods_to_plan

Revision ID: ecb513a9360b
Revises: 32b4fc9d61a1
Create Date: 2026-03-26 23:47:13.956306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ecb513a9360b'
down_revision: Union[str, Sequence[str], None] = '32b4fc9d61a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('plans', sa.Column('vesting_accidental_days', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('plans', sa.Column('vesting_natural_days', sa.Integer(), nullable=False, server_default='180'))
    op.add_column('plans', sa.Column('vesting_suicide_days', sa.Integer(), nullable=False, server_default='365'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('plans', 'vesting_accidental_days')
    op.drop_column('plans', 'vesting_natural_days')
    op.drop_column('plans', 'vesting_suicide_days')
