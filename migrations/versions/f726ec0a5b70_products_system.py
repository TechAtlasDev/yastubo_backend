"""products_system

Revision ID: f726ec0a5b70
Revises: ce81c153f259
Create Date: 2026-03-31 12:11:37.895015

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.shared.base_model

# revision identifiers, used by Alembic.
revision: str = "f726ec0a5b70"
down_revision: Union[str, Sequence[str], None] = "ce81c153f259"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Crear tabla de Productos (Entidad Raíz)
    op.create_table(
        "products",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)

    # 2. Modificar tabla de Planes para vincular a Productos
    op.add_column(
        "plans", sa.Column("product_id", app.shared.base_model.GUID(), nullable=True)
    )
    op.create_foreign_key(
        None, "plans", "products", ["product_id"], ["id"], ondelete="CASCADE"
    )

    op.drop_column("plans", "terms_es")
    op.drop_column("plans", "max_entry_age")
    op.drop_column("plans", "currency")
    op.drop_column("plans", "stripe_price_id")
    op.drop_column("plans", "max_renewal_age")
    op.drop_column("plans", "repatriation_countries")
    op.drop_column("plans", "terms_en")
    op.drop_column("plans", "base_price")
    op.drop_column("plans", "vesting_suicide_days")
    op.drop_column("plans", "vesting_natural_days")
    op.drop_column("plans", "vesting_accidental_days")

    # 3. Actualizar PlanVersion
    op.add_column(
        "plan_versions",
        sa.Column("cost_price", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column(
        "plan_versions",
        sa.Column("public_price", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column(
        "plan_versions",
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="USD"
        ),
    )
    op.add_column(
        "plan_versions", sa.Column("max_entry_age", sa.Integer(), nullable=True)
    )
    op.add_column(
        "plan_versions", sa.Column("max_renewal_age", sa.Integer(), nullable=True)
    )
    op.add_column(
        "plan_versions",
        sa.Column("wtime_suicide", sa.Integer(), nullable=False, server_default="365"),
    )
    op.add_column(
        "plan_versions",
        sa.Column(
            "wtime_preexisting", sa.Integer(), nullable=False, server_default="180"
        ),
    )
    op.add_column(
        "plan_versions",
        sa.Column("wtime_accident", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("plan_versions", sa.Column("terms_es", sa.Text(), nullable=True))
    op.add_column("plan_versions", sa.Column("terms_en", sa.Text(), nullable=True))
    op.add_column(
        "plan_versions",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.drop_column("plan_versions", "snapshot")

    # 4. Crear nuevas tablas satélite
    op.create_table(
        "plan_version_age_surcharges",
        sa.Column("plan_version_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("min_age", sa.Integer(), nullable=False),
        sa.Column("max_age", sa.Integer(), nullable=False),
        sa.Column(
            "surcharge_percentage", sa.Numeric(precision=5, scale=2), nullable=False
        ),
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint("min_age <= max_age", name="check_age_order"),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["plan_versions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plan_version_age_surcharges_id"),
        "plan_version_age_surcharges",
        ["id"],
        unique=False,
    )

    op.create_table(
        "plan_version_countries",
        sa.Column("plan_version_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("country_name", sa.String(length=100), nullable=False),
        sa.Column("price_override", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["plan_versions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "plan_version_id", "country_code", name="uq_plan_version_country"
        ),
    )
    op.create_index(
        op.f("ix_plan_version_countries_id"),
        "plan_version_countries",
        ["id"],
        unique=False,
    )

    op.create_table(
        "plan_version_coverages",
        sa.Column("plan_version_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("coverage_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("value_int", sa.Integer(), nullable=True),
        sa.Column("value_decimal", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("value_text", sa.JSON(), nullable=True),
        sa.Column("notes", sa.JSON(), nullable=True),
        sa.Column("is_included", sa.Boolean(), nullable=False),
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["coverage_id"], ["coverages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["plan_versions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plan_version_coverages_id"),
        "plan_version_coverages",
        ["id"],
        unique=False,
    )

    op.create_table(
        "plan_version_repatriation_countries",
        sa.Column("plan_version_id", app.shared.base_model.GUID(), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("country_name", sa.String(length=100), nullable=False),
        sa.Column("id", app.shared.base_model.GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["plan_versions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plan_version_repatriation_countries_id"),
        "plan_version_repatriation_countries",
        ["id"],
        unique=False,
    )

    # 5. ELIMINAR Tablas Viejas
    op.drop_index(op.f("ix_country_configs_id"), table_name="country_configs")
    # op.drop_table('country_configs') # Keep them for now if we want to be safe, but you asked to drop them
    op.drop_table("country_configs")
    op.drop_index(op.f("ix_age_ranges_id"), table_name="age_ranges")
    op.drop_table("age_ranges")
    op.drop_table("plan_coverages")

    op.drop_column("coverages", "notes_es")
    op.drop_column("coverages", "limit_amount")
    op.drop_column("coverages", "limit_unit")
    op.drop_column("coverages", "notes_en")


def downgrade() -> None:
    """Downgrade schema."""
    pass
