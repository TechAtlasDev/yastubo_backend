"""Pruebas unitarias para scripts/cli/utils/scaffolder.py"""

from __future__ import annotations

from unittest.mock import patch


from scripts.cli.utils.scaffolder import scaffold_module


class TestScaffoldModule:
    """Pruebas unitarias del scaffolder de módulos."""

    def test_scaffold_creates_expected_files(self, tmp_path):
        """Verifica que se crean todos los archivos esperados."""
        modules_dir = tmp_path / "app" / "modules"
        modules_dir.mkdir(parents=True)
        fake_utils = tmp_path / "scripts" / "cli" / "utils"
        fake_utils.mkdir(parents=True, exist_ok=True)

        with patch(
            "scripts.cli.utils.scaffolder.os.path.abspath",
            return_value=str(fake_utils / "scaffolder.py"),
        ):
            result = scaffold_module("facturas")

        assert result.startswith("Success")
        module_path = modules_dir / "facturas"
        assert module_path.exists()
        expected_files = [
            "__init__.py",
            "models.py",
            "schemas.py",
            "service.py",
            "router.py",
            "state_machine.py",
        ]
        for fname in expected_files:
            assert (module_path / fname).exists(), f"Falta el archivo: {fname}"

    def test_scaffold_returns_success_message(self, tmp_path):
        """El mensaje de éxito contiene el nombre del módulo."""
        modules_dir = tmp_path / "app" / "modules"
        modules_dir.mkdir(parents=True)
        fake_utils = tmp_path / "scripts" / "cli" / "utils"
        fake_utils.mkdir(parents=True, exist_ok=True)

        with patch(
            "scripts.cli.utils.scaffolder.os.path.abspath",
            return_value=str(fake_utils / "scaffolder.py"),
        ):
            result = scaffold_module("pagos")

        assert "pagos" in result
        assert result.startswith("Success")

    def test_scaffold_rejects_invalid_identifier(self):
        """Rechaza nombres que no son identificadores Python válidos."""
        result = scaffold_module("mi-modulo")
        assert result.startswith("Error")
        assert "mi-modulo" in result

    def test_scaffold_rejects_empty_name(self):
        """Rechaza nombre vacío."""
        result = scaffold_module("")
        assert result.startswith("Error")

    def test_scaffold_rejects_existing_module(self, tmp_path):
        """No sobrescribe un módulo que ya existe."""
        modules_dir = tmp_path / "app" / "modules"
        existing = modules_dir / "auth"
        existing.mkdir(parents=True)
        fake_utils = tmp_path / "scripts" / "cli" / "utils"
        fake_utils.mkdir(parents=True, exist_ok=True)

        with patch(
            "scripts.cli.utils.scaffolder.os.path.abspath",
            return_value=str(fake_utils / "scaffolder.py"),
        ):
            result = scaffold_module("auth")

        assert result.startswith("Error")
        assert "auth" in result

    def test_scaffold_router_contains_module_name(self, tmp_path):
        """El archivo router.py generado contiene el nombre del módulo."""
        modules_dir = tmp_path / "app" / "modules"
        modules_dir.mkdir(parents=True)
        fake_utils = tmp_path / "scripts" / "cli" / "utils"
        fake_utils.mkdir(parents=True, exist_ok=True)

        with patch(
            "scripts.cli.utils.scaffolder.os.path.abspath",
            return_value=str(fake_utils / "scaffolder.py"),
        ):
            scaffold_module("siniestros")

        router_content = (modules_dir / "siniestros" / "router.py").read_text()
        assert "siniestros" in router_content

    def test_scaffold_state_machine_contains_transitions(self, tmp_path):
        """El state_machine.py generado contiene las transiciones básicas."""
        modules_dir = tmp_path / "app" / "modules"
        modules_dir.mkdir(parents=True)
        fake_utils = tmp_path / "scripts" / "cli" / "utils"
        fake_utils.mkdir(parents=True, exist_ok=True)

        with patch(
            "scripts.cli.utils.scaffolder.os.path.abspath",
            return_value=str(fake_utils / "scaffolder.py"),
        ):
            scaffold_module("contratos")

        sm_content = (modules_dir / "contratos" / "state_machine.py").read_text()
        assert "VALID_TRANSITIONS" in sm_content
        assert "transition" in sm_content
