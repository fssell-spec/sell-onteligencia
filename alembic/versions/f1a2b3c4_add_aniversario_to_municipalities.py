"""add_aniversario_to_municipalities

Revision ID: f1a2b3c4
Revises: b4c19e26bcb8
Create Date: 2026-06-01

"""
from alembic import op
import sqlalchemy as sa

revision = "f1a2b3c4"
down_revision = "e7a3b1c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("municipalities", sa.Column("aniversario_mes", sa.Integer(), nullable=True))
    op.add_column("municipalities", sa.Column("aniversario_dia", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("municipalities", "aniversario_dia")
    op.drop_column("municipalities", "aniversario_mes")
