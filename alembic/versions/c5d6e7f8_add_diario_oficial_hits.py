"""add_diario_oficial_hits

Revision ID: c5d6e7f8
Revises: a2b3c4d5
Create Date: 2026-06-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c5d6e7f8"
down_revision = "a2b3c4d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "diario_oficial_hits",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("keyword", sa.String(100), nullable=False),
        sa.Column("data_publicacao", sa.String(10), nullable=True),
        sa.Column("arquivo", sa.String(255), nullable=True),
        sa.Column("pagina", sa.Integer, nullable=True),
        sa.Column("highlight", sa.Text, nullable=True),
        sa.Column("municipio_detectado", sa.String(255), nullable=True),
        sa.Column(
            "municipio_id",
            sa.Integer,
            sa.ForeignKey("municipalities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("artista_detectado", sa.String(255), nullable=True),
        sa.Column("tipo_contratacao", sa.String(100), nullable=True),
        sa.Column("valor_estimado", sa.Numeric(14, 2), nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="novo"),
        sa.Column("raw_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_unique_constraint(
        "uq_diario_arquivo_pagina_kw", "diario_oficial_hits", ["arquivo", "pagina", "keyword"]
    )
    op.create_index("ix_diario_hits_data", "diario_oficial_hits", ["data_publicacao"])
    op.create_index("ix_diario_hits_municipio_id", "diario_oficial_hits", ["municipio_id"])
    op.create_index("ix_diario_hits_status", "diario_oficial_hits", ["status"])


def downgrade() -> None:
    op.drop_table("diario_oficial_hits")
