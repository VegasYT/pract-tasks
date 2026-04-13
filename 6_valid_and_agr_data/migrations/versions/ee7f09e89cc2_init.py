"""init

Revision ID: ee7f09e89cc2
Revises: 
Create Date: 2026-04-08 20:19:01.930258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ee7f09e89cc2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('company_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inn', sa.BigInteger(), nullable=True),
    sa.Column('okved', sa.String(), nullable=True),
    sa.Column('okved_description', sa.Text(), nullable=True),
    sa.Column('industry', sa.Text(), nullable=True),
    sa.Column('subject', sa.String(), nullable=True),
    sa.Column('district', sa.String(), nullable=True),
    sa.Column('current_business_value', sa.Float(), nullable=True),
    sa.Column('liquidation_value', sa.Float(), nullable=True),
    sa.Column('creditor_return_rate', sa.Float(), nullable=True),
    sa.Column('working_capital_need', sa.Float(), nullable=True),
    sa.Column('profit_before_tax', sa.Float(), nullable=True),
    sa.Column('tax_debt', sa.Float(), nullable=True),
    sa.Column('enforcement_debt', sa.Float(), nullable=True),
    sa.Column('guarantee_limit', sa.String(), nullable=True),
    sa.Column('solvency_rank', sa.Float(), nullable=True),
    sa.Column('organization_age', sa.Float(), nullable=True),
    sa.Column('bankruptcy_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('company_data')
