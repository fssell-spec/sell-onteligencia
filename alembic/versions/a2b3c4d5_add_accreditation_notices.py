"""add_accreditation_notices

Revision ID: a2b3c4d5
Revises: f1a2b3c4
Create Date: 2026-06-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a2b3c4d5"
down_revision = "f1a2b3c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accreditation_notices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "municipality_id",
            sa.Integer,
            sa.ForeignKey("municipalities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("numero_controle", sa.String(255), nullable=False, unique=True),
        sa.Column("objeto", sa.Text, nullable=True),
        sa.Column("valor_estimado", sa.Numeric(14, 2), nullable=True),
        sa.Column("data_publicacao", sa.Date, nullable=True),
        sa.Column("data_encerramento", sa.Date, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("contract_types_json", postgresql.JSONB, nullable=True),
        sa.Column("orgao_cnpj", sa.String(20), nullable=True),
        sa.Column("orgao_nome", sa.String(500), nullable=True),
        sa.Column("raw_json", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_accreditation_notices_municipality_id",
        "accreditation_notices",
        ["municipality_id"],
    )
    op.create_index(
        "ix_accreditation_notices_is_active",
        "accreditation_notices",
        ["is_active"],
    )
    op.create_index(
        "ix_accreditation_notices_data_publicacao",
        "accreditation_notices",
        ["data_publicacao"],
    )


def downgrade() -> None:
    op.drop_index("ix_accreditation_notices_data_publicacao", "accreditation_notices")
    op.drop_index("ix_accreditation_notices_is_active", "accreditation_notices")
    op.drop_index("ix_accreditation_notices_municipality_id", "accreditation_notices")
    op.drop_table("accreditation_notices")
