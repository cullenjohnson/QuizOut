"""Player table

Revision ID: 9dfe9ff3bb55
Revises: 13df7a1ecda5
Create Date: 2025-07-31 01:18:24.488797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dfe9ff3bb55'
down_revision = '13df7a1ecda5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('player',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('last_played', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('player')
