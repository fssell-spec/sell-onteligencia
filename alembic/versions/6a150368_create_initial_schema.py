"""create_initial_schema

Revision ID: 6a150368
Revises:
Create Date: 2026-05-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "6a150368"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Enums (create_type=False: criados explicitamente abaixo para evitar dupla criação) ---
    event_type_enum = postgresql.ENUM(
        "aniversario_cidade", "expoagro", "festa_peao", "rodeio", "carnaval",
        "reveillon", "festival_cultural", "festa_tradicional", "outro",
        name="event_type_enum", create_type=False,
    )
    contract_type_enum = postgresql.ENUM(
        "show_artistico", "rodeio_completo", "estrutura_evento", "som_luz",
        "seguranca", "banheiro_quimico", "arquibancada", "arena", "gerador",
        "portaria", "alimentacao", "limpeza", "producao", "outro",
        name="contract_type_enum", create_type=False,
    )
    procurement_modality_enum = postgresql.ENUM(
        "inexigibilidade", "dispensa", "pregao", "concorrencia",
        "credenciamento", "outro", "desconhecido",
        name="procurement_modality_enum", create_type=False,
    )
    supplier_category_enum = postgresql.ENUM(
        "arena", "arquibancada", "banheiro_quimico", "seguranca", "brigadista",
        "som", "luz", "led", "gerador", "portaria", "alimentacao", "limpeza",
        "producao", "outro",
        name="supplier_category_enum", create_type=False,
    )
    opportunity_type_enum = postgresql.ENUM(
        "venda_show", "venda_rodeio", "evento_completo", "estrutura_evento",
        name="opportunity_type_enum", create_type=False,
    )
    opportunity_status_enum = postgresql.ENUM(
        "novo", "pesquisar", "abordar", "em_contato", "proposta_enviada",
        "negociacao", "ganho", "perdido", "suspenso",
        name="opportunity_status_enum", create_type=False,
    )
    crawler_status_enum = postgresql.ENUM(
        "running", "success", "failed", "partial",
        name="crawler_status_enum", create_type=False,
    )

    for name, values in [
        ("event_type_enum", ["aniversario_cidade", "expoagro", "festa_peao", "rodeio", "carnaval", "reveillon", "festival_cultural", "festa_tradicional", "outro"]),
        ("contract_type_enum", ["show_artistico", "rodeio_completo", "estrutura_evento", "som_luz", "seguranca", "banheiro_quimico", "arquibancada", "arena", "gerador", "portaria", "alimentacao", "limpeza", "producao", "outro"]),
        ("procurement_modality_enum", ["inexigibilidade", "dispensa", "pregao", "concorrencia", "credenciamento", "outro", "desconhecido"]),
        ("supplier_category_enum", ["arena", "arquibancada", "banheiro_quimico", "seguranca", "brigadista", "som", "luz", "led", "gerador", "portaria", "alimentacao", "limpeza", "producao", "outro"]),
        ("opportunity_type_enum", ["venda_show", "venda_rodeio", "evento_completo", "estrutura_evento"]),
        ("opportunity_status_enum", ["novo", "pesquisar", "abordar", "em_contato", "proposta_enviada", "negociacao", "ganho", "perdido", "suspenso"]),
        ("crawler_status_enum", ["running", "success", "failed", "partial"]),
    ]:
        quoted = ", ".join(f"'{v}'" for v in values)
        op.execute(f"CREATE TYPE {name} AS ENUM ({quoted})")

    # --- municipalities ---
    op.create_table(
        "municipalities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.Column("state", sa.String(2), nullable=False, server_default="MS"),
        sa.Column("population", sa.Integer, nullable=True),
        sa.Column("region", sa.String(255), nullable=True),
        sa.Column("official_website", sa.String(500), nullable=True),
        sa.Column("transparency_url", sa.String(500), nullable=True),
        sa.Column("official_gazette_url", sa.String(500), nullable=True),
        sa.Column("instagram_url", sa.String(500), nullable=True),
        sa.Column("facebook_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("normalized_name", "state", name="uq_municipality_name_state"),
    )
    op.create_index("ix_municipalities_name", "municipalities", ["name"])
    op.create_index("ix_municipalities_normalized_name", "municipalities", ["normalized_name"])
    op.create_index("ix_municipalities_state", "municipalities", ["state"])

    # --- public_contacts ---
    op.create_table(
        "public_contacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("municipality_id", sa.Integer, sa.ForeignKey("municipalities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("whatsapp", sa.String(50), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_public_contacts_municipality_id", "public_contacts", ["municipality_id"])
    op.create_index("ix_public_contacts_role", "public_contacts", ["role"])
    op.create_index("ix_public_contacts_department", "public_contacts", ["department"])

    # --- artists ---
    op.create_table(
        "artists",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False, unique=True),
        sa.Column("main_style", sa.String(100), nullable=True),
        sa.Column("sub_style", sa.String(100), nullable=True),
        sa.Column("booking_office", sa.String(255), nullable=True),
        sa.Column("booking_contact", sa.String(255), nullable=True),
        sa.Column("origin_city", sa.String(255), nullable=True),
        sa.Column("origin_state", sa.String(2), nullable=True),
        sa.Column("official_instagram", sa.String(255), nullable=True),
        sa.Column("official_website", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_artists_name", "artists", ["name"])
    op.create_index("ix_artists_normalized_name", "artists", ["normalized_name"])
    op.create_index("ix_artists_main_style", "artists", ["main_style"])
    op.create_index("ix_artists_sub_style", "artists", ["sub_style"])

    # --- municipal_events ---
    op.create_table(
        "municipal_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("municipality_id", sa.Integer, sa.ForeignKey("municipalities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.Column("event_type", event_type_enum, nullable=False, server_default="outro"),
        sa.Column("usual_month", sa.Integer, nullable=True),
        sa.Column("estimated_start_date", sa.Date, nullable=True),
        sa.Column("estimated_end_date", sa.Date, nullable=True),
        sa.Column("recurrence_pattern", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_municipal_events_municipality_id", "municipal_events", ["municipality_id"])
    op.create_index("ix_municipal_events_event_type", "municipal_events", ["event_type"])
    op.create_index("ix_municipal_events_usual_month", "municipal_events", ["usual_month"])
    op.create_index("ix_municipal_events_normalized_name", "municipal_events", ["normalized_name"])

    # --- public_contracts ---
    op.create_table(
        "public_contracts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("municipality_id", sa.Integer, sa.ForeignKey("municipalities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_id", sa.Integer, sa.ForeignKey("municipal_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("artist_id", sa.Integer, sa.ForeignKey("artists.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contract_type", contract_type_enum, nullable=False, server_default="outro"),
        sa.Column("object_description", sa.Text, nullable=True),
        sa.Column("supplier_name", sa.String(255), nullable=True),
        sa.Column("supplier_document", sa.String(20), nullable=True),
        sa.Column("contract_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("publication_date", sa.Date, nullable=True),
        sa.Column("event_date", sa.Date, nullable=True),
        sa.Column("process_number", sa.String(255), nullable=True),
        sa.Column("procurement_modality", procurement_modality_enum, nullable=False, server_default="desconhecido"),
        sa.Column("source_name", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("extracted_json", postgresql.JSONB, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_public_contracts_municipality_id", "public_contracts", ["municipality_id"])
    op.create_index("ix_public_contracts_event_id", "public_contracts", ["event_id"])
    op.create_index("ix_public_contracts_artist_id", "public_contracts", ["artist_id"])
    op.create_index("ix_public_contracts_contract_type", "public_contracts", ["contract_type"])
    op.create_index("ix_public_contracts_publication_date", "public_contracts", ["publication_date"])
    op.create_index("ix_public_contracts_event_date", "public_contracts", ["event_date"])
    op.create_index("ix_public_contracts_supplier_name", "public_contracts", ["supplier_name"])
    op.create_index("ix_public_contracts_supplier_document", "public_contracts", ["supplier_document"])
    op.create_index("ix_public_contracts_process_number", "public_contracts", ["process_number"])

    # --- artist_fees ---
    op.create_table(
        "artist_fees",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("artist_id", sa.Integer, sa.ForeignKey("artists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("municipality_id", sa.Integer, sa.ForeignKey("municipalities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contract_id", sa.Integer, sa.ForeignKey("public_contracts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("value", sa.Numeric(14, 2), nullable=False),
        sa.Column("date", sa.Date, nullable=True),
        sa.Column("source_type", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_artist_fees_artist_id", "artist_fees", ["artist_id"])
    op.create_index("ix_artist_fees_municipality_id", "artist_fees", ["municipality_id"])
    op.create_index("ix_artist_fees_contract_id", "artist_fees", ["contract_id"])
    op.create_index("ix_artist_fees_date", "artist_fees", ["date"])
    op.create_index("ix_artist_fees_value", "artist_fees", ["value"])

    # --- artist_regional_strength ---
    op.create_table(
        "artist_regional_strength",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("artist_id", sa.Integer, sa.ForeignKey("artists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("region", sa.String(255), nullable=True),
        sa.Column("state", sa.String(2), nullable=False, server_default="MS"),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("spotify_score", sa.Float, nullable=True),
        sa.Column("youtube_score", sa.Float, nullable=True),
        sa.Column("google_trends_score", sa.Float, nullable=True),
        sa.Column("public_contracts_score", sa.Float, nullable=True),
        sa.Column("final_score", sa.Float, nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_artist_regional_strength_artist_id", "artist_regional_strength", ["artist_id"])
    op.create_index("ix_artist_regional_strength_state", "artist_regional_strength", ["state"])
    op.create_index("ix_artist_regional_strength_city", "artist_regional_strength", ["city"])
    op.create_index("ix_artist_regional_strength_final_score", "artist_regional_strength", ["final_score"])

    # --- suppliers ---
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.Column("category", supplier_category_enum, nullable=False, server_default="outro"),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("service_region", sa.String(255), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("instagram", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_suppliers_name", "suppliers", ["name"])
    op.create_index("ix_suppliers_normalized_name", "suppliers", ["normalized_name"])
    op.create_index("ix_suppliers_category", "suppliers", ["category"])
    op.create_index("ix_suppliers_city", "suppliers", ["city"])
    op.create_index("ix_suppliers_state", "suppliers", ["state"])

    # --- supplier_prices ---
    op.create_table(
        "supplier_prices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("supplier_id", sa.Integer, sa.ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_description", sa.String(500), nullable=True),
        sa.Column("unit_type", sa.String(100), nullable=True),
        sa.Column("min_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("avg_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("max_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("source_type", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_supplier_prices_supplier_id", "supplier_prices", ["supplier_id"])
    op.create_index("ix_supplier_prices_unit_type", "supplier_prices", ["unit_type"])
    op.create_index("ix_supplier_prices_avg_price", "supplier_prices", ["avg_price"])

    # --- rodeo_budget_templates ---
    op.create_table(
        "rodeo_budget_templates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("event_size", sa.String(20), nullable=False),
        sa.Column("expected_audience", sa.Integer, nullable=True),
        sa.Column("duration_days", sa.Integer, nullable=True),
        sa.Column("required_items_json", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_rodeo_budget_templates_name", "rodeo_budget_templates", ["name"])
    op.create_index("ix_rodeo_budget_templates_event_size", "rodeo_budget_templates", ["event_size"])
    op.create_index("ix_rodeo_budget_templates_expected_audience", "rodeo_budget_templates", ["expected_audience"])

    # --- commercial_opportunities ---
    op.create_table(
        "commercial_opportunities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("municipality_id", sa.Integer, sa.ForeignKey("municipalities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", sa.Integer, sa.ForeignKey("municipal_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("opportunity_type", opportunity_type_enum, nullable=False),
        sa.Column("estimated_budget", sa.Numeric(14, 2), nullable=True),
        sa.Column("estimated_event_date", sa.Date, nullable=True),
        sa.Column("urgency_score", sa.Float, nullable=True),
        sa.Column("fit_score", sa.Float, nullable=True),
        sa.Column("margin_potential_score", sa.Float, nullable=True),
        sa.Column("final_opportunity_score", sa.Float, nullable=True),
        sa.Column("recommended_artists_json", postgresql.JSONB, nullable=True),
        sa.Column("recommended_structure_json", postgresql.JSONB, nullable=True),
        sa.Column("suggested_next_action", sa.Text, nullable=True),
        sa.Column("status", opportunity_status_enum, nullable=False, server_default="novo"),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("last_contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_commercial_opportunities_municipality_id", "commercial_opportunities", ["municipality_id"])
    op.create_index("ix_commercial_opportunities_event_id", "commercial_opportunities", ["event_id"])
    op.create_index("ix_commercial_opportunities_opportunity_type", "commercial_opportunities", ["opportunity_type"])
    op.create_index("ix_commercial_opportunities_status", "commercial_opportunities", ["status"])
    op.create_index("ix_commercial_opportunities_final_score", "commercial_opportunities", ["final_opportunity_score"])
    op.create_index("ix_commercial_opportunities_estimated_event_date", "commercial_opportunities", ["estimated_event_date"])
    op.create_index("ix_commercial_opportunities_next_action_at", "commercial_opportunities", ["next_action_at"])

    # --- crawler_runs ---
    op.create_table(
        "crawler_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("crawler_name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(100), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", crawler_status_enum, nullable=False, server_default="running"),
        sa.Column("records_found", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_crawler_runs_crawler_name", "crawler_runs", ["crawler_name"])
    op.create_index("ix_crawler_runs_source_type", "crawler_runs", ["source_type"])
    op.create_index("ix_crawler_runs_status", "crawler_runs", ["status"])
    op.create_index("ix_crawler_runs_started_at", "crawler_runs", ["started_at"])


def downgrade() -> None:
    op.drop_table("crawler_runs")
    op.drop_table("commercial_opportunities")
    op.drop_table("rodeo_budget_templates")
    op.drop_table("supplier_prices")
    op.drop_table("suppliers")
    op.drop_table("artist_regional_strength")
    op.drop_table("artist_fees")
    op.drop_table("public_contracts")
    op.drop_table("municipal_events")
    op.drop_table("artists")
    op.drop_table("public_contacts")
    op.drop_table("municipalities")

    for enum_name in [
        "crawler_status_enum", "opportunity_status_enum", "opportunity_type_enum",
        "supplier_category_enum", "procurement_modality_enum", "contract_type_enum",
        "event_type_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
