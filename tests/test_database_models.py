"""Valida que todos os models estão registrados corretamente no metadata do SQLAlchemy."""
import app.models  # noqa: F401 — importa todos os models
from app.database import Base

EXPECTED_TABLES = {
    "municipalities",
    "public_contacts",
    "municipal_events",
    "public_contracts",
    "artists",
    "artist_fees",
    "artist_regional_strength",
    "suppliers",
    "supplier_prices",
    "rodeo_budget_templates",
    "commercial_opportunities",
    "crawler_runs",
}


def test_all_expected_tables_registered():
    registered = set(Base.metadata.tables.keys())
    missing = EXPECTED_TABLES - registered
    assert not missing, f"Tabelas ausentes no metadata: {missing}"


def test_no_extra_tables_registered():
    registered = set(Base.metadata.tables.keys())
    extra = registered - EXPECTED_TABLES
    assert not extra, f"Tabelas inesperadas no metadata: {extra}"


def test_municipalities_columns():
    table = Base.metadata.tables["municipalities"]
    col_names = {c.name for c in table.columns}
    required = {"id", "name", "normalized_name", "state", "created_at", "updated_at"}
    assert required.issubset(col_names)


def test_public_contracts_columns():
    table = Base.metadata.tables["public_contracts"]
    col_names = {c.name for c in table.columns}
    required = {
        "id", "municipality_id", "event_id", "artist_id", "contract_type",
        "contract_value", "confidence_score", "extracted_json", "source_url",
    }
    assert required.issubset(col_names)


def test_commercial_opportunities_columns():
    table = Base.metadata.tables["commercial_opportunities"]
    col_names = {c.name for c in table.columns}
    required = {
        "id", "municipality_id", "opportunity_type", "status",
        "final_opportunity_score", "recommended_artists_json",
    }
    assert required.issubset(col_names)


def test_crawler_runs_columns():
    table = Base.metadata.tables["crawler_runs"]
    col_names = {c.name for c in table.columns}
    required = {
        "id", "crawler_name", "status", "started_at",
        "records_found", "records_created", "records_updated",
    }
    assert required.issubset(col_names)


def test_enums_importable():
    from app.models.enums import (
        ContractType,
        CrawlerStatus,
        EventType,
        OpportunityStatus,
        OpportunityType,
        ProcurementModality,
        SupplierCategory,
    )
    assert EventType.rodeio.value == "rodeio"
    assert ContractType.show_artistico.value == "show_artistico"
    assert OpportunityStatus.novo.value == "novo"
    assert CrawlerStatus.running.value == "running"


def test_all_models_importable():
    from app.models import (
        Artist,
        ArtistFee,
        ArtistRegionalStrength,
        CommercialOpportunity,
        CrawlerRun,
        MunicipalEvent,
        Municipality,
        PublicContact,
        PublicContract,
        RodeoBudgetTemplate,
        Supplier,
        SupplierPrice,
    )
    assert Municipality.__tablename__ == "municipalities"
    assert PublicContract.__tablename__ == "public_contracts"
    assert CommercialOpportunity.__tablename__ == "commercial_opportunities"
    assert CrawlerRun.__tablename__ == "crawler_runs"
