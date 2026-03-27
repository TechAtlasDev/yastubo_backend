from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
ROOT = Path(__file__).resolve().parents[1]


def run_step(title: str, command: list[str]) -> tuple[bool, str]:
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"[dim]$ {' '.join(command)}[/dim]")

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if completed.returncode == 0:
        console.print("[green]✓ OK[/green]")
        return True, completed.stdout.strip()

    console.print("[red]✗ ERROR[/red]")
    if completed.stderr:
        console.print(
            Panel(completed.stderr.strip(), title="stderr", border_style="red")
        )
    return False, completed.stderr.strip()


def ensure_env_file() -> None:
    env_example = ROOT / ".env.example"
    env_file = ROOT / ".env"

    if env_file.exists():
        console.print("[green]✓ .env ya existe[/green]")
        return

    if not env_example.exists():
        console.print("[yellow]! .env.example no encontrado, se omite copia[/yellow]")
        return

    shutil.copy(env_example, env_file)
    console.print("[green]✓ .env creado desde .env.example[/green]")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Instala e inicializa el backend de Yastubo con un solo comando.",
    )
    parser.add_argument("--skip-sync", action="store_true", help="No ejecutar uv sync")
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="No ejecutar alembic upgrade head",
    )
    parser.add_argument(
        "--skip-seed", action="store_true", help="No ejecutar scripts/seed_roles.py"
    )
    parser.add_argument(
        "--skip-smoke-test", action="store_true", help="No ejecutar tests/test_infra.py"
    )
    parser.add_argument(
        "--skip-hooks", action="store_true", help="No instalar hooks de pre-commit"
    )

    args = parser.parse_args()

    console.print(
        Panel(
            "[bold]Yastubo Backend Setup[/bold]\n"
            "Instalación e inicialización automática",
            border_style="blue",
        )
    )

    ensure_env_file()

    results: list[tuple[str, bool]] = []

    if not args.skip_sync:
        ok, _ = run_step("Instalando dependencias", ["uv", "sync", "--dev"])
        results.append(("uv sync --dev", ok))
        if not ok:
            return 1

    if not args.skip_hooks:
        ok, _ = run_step(
            "Instalando hook pre-commit", ["uv", "run", "pre-commit", "install"]
        )
        results.append(("pre-commit install", ok))
        if not ok:
            return 1

        ok, _ = run_step(
            "Instalando hook pre-push",
            ["uv", "run", "pre-commit", "install", "--hook-type", "pre-push"],
        )
        results.append(("pre-commit install --hook-type pre-push", ok))
        if not ok:
            return 1

    if not args.skip_migrations:
        ok, _ = run_step(
            "Aplicando migraciones", ["uv", "run", "alembic", "upgrade", "head"]
        )
        results.append(("alembic upgrade head", ok))
        if not ok:
            return 1

    if not args.skip_seed:
        ok, _ = run_step(
            "Sembrando roles y permisos",
            ["uv", "run", "python", "scripts/seed_roles.py"],
        )
        results.append(("seed_roles.py", ok))
        if not ok:
            return 1

    if not args.skip_smoke_test:
        ok, _ = run_step(
            "Ejecutando smoke test",
            ["uv", "run", "pytest", "tests/test_infra.py", "-q"],
        )
        results.append(("pytest tests/test_infra.py -q", ok))
        if not ok:
            return 1

    table = Table(title="Resumen")
    table.add_column("Paso")
    table.add_column("Estado")
    for step, ok in results:
        table.add_row(step, "[green]OK[/green]" if ok else "[red]FAIL[/red]")

    console.print(table)
    console.print("[bold green]Backend listo.[/bold green]")
    console.print(
        "[dim]Comando sugerido para correr API: uv run uvicorn app.main:app --reload[/dim]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
