"""add_artist_contract_appearances

Revision ID: e8f9a0b1
Revises: c5d6e7f8
Create Date: 2026-06-07

Tabela unificada de aparições de artistas em contratos (PNCP) e
menções em diários oficiais (DOE/DIOGRANDE), com link para artista
e município. Fonte única de verdade para histórico real de cachê.
"""
from alembic import op
import sqlalchemy as sa

revision = "e8f9a0b1"
down_revision = "c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artist_contract_appearances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "artist_id",
            sa.Integer(),
            sa.ForeignKey("artists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "municipality_id",
            sa.Integer(),
            sa.ForeignKey("municipalities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # 'pncp' | 'doe' | 'diogrande'
        sa.Column("source", sa.String(20), nullable=False),
        # PK no public_contracts ou diario_oficial_hits
        sa.Column("source_ref_id", sa.Integer(), nullable=True),
        # Valor pago/contratado — pode ser NULL se não constar no documento
        sa.Column("cache_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        # Nome original no documento antes do match
        sa.Column("raw_artist_name", sa.String(500), nullable=True),
        # 1.0 = match exato; 0.9 = contém; 0.7 = primeira palavra
        sa.Column("match_confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.create_index("ix_aca_artist_id", "artist_contract_appearances", ["artist_id"])
    op.create_index(
        "ix_aca_municipality_id", "artist_contract_appearances", ["municipality_id"]
    )
    op.create_index(
        "ix_aca_source_ref",
        "artist_contract_appearances",
        ["source", "source_ref_id"],
    )
    op.create_unique_constraint(
        "uq_aca_source_artist",
        "artist_contract_appearances",
        ["source", "source_ref_id", "artist_id"],
    )


def downgrade() -> None:
    op.drop_table("artist_contract_appearances")
