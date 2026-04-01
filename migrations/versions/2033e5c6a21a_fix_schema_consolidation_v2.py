"""fix_schema_consolidation_v2

Revision ID: 2033e5c6a21a
Revises: de5c8d34c5bc
Create Date: 2026-03-31 22:15:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import app.shared.base_model

# revision identifiers, used by Alembic.
revision: str = "2033e5c6a21a"
down_revision: Union[str, Sequence[str], None] = "de5c8d34c5bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear tipos ENUM explícitamente (Regla 1)
    op.execute(
        "DO $$ BEGIN CREATE TYPE genderenum AS ENUM ('male', 'female', 'other'); EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE preferredlanguageenum AS ENUM ('es', 'en'); EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE contactviaenum AS ENUM ('email', 'whatsapp', 'sms'); EXCEPTION WHEN duplicate_object THEN null; END $$;"
    )

    # 2. Tablas nuevas e Índices (Idempotencia básica)
    op.create_table(
        "memberships_business_unit",
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("business_unit_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("user_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("role_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), server_default="active", nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["business_unit_id"],
            ["business_units.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Parchear tablas existentes: Business Units
    op.add_column(
        "business_units",
        sa.Column("parent_id", app.shared.base_model.GUID(), nullable=True),
    )
    op.add_column(
        "business_units",
        sa.Column(
            "type", sa.String(length=20), nullable=False, server_default="office"
        ),
    )
    op.add_column(
        "business_units",
        sa.Column(
            "status", sa.String(length=20), server_default="active", nullable=False
        ),
    )
    op.add_column(
        "business_units",
        sa.Column("branding_text_dark", sa.String(length=12), nullable=True),
    )
    op.add_column(
        "business_units",
        sa.Column("branding_bg_light", sa.String(length=12), nullable=True),
    )
    op.add_column(
        "business_units",
        sa.Column("branding_text_light", sa.String(length=12), nullable=True),
    )
    op.add_column(
        "business_units",
        sa.Column("branding_bg_dark", sa.String(length=12), nullable=True),
    )
    op.add_column(
        "business_units",
        sa.Column("branding_logo_file_id", sa.BigInteger(), nullable=True),
    )
    op.create_index(
        op.f("ix_business_units_id"), "business_units", ["id"], unique=False
    )
    op.create_foreign_key(
        None, "business_units", "business_units", ["parent_id"], ["id"]
    )

    # 4. Parchear tablas existentes: Companies
    op.add_column(
        "companies",
        sa.Column("branding_text_dark", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "companies", sa.Column("branding_bg_light", sa.String(length=16), nullable=True)
    )
    op.add_column(
        "companies",
        sa.Column("branding_text_light", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "companies", sa.Column("branding_bg_dark", sa.String(length=16), nullable=True)
    )
    op.add_column(
        "companies", sa.Column("branding_logo_file_id", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "companies", sa.Column("pdf_template_id", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "companies",
        sa.Column(
            "commission_beneficiary_user_id",
            app.shared.base_model.GUID(),
            nullable=True,
        ),
    )
    op.alter_column("companies", "name", type_=sa.Text())
    op.alter_column("companies", "description", type_=sa.Text())
    op.alter_column("companies", "status", nullable=False)
    op.execute("DROP INDEX IF EXISTS ix_workspaces_id")
    op.execute("DROP INDEX IF EXISTS ix_workspaces_slug")
    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)
    op.create_index(
        op.f("ix_companies_short_code"), "companies", ["short_code"], unique=True
    )
    op.create_foreign_key(
        None,
        "companies",
        "users",
        ["commission_beneficiary_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 5. Parchear tablas existentes: Company User
    op.add_column(
        "company_user",
        sa.Column(
            "id",
            app.shared.base_model.GUID(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )
    op.add_column(
        "company_user",
        sa.Column("company_id", app.shared.base_model.GUID(), nullable=True),
    )
    op.add_column(
        "company_user",
        sa.Column("basic_functions", sa.String(length=191), nullable=True),
    )
    op.add_column(
        "company_user",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.add_column(
        "company_user",
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
    )
    # Migrar datos si es necesario (asumiendo entorno limpio o que workspace_id es company_id)
    op.execute(
        "UPDATE company_user SET company_id = workspace_id WHERE company_id IS NULL"
    )
    op.alter_column("company_user", "company_id", nullable=False)
    op.create_foreign_key(
        None, "company_user", "companies", ["company_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_column("company_user", "workspace_id")

    # 6. Parchear tablas existentes: Customer Profiles (ENUMS reales)
    op.add_column(
        "customer_profiles",
        sa.Column("residence_address_json", sa.JSON(), nullable=True),
    )
    op.add_column(
        "customer_profiles",
        sa.Column("is_public", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("customer_profiles", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column(
        "customer_profiles", sa.Column("notes_admin", sa.Text(), nullable=True)
    )

    # Cambio de tipo a ENUM con CAST explícito
    op.execute(
        "ALTER TABLE customer_profiles ALTER COLUMN gender TYPE genderenum USING gender::text::genderenum"
    )
    op.execute(
        "ALTER TABLE customer_profiles ALTER COLUMN preferred_language TYPE preferredlanguageenum USING preferred_language::text::preferredlanguageenum"
    )
    op.execute(
        "ALTER TABLE customer_profiles ALTER COLUMN contact_via TYPE contactviaenum USING contact_via::text::contactviaenum"
    )
    op.alter_column("customer_profiles", "preferred_language", nullable=True)
    op.alter_column("customer_profiles", "contact_via", nullable=True)

    # 7. Limpieza de columnas obsoletas
    op.drop_column("customer_profiles", "emergency_relation")
    op.drop_column("customer_profiles", "billing_address_json")
    op.drop_column("customer_profiles", "tags")
    op.drop_column("customer_profiles", "emergency_name")
    op.drop_column("customer_profiles", "billing_name")
    op.drop_column("customer_profiles", "emergency_phone_e164")
    op.drop_column("customer_profiles", "notes_internal")
    op.drop_column("customer_profiles", "tax_id")

    # 8. Staff Profiles
    op.add_column(
        "staff_profiles", sa.Column("job_title", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "staff_profiles", sa.Column("department", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "staff_profiles",
        sa.Column("internal_phone", sa.String(length=50), nullable=True),
    )
    op.drop_column("staff_profiles", "commission_capitados_pct")
    op.drop_column("staff_profiles", "commission_regular_first_year_pct")
    op.drop_column("staff_profiles", "work_phone")
    op.drop_column("staff_profiles", "commission_regular_renewal_pct")

    # 9. Índices de búsqueda (Audit & Knowledge)
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_workspace_id")
    op.create_index(
        op.f("ix_audit_logs_company_id"), "audit_logs", ["company_id"], unique=False
    )
    op.execute("DROP INDEX IF EXISTS ix_knowledge_documents_workspace_id")
    op.create_index(
        op.f("ix_knowledge_documents_company_id"),
        "knowledge_documents",
        ["company_id"],
        unique=False,
    )


def downgrade() -> None:
    pass
