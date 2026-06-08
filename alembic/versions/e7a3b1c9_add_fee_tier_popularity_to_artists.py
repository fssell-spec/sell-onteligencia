"""add_fee_tier_popularity_to_artists

Revision ID: e7a3b1c9
Revises: b4c19e26bcb8
Create Date: 2026-06-01

"""
from alembic import op
import sqlalchemy as sa

revision = "e7a3b1c9"
down_revision = "b4c19e26bcb8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("artists", sa.Column("fee_tier", sa.String(50), nullable=True))
    op.add_column("artists", sa.Column("popularity_level", sa.String(50), nullable=True))
    op.create_index("ix_artists_fee_tier", "artists", ["fee_tier"])
    op.create_index("ix_artists_popularity_level", "artists", ["popularity_level"])


def downgrade() -> None:
    op.drop_index("ix_artists_popularity_level", table_name="artists")
    op.drop_index("ix_artists_fee_tier", table_name="artists")
    op.drop_column("artists", "popularity_level")
    op.drop_column("artists", "fee_tier")
