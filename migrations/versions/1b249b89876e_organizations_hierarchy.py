"""organizations_hierarchy_blindado_v2

Revision ID: 1b249b89876e
Revises: cfcc3aa64589
Create Date: 2026-03-31 10:38:00.000000
"""

import logging
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import app.shared.base_model

logger = logging.getLogger("alembic.runtime.migration")

revision: str = "1b249b89876e"
down_revision: Union[str, Sequence[str], None] = "cfcc3aa64589"

TABLES_TO_MIGRATE = [
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


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    logger.info(">>> PASO 1: Eliminación dinámica de FKs que apuntan a Workspaces")
    existing_tables = inspector.get_table_names()
    for table in TABLES_TO_MIGRATE + ["user_workspaces"]:
        if table in existing_tables:
            fks = inspector.get_foreign_keys(table)
            for fk in fks:
                if fk["referred_table"] in ["workspaces", "companies"]:
                    fk_name = fk["name"]
                    if fk_name:
                        logger.info(f"    [DROP FK] {fk_name} en {table}")
                        op.drop_constraint(fk_name, table, type_="foreignkey")

    logger.info(">>> PASO 2: Renombrado de tablas base")
    if "workspaces" in existing_tables and "companies" not in existing_tables:
        logger.info("    [ACCIÓN] Renombrando 'workspaces' -> 'companies'")
        op.rename_table("workspaces", "companies")

    if "user_workspaces" in existing_tables and "company_user" not in existing_tables:
        logger.info("    [ACCIÓN] Renombrando 'user_workspaces' -> 'company_user'")
        op.rename_table("user_workspaces", "company_user")

    # Refrescar inspector
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "companies" in existing_tables:
        logger.info(">>> PASO 3: Configurando 'companies'")
        cols = [c["name"] for c in inspector.get_columns("companies")]
        if "slug" in cols and "short_code" not in cols:
            logger.info("    [ACCIÓN] Renombrando 'slug' -> 'short_code'")
            op.alter_column(
                "companies", "slug", new_column_name="short_code", type_=sa.String(10)
            )

        for col_name, col_type in [
            ("phone", sa.String(50)),
            ("email", sa.String(191)),
            ("status", sa.String(32)),
        ]:
            if col_name not in cols:
                logger.info(f"    [ACCIÓN] Agregando columna '{col_name}'")
                op.add_column("companies", sa.Column(col_name, col_type, nullable=True))

    logger.info(">>> PASO 4: Actualizando workspace_id -> company_id")
    for table in TABLES_TO_MIGRATE:
        if table in existing_tables:
            cols = [c["name"] for c in inspector.get_columns(table)]
            if "workspace_id" in cols and "company_id" not in cols:
                logger.info(f"    [ACCIÓN] Renombrando columna en '{table}'")
                op.alter_column(table, "workspace_id", new_column_name="company_id")

            # Re-crear FK (Idempotente: Alembic suele manejar el error si ya existe, pero somos cautos)
            logger.info(f"    [ACCIÓN] Creando FK en '{table}'")
            op.create_foreign_key(
                f"fk_{table}_company",
                table,
                "companies",
                ["company_id"],
                ["id"],
                ondelete="CASCADE",
            )

    if "business_units" not in existing_tables:
        logger.info(">>> PASO 5: Creando business_units")
        op.create_table(
            "business_units",
            sa.Column("id", app.shared.base_model.GUID(), nullable=False),
            sa.Column("company_id", app.shared.base_model.GUID(), nullable=False),
            sa.Column("name", sa.String(191), nullable=False),
            sa.ForeignKeyConstraint(
                ["company_id"], ["companies.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    logger.info(">>> UPGRADE FINALIZADO")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    logger.info(">>> REVIRTIENDO MIGRACIÓN (Downgrade)")

    if "business_units" in existing_tables:
        op.drop_table("business_units")

    for table in TABLES_TO_MIGRATE:
        if table in existing_tables:
            fks = inspector.get_foreign_keys(table)
            for fk in fks:
                if fk["referred_table"] == "companies":
                    op.drop_constraint(fk["name"], table, type_="foreignkey")

            cols = [c["name"] for c in inspector.get_columns(table)]
            if "company_id" in cols and "workspace_id" not in cols:
                op.alter_column(table, "company_id", new_column_name="workspace_id")

    if "companies" in existing_tables and "workspaces" not in existing_tables:
        op.rename_table("companies", "workspaces")
    if "company_user" in existing_tables and "user_workspaces" not in existing_tables:
        op.rename_table("company_user", "user_workspaces")

    # CORRECCIÓN MENOR: Verificar que 'workspaces' exista antes de re-crear FKs
    inspector = sa.inspect(conn)
    current_tables = inspector.get_table_names()
    if "workspaces" in current_tables:
        logger.info(">>> Re-creando FKs originales hacia 'workspaces'")
        for table in TABLES_TO_MIGRATE + ["user_workspaces"]:
            if table in current_tables:
                op.create_foreign_key(
                    f"fk_{table}_workspace",
                    table,
                    "workspaces",
                    ["workspace_id"],
                    ["id"],
                    ondelete="CASCADE",
                )
