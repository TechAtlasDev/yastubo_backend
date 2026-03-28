"""Smoke tests for DT-10: Alembic migration for leads, AI tables, and pgvector extension."""

import pathlib


MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / "migrations" / "versions"
MIGRATION_FILE = MIGRATIONS_DIR / "b1c2d3e4f5a6_leads_and_ai_modules.py"


class TestMigrationFileExists:
    def test_migration_file_present(self):
        assert MIGRATION_FILE.exists(), (
            f"Expected migration file not found: {MIGRATION_FILE}"
        )


class TestMigrationContent:
    """Validate the migration script contains the expected DDL operations."""

    def _source(self) -> str:
        return MIGRATION_FILE.read_text()

    def test_revision_id(self):
        source = self._source()
        assert 'revision: str = "b1c2d3e4f5a6"' in source

    def test_down_revision_points_to_payments_module(self):
        source = self._source()
        assert '"32b4fc9d61a1"' in source

    def test_creates_pgvector_extension(self):
        source = self._source()
        assert "CREATE EXTENSION IF NOT EXISTS vector" in source

    def test_creates_leads_table(self):
        source = self._source()
        assert '"leads"' in source
        assert "create_table" in source

    def test_leads_has_phone_e164_column(self):
        source = self._source()
        assert "phone_e164" in source

    def test_leads_has_workspace_fk(self):
        source = self._source()
        assert "workspaces.id" in source

    def test_creates_knowledge_documents_table(self):
        source = self._source()
        assert '"knowledge_documents"' in source

    def test_knowledge_documents_has_embedding_column(self):
        source = self._source()
        assert "embedding" in source
        # The column is converted to vector(768)
        assert "vector(768)" in source

    def test_creates_chat_conversations_table(self):
        source = self._source()
        assert '"chat_conversations"' in source

    def test_creates_chat_messages_table(self):
        source = self._source()
        assert '"chat_messages"' in source

    def test_chat_messages_references_chat_conversations(self):
        source = self._source()
        assert "chat_conversations.id" in source

    def test_downgrade_drops_tables(self):
        source = self._source()
        assert "drop_table" in source
        assert '"chat_messages"' in source
        assert '"chat_conversations"' in source
        assert '"knowledge_documents"' in source
        assert '"leads"' in source

    def test_upgrade_and_downgrade_functions_defined(self):
        source = self._source()
        assert "def upgrade()" in source
        assert "def downgrade()" in source
