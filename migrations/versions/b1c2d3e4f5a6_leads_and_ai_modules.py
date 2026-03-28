"""leads_and_ai_modules

Revision ID: b1c2d3e4f5a6
Revises: 32b4fc9d61a1
Create Date: 2026-03-28 11:17:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "32b4fc9d61a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create leads and AI module tables; enable pgvector extension."""

    # Enable pgvector extension (required for KnowledgeDocument.embedding)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ------------------------------------------------------------------
    # leads table
    # ------------------------------------------------------------------
    op.create_table(
        "leads",
        sa.Column("id", sa.CHAR(36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", sa.CHAR(36), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        # Identity
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("phone_e164", sa.String(50), unique=True, nullable=False),
        sa.Column("phone_raw", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="es"),
        sa.Column("country_of_residence", sa.String(2), nullable=True),
        sa.Column("nationality", sa.String(2), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state_region", sa.String(100), nullable=True),
        # Attribution
        sa.Column("source_channel", sa.String(100), nullable=True),
        sa.Column("campaign_name", sa.String(255), nullable=True),
        sa.Column("campaign_id", sa.String(255), nullable=True),
        sa.Column("adset_id", sa.String(255), nullable=True),
        sa.Column("ad_id", sa.String(255), nullable=True),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(100), nullable=True),
        sa.Column("landing_page", sa.String(500), nullable=True),
        sa.Column("referral_source", sa.String(500), nullable=True),
        # Commercial
        sa.Column("lead_status", sa.String(50), nullable=False, server_default="NEW"),
        sa.Column("funnel_stage", sa.String(50), nullable=False, server_default="AWARENESS"),
        sa.Column("lead_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("intent_level", sa.String(50), nullable=True),
        # Conversation tracking
        sa.Column("first_contact_at", sa.DateTime(), nullable=True),
        sa.Column("last_conversation_at", sa.DateTime(), nullable=True),
        sa.Column("last_conversation_channel", sa.String(50), nullable=True),
        sa.Column("conversation_status", sa.String(50), nullable=True),
        sa.Column("whatsapp_opt_in_status", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("chatwoot_contact_id", sa.String(100), nullable=True),
        sa.Column("chatwoot_conversation_id_last", sa.String(100), nullable=True),
        sa.Column("assigned_agent", sa.String(255), nullable=True),
        sa.Column("ai_handled_flag", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("human_handoff_flag", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("last_message_summary", sa.Text(), nullable=True),
        # Checkout tracking
        sa.Column("form_started", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("form_completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("checkout_started", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("checkout_started_at", sa.DateTime(), nullable=True),
        sa.Column("checkout_completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("abandoned_checkout_flag", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("abandoned_checkout_at", sa.DateTime(), nullable=True),
        sa.Column("purchase_completed", sa.Boolean(), nullable=False, server_default="0"),
        # Follow-up
        sa.Column("followup_whatsapp_sent", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("followup_whatsapp_sent_at", sa.DateTime(), nullable=True),
        sa.Column("followup_sequence_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_followup_at", sa.DateTime(), nullable=True),
        sa.Column("converted_to_contact_flag", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("converted_at", sa.DateTime(), nullable=True),
        sa.Column("backend_customer_id", sa.CHAR(36), nullable=True),
        # Sync
        sa.Column("zoho_lead_id", sa.String(100), nullable=True),
        sa.Column("snapshot_last_synced_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_leads_id", "leads", ["id"])
    op.create_index("ix_leads_phone_e164", "leads", ["phone_e164"], unique=True)
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_workspace_id", "leads", ["workspace_id"])

    # ------------------------------------------------------------------
    # knowledge_documents table  (pgvector embedding column)
    # ------------------------------------------------------------------
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.CHAR(36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", sa.CHAR(36), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        # embedding is added as a raw DDL column because SA doesn't know Vector natively
        # without pgvector installed; the type is resolved at runtime via pgvector.sqlalchemy.
        sa.Column("embedding", sa.Text(), nullable=True),  # placeholder, altered below
    )
    # Replace placeholder 'embedding' column with proper vector(768) type
    op.execute("ALTER TABLE knowledge_documents ALTER COLUMN embedding TYPE vector(768) USING NULL::vector(768)")
    op.create_index("ix_knowledge_documents_id", "knowledge_documents", ["id"])
    op.create_index("ix_knowledge_documents_workspace_id", "knowledge_documents", ["workspace_id"])

    # ------------------------------------------------------------------
    # chat_conversations table
    # ------------------------------------------------------------------
    op.create_table(
        "chat_conversations",
        sa.Column("id", sa.CHAR(36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", sa.CHAR(36), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.CHAR(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.String(100), unique=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("context_snapshot", sa.JSON(), nullable=True),
    )
    op.create_index("ix_chat_conversations_id", "chat_conversations", ["id"])
    op.create_index("ix_chat_conversations_workspace_id", "chat_conversations", ["workspace_id"])
    op.create_index("ix_chat_conversations_session_id", "chat_conversations", ["session_id"], unique=True)

    # ------------------------------------------------------------------
    # chat_messages table
    # ------------------------------------------------------------------
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.CHAR(36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "conversation_id",
            sa.CHAR(36),
            sa.ForeignKey("chat_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
    )
    op.create_index("ix_chat_messages_id", "chat_messages", ["id"])


def downgrade() -> None:
    """Drop AI and leads tables.

    Note: the pgvector extension is intentionally NOT dropped here because
    other tables or future migrations may depend on it. Dropping it could
    break vector columns that exist outside this migration's scope.
    """
    op.drop_table("chat_messages")
    op.drop_table("chat_conversations")
    op.drop_table("knowledge_documents")
    op.drop_table("leads")
