"""add_region_county_tables

Revision ID: dbcc18cb95f2
Revises: ee7f09e89cc2
Create Date: 2026-04-13 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'dbcc18cb95f2'
down_revision: Union[str, None] = 'ee7f09e89cc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'region_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('current_business_value', sa.Float(), nullable=True),
        sa.Column('liquidation_value', sa.Float(), nullable=True),
        sa.Column('creditor_return_rate', sa.Float(), nullable=True),
        sa.Column('working_capital_need', sa.Float(), nullable=True),
        sa.Column('profit_before_tax', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'county_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('district', sa.String(), nullable=False),
        sa.Column('current_business_value', sa.Float(), nullable=True),
        sa.Column('liquidation_value', sa.Float(), nullable=True),
        sa.Column('creditor_return_rate', sa.Float(), nullable=True),
        sa.Column('working_capital_need', sa.Float(), nullable=True),
        sa.Column('profit_before_tax', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('county_data')
    op.drop_table('region_data')
