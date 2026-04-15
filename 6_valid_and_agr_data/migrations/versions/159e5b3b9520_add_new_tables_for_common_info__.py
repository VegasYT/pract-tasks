"""add_new_tables_for_common_info__:)

Revision ID: 159e5b3b9520
Revises: dbcc18cb95f2
Create Date: 2026-04-15 22:16:44.866778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '159e5b3b9520'
down_revision: Union[str, None] = 'dbcc18cb95f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('industry_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('industry', sa.Text(), nullable=False),
    sa.Column('current_business_value', sa.Float(), nullable=True),
    sa.Column('liquidation_value', sa.Float(), nullable=True),
    sa.Column('creditor_return_rate', sa.Float(), nullable=True),
    sa.Column('working_capital_need', sa.Float(), nullable=True),
    sa.Column('profit_before_tax', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('common_info_county',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('county_id', sa.Integer(), nullable=False),
    sa.Column('district', sa.String(), nullable=False),
    sa.Column('total_companies', sa.Integer(), nullable=False),
    sa.Column('companies_with_business_value', sa.Integer(), nullable=False),
    sa.Column('companies_with_profit', sa.Integer(), nullable=False),
    sa.Column('companies_without_debt', sa.Integer(), nullable=False),
    sa.Column('companies_with_solvency_rank', sa.Integer(), nullable=False),
    sa.Column('companies_with_roa', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['county_id'], ['county_data.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('county_id')
    )
    op.create_table('common_info_industry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('industry_id', sa.Integer(), nullable=False),
    sa.Column('industry', sa.Text(), nullable=False),
    sa.Column('total_companies', sa.Integer(), nullable=False),
    sa.Column('companies_with_business_value', sa.Integer(), nullable=False),
    sa.Column('companies_with_profit', sa.Integer(), nullable=False),
    sa.Column('companies_without_debt', sa.Integer(), nullable=False),
    sa.Column('companies_with_solvency_rank', sa.Integer(), nullable=False),
    sa.Column('companies_with_roa', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['industry_id'], ['industry_data.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('industry_id')
    )
    op.create_table('common_info_region',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('region_id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('total_companies', sa.Integer(), nullable=False),
    sa.Column('companies_with_business_value', sa.Integer(), nullable=False),
    sa.Column('companies_with_profit', sa.Integer(), nullable=False),
    sa.Column('companies_without_debt', sa.Integer(), nullable=False),
    sa.Column('companies_with_solvency_rank', sa.Integer(), nullable=False),
    sa.Column('companies_with_roa', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['region_id'], ['region_data.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('region_id')
    )


def downgrade() -> None:
    op.drop_table('common_info_region')
    op.drop_table('common_info_industry')
    op.drop_table('common_info_county')
    op.drop_table('industry_data')
