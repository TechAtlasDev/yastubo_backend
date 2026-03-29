"""leads_and_ai_modules

Revision ID: f1a2b3c4d5e6
Revises: ecb513a9360b
Create Date: 2026-03-29 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "ecb513a9360b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension (required by KnowledgeDocument.embedding)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # --- leads table ---
    op.create_table(
        "leads",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identity
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("phone_e164", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("phone_raw", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column(
            "preferred_language", sa.String(10), nullable=False, server_default="es"
        ),
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
        sa.Column(
            "funnel_stage", sa.String(50), nullable=False, server_default="AWARENESS"
        ),
        sa.Column("lead_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("intent_level", sa.String(50), nullable=True),
        # Conversation tracking
        sa.Column("first_contact_at", sa.DateTime(), nullable=True),
        sa.Column("last_conversation_at", sa.DateTime(), nullable=True),
        sa.Column("last_conversation_channel", sa.String(50), nullable=True),
        sa.Column("conversation_status", sa.String(50), nullable=True),
        sa.Column(
            "whatsapp_opt_in_status",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("chatwoot_contact_id", sa.String(100), nullable=True),
        sa.Column("chatwoot_conversation_id_last", sa.String(100), nullable=True),
        sa.Column("assigned_agent", sa.String(255), nullable=True),
        sa.Column(
            "ai_handled_flag", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "human_handoff_flag", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("last_message_summary", sa.Text(), nullable=True),
        # Checkout tracking
        sa.Column("form_started", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "form_completed", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "checkout_started", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("checkout_started_at", sa.DateTime(), nullable=True),
        sa.Column(
            "checkout_completed", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "abandoned_checkout_flag",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("abandoned_checkout_at", sa.DateTime(), nullable=True),
        sa.Column(
            "purchase_completed", sa.Boolean(), nullable=False, server_default="false"
        ),
        # Follow-up
        sa.Column(
            "followup_whatsapp_sent",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("followup_whatsapp_sent_at", sa.DateTime(), nullable=True),
        sa.Column(
            "followup_sequence_step", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("next_followup_at", sa.DateTime(), nullable=True),
        sa.Column(
            "converted_to_contact_flag",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("converted_at", sa.DateTime(), nullable=True),
        sa.Column("backend_customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Sync
        sa.Column("zoho_lead_id", sa.String(100), nullable=True),
        sa.Column("snapshot_last_synced_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_leads_id", "leads", ["id"])
    op.create_index("ix_leads_email", "leads", ["email"])

    # --- knowledge_documents table ---
    op.create_table(
        "knowledge_documents",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_knowledge_documents_id", "knowledge_documents", ["id"])
    op.create_index(
        "ix_knowledge_documents_workspace_id", "knowledge_documents", ["workspace_id"]
    )

    # --- chat_conversations table ---
    op.create_table(
        "chat_conversations",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("context_snapshot", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_chat_conversations_id", "chat_conversations", ["id"])
    op.create_index(
        "ix_chat_conversations_workspace_id", "chat_conversations", ["workspace_id"]
    )
    op.create_index(
        "ix_chat_conversations_session_id", "chat_conversations", ["session_id"]
    )

    # --- chat_messages table ---
    op.create_table(
        "chat_messages",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["chat_conversations.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_chat_messages_id", "chat_messages", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("chat_messages")
    op.drop_table("chat_conversations")
    op.drop_table("knowledge_documents")
    op.drop_table("leads")
    op.execute("DROP EXTENSION IF EXISTS vector")
