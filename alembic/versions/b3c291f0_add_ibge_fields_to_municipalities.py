"""add_ibge_fields_to_municipalities

Revision ID: b3c291f0
Revises: 6a150368
Create Date: 2026-05-30

"""
from alembic import op
import sqlalchemy as sa

revision = "b3c291f0"
down_revision = "6a150368"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("municipalities", sa.Column("ibge_code", sa.String(7), nullable=True))
    op.add_column("municipalities", sa.Column("area_km2", sa.Float(), nullable=True))
    op.add_column("municipalities", sa.Column("mesorregiao", sa.String(255), nullable=True))
    op.add_column("municipalities", sa.Column("microrregiao", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_municipalities_ibge_code", "municipalities", ["ibge_code"])
    op.create_index("ix_municipalities_ibge_code", "municipalities", ["ibge_code"])


def downgrade() -> None:
    op.drop_index("ix_municipalities_ibge_code", table_name="municipalities")
    op.drop_constraint("uq_municipalities_ibge_code", "municipalities", type_="unique")
    op.drop_column("municipalities", "microrregiao")
    op.drop_column("municipalities", "mesorregiao")
    op.drop_column("municipalities", "area_km2")
    op.drop_column("municipalities", "ibge_code")
