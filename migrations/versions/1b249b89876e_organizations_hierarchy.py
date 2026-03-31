"""organizations_hierarchy

Revision ID: 1b249b89876e
Revises: cfcc3aa64589
Create Date: 2026-03-31 10:38:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.shared.base_model


# revision identifiers, used by Alembic.
revision: str = "1b249b89876e"
down_revision: Union[str, Sequence[str], None] = "cfcc3aa64589"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Dropear todos los FK constraints que apuntan a workspaces
    tables_with_fk = [
        "audit_logs",
        "chat_conversations",
        "clients",
        "commission_distributions",
        "knowledge_documents",
        "leads",
        "plans",
        "policies",
        "subscriptions",
        "transactions",
        "user_workspaces",
    ]
    for table in tables_with_fk:
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {table}_workspace_id_fkey"
        )

    # 2. Dropear índices de workspaces
    op.execute("DROP INDEX IF EXISTS ix_workspaces_slug")
    op.execute("DROP INDEX IF EXISTS ix_workspaces_id")

    # 3. Renombrar las tablas base
    op.rename_table("workspaces", "companies")
    op.rename_table("user_workspaces", "company_user")

    # 4. Transformar 'companies'
    op.alter_column(
        "companies", "slug", new_column_name="short_code", type_=sa.String(length=10)
    )
    op.alter_column("companies", "name", type_=sa.Text())
    op.alter_column("companies", "description", type_=sa.Text())

    op.add_column("companies", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("companies", sa.Column("email", sa.String(length=191), nullable=True))
    op.add_column(
        "companies",
        sa.Column(
            "status", sa.String(length=32), server_default="active", nullable=False
        ),
    )
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

    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)
    op.create_index(
        op.f("ix_companies_short_code"), "companies", ["short_code"], unique=True
    )
    op.create_foreign_key(
        "companies_commission_beneficiary_user_id_fkey",
        "companies",
        "users",
        ["commission_beneficiary_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 5. Transformar 'company_user'
    op.alter_column("company_user", "workspace_id", new_column_name="company_id")
    op.add_column(
        "company_user", sa.Column("id", app.shared.base_model.GUID(), nullable=True)
    )
    op.execute("UPDATE company_user SET id = gen_random_uuid() WHERE id IS NULL")
    op.alter_column("company_user", "id", nullable=False)
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

    op.drop_constraint("user_workspaces_pkey", "company_user", type_="primary")
    op.create_primary_key("company_user_pkey", "company_user", ["id"])
    op.create_foreign_key(
        "company_user_company_id_fkey",
        "company_user",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 6. Transformar resto de tablas (Renombrar columna + índices + FKs)
    other_tables = [
        "audit_logs",
        "chat_conversations",
        "clients",
        "commission_distributions",
        "knowledge_documents",
        "leads",
        "plans",
        "policies",
        "subscriptions",
        "transactions",
    ]
    for table in other_tables:
        op.alter_column(table, "workspace_id", new_column_name="company_id")
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_workspace_id")
        op.create_index(
            op.f(f"ix_{table}_company_id"), table, ["company_id"], unique=False
        )
        op.create_foreign_key(
            f"{table}_company_id_fkey",
            table,
            "companies",
            ["company_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # 7. Crear business_units y memberships
    op.create_table(
        "business_units",
        sa.Column("company_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("parent_id", app.shared.base_model.GUID(), nullable=True),
        sa.Column("name", sa.String(length=191), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
        ),
        sa.Column("branding_text_dark", sa.String(length=12), nullable=True),
        sa.Column("branding_bg_light", sa.String(length=12), nullable=True),
        sa.Column("branding_text_light", sa.String(length=12), nullable=True),
        sa.Column("branding_bg_dark", sa.String(length=12), nullable=True),
        sa.Column("branding_logo_file_id", sa.BigInteger(), nullable=True),
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="business_units_company_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["business_units.id"], name="business_units_parent_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_business_units_id"), "business_units", ["id"], unique=False
    )

    op.create_table(
        "memberships_business_unit",
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("business_unit_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("user_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("role_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
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
            name="memberships_bu_unit_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="memberships_bu_role_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="memberships_bu_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 8. Geografía
    op.alter_column(
        "countries",
        "id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "country_zone",
        "zone_id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "country_zone",
        "country_id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "zones",
        "id",
        existing_type=sa.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=False,
        autoincrement=True,
    )


def downgrade() -> None:
    # Reverse Geografía
    op.alter_column(
        "zones",
        "id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "country_zone",
        "country_id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_nullable=False,
    )
    op.alter_column(
        "country_zone",
        "zone_id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_nullable=False,
    )
    op.alter_column(
        "countries",
        "id",
        existing_type=sa.Integer(),
        type_=sa.BIGINT(),
        existing_nullable=False,
        autoincrement=True,
    )

    # 1. Dropear FKs de companies (nombres explícitos)
    other_tables = [
        "audit_logs",
        "chat_conversations",
        "clients",
        "commission_distributions",
        "knowledge_documents",
        "leads",
        "plans",
        "policies",
        "subscriptions",
        "transactions",
    ]
    for table in other_tables:
        op.drop_constraint(f"{table}_company_id_fkey", table, type_="foreignkey")
    op.drop_constraint(
        "company_user_company_id_fkey", "company_user", type_="foreignkey"
    )

    # 2. Dropear tablas nuevas
    op.drop_table("memberships_business_unit")
    op.drop_table("business_units")

    # 3. Renombrar tablas inversamente
    op.rename_table("companies", "workspaces")
    op.rename_table("company_user", "user_workspaces")

    # 4. Revertir columnas e índices
    for table in other_tables + ["user_workspaces"]:
        op.alter_column(table, "company_id", new_column_name="workspace_id")
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_company_id")
        op.create_index(
            op.f(f"ix_{table}_workspace_id"), table, ["workspace_id"], unique=False
        )
        op.create_foreign_key(
            f"{table}_workspace_id_fkey",
            table,
            "workspaces",
            ["workspace_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # 5. Revertir user_workspaces (company_user)
    op.drop_constraint("company_user_pkey", "user_workspaces", type_="primary")
    op.create_primary_key(
        "user_workspaces_pkey", "user_workspaces", ["user_id", "workspace_id"]
    )
    op.drop_column("user_workspaces", "id")
    op.drop_column("user_workspaces", "basic_functions")
    op.drop_column("user_workspaces", "created_at")
    op.drop_column("user_workspaces", "updated_at")

    # 6. Revertir workspaces (companies)
    op.execute("DROP INDEX IF EXISTS ix_companies_short_code")
    op.execute("DROP INDEX IF EXISTS ix_companies_id")

    op.drop_constraint(
        "companies_commission_beneficiary_user_id_fkey",
        "workspaces",
        type_="foreignkey",
    )
    op.drop_column("workspaces", "phone")
    op.drop_column("workspaces", "email")
    op.drop_column("workspaces", "status")
    op.drop_column("workspaces", "branding_text_dark")
    op.drop_column("workspaces", "branding_bg_light")
    op.drop_column("workspaces", "branding_text_light")
    op.drop_column("workspaces", "branding_bg_dark")
    op.drop_column("workspaces", "branding_logo_file_id")
    op.drop_column("workspaces", "pdf_template_id")
    op.drop_column("workspaces", "commission_beneficiary_user_id")

    op.alter_column(
        "workspaces", "short_code", new_column_name="slug", type_=sa.String(length=100)
    )
    op.alter_column("workspaces", "name", type_=sa.String(length=100))
    op.alter_column("workspaces", "description", type_=sa.String(length=255))

    op.create_index(op.f("ix_workspaces_id"), "workspaces", ["id"], unique=False)
    op.create_index(op.f("ix_workspaces_slug"), "workspaces", ["slug"], unique=True)
