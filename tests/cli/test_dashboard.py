"""Pruebas unitarias para scripts/cli/screens/dashboard.py (funciones auxiliares)."""

from __future__ import annotations

import os


from scripts.cli.screens.dashboard import (
    _check_env_vars,
    _count_modules,
    _count_test_files,
    _get_modules_dir,
    _get_root_dir,
)


class TestGetRootDir:
    def test_returns_string(self):
        result = _get_root_dir()
        assert isinstance(result, str)

    def test_contains_yastubo_backend(self):
        result = _get_root_dir()
        assert os.path.isdir(result)


class TestGetModulesDir:
    def test_returns_string(self):
        result = _get_modules_dir()
        assert isinstance(result, str)

    def test_path_ends_with_modules(self):
        result = _get_modules_dir()
        assert result.endswith(os.path.join("app", "modules"))


class TestCountModules:
    def test_counts_only_directories(self, tmp_path):
        """Solo cuenta directorios (no archivos)."""
        (tmp_path / "mod_a").mkdir()
        (tmp_path / "mod_b").mkdir()
        (tmp_path / "not_a_module.py").write_text("")
        assert _count_modules(str(tmp_path)) == 2

    def test_excludes_dunder_dirs(self, tmp_path):
        """Excluye directorios que empiezan con __ (ej. __pycache__)."""
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__init__").mkdir()
        (tmp_path / "real_module").mkdir()
        assert _count_modules(str(tmp_path)) == 1

    def test_returns_zero_for_missing_dir(self, tmp_path):
        missing = str(tmp_path / "non_existent")
        assert _count_modules(missing) == 0

    def test_returns_zero_for_empty_dir(self, tmp_path):
        assert _count_modules(str(tmp_path)) == 0

    def test_counts_multiple_modules(self, tmp_path):
        for name in ["auth", "plans", "emission", "payments"]:
            (tmp_path / name).mkdir()
        assert _count_modules(str(tmp_path)) == 4


class TestCountTestFiles:
    def test_counts_test_files_recursively(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_a.py").write_text("")
        sub = tests_dir / "modules"
        sub.mkdir()
        (sub / "test_b.py").write_text("")
        assert _count_test_files(str(tmp_path)) == 2

    def test_ignores_non_test_files(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "conftest.py").write_text("")
        (tests_dir / "helpers.py").write_text("")
        assert _count_test_files(str(tmp_path)) == 0

    def test_returns_zero_when_tests_dir_missing(self, tmp_path):
        result = _count_test_files(str(tmp_path / "ghost"))
        assert result == 0

    def test_counts_correctly_with_multiple_levels(self, tmp_path):
        tests_dir = tmp_path / "tests"
        for sub in ["modules/auth", "modules/plans", "integrations"]:
            d = tests_dir / sub
            d.mkdir(parents=True)
            (d / f"test_{sub.replace('/', '_')}.py").write_text("")
        assert _count_test_files(str(tmp_path)) == 3


class TestCheckEnvVars:
    def test_returns_false_when_no_env_file(self, tmp_path):
        result = _check_env_vars(str(tmp_path))
        assert result["env_file"] is False
        assert result["database_url"] is False
        assert result["stripe_key"] is False
        assert result["secret_key"] is False
        assert result["redis_url"] is False

    def test_detects_all_vars_present(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DATABASE_URL=postgresql://...\n"
            "STRIPE_SECRET_KEY=sk_test_...\n"
            "SECRET_KEY=supersecret\n"
            "REDIS_URL=redis://localhost\n"
        )
        result = _check_env_vars(str(tmp_path))
        assert result["env_file"] is True
        assert result["database_url"] is True
        assert result["stripe_key"] is True
        assert result["secret_key"] is True
        assert result["redis_url"] is True

    def test_partial_env_vars(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_URL=postgresql://...\n")
        result = _check_env_vars(str(tmp_path))
        assert result["database_url"] is True
        assert result["stripe_key"] is False
        assert result["secret_key"] is False
        assert result["redis_url"] is False

    def test_env_file_exists_but_empty(self, tmp_path):
        (tmp_path / ".env").write_text("")
        result = _check_env_vars(str(tmp_path))
        assert result["env_file"] is True
        assert result["database_url"] is False
