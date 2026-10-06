"""baseline existing schema

Revision ID: 1a2f2297e131
Revises:
Create Date: 2026-10-06 10:20:25.741711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2f2297e131'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('text', sa.Text(), nullable=False)
    )

    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'ticket_id',
            sa.Integer(),
            sa.ForeignKey('tickets.id'),
            nullable=False
        ),
        sa.Column('category', sa.String(255), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('entities', sa.JSON(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('predictions')
    op.drop_table('tickets')
