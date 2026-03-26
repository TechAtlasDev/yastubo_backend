from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, cmd: list[str]) -> bool:
    console.rule(f"[bold cyan]{name}[/bold cyan]")
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
    )
    if completed.returncode == 0:
        console.print("[green]✓ OK[/green]")
        if completed.stdout.strip():
            console.print(completed.stdout.strip())
        return True

    console.print("[red]✗ FAIL[/red]")
    if completed.stdout.strip():
        console.print(Panel(completed.stdout.strip(), title="stdout", border_style="yellow"))
    if completed.stderr.strip():
        console.print(Panel(completed.stderr.strip(), title="stderr", border_style="red"))
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quality gate equivalente a npm run build: lint + tests.",
    )
    parser.add_argument("--lint-only", action="store_true", help="Ejecuta solo lint")
    parser.add_argument("--tests-only", action="store_true", help="Ejecuta solo tests")
    parser.add_argument("--fail-fast", action="store_true", help="Usar pytest -x")
    args = parser.parse_args()

    if args.lint_only and args.tests_only:
        console.print("[red]No puedes usar --lint-only y --tests-only al mismo tiempo.[/red]")
        return 2

    steps: list[tuple[str, list[str]]] = []

    if not args.tests_only:
        steps.append(("Lint (Ruff)", ["uv", "run", "ruff", "check", "."]))

    if not args.lint_only:
        pytest_cmd = ["uv", "run", "pytest", "-q"]
        if args.fail_fast:
            pytest_cmd.append("-x")
        steps.append(("Tests (pytest)", pytest_cmd))

    summary: list[tuple[str, bool]] = []

    for step_name, cmd in steps:
        ok = run_step(step_name, cmd)
        summary.append((step_name, ok))
        if not ok:
            break

    table = Table(title="Resultado Build")
    table.add_column("Paso")
    table.add_column("Estado")
    for name, ok in summary:
        table.add_row(name, "[green]OK[/green]" if ok else "[red]FAIL[/red]")

    console.print(table)

    all_ok = all(ok for _, ok in summary) and len(summary) == len(steps)
    if all_ok:
        console.print("[bold green]Build exitoso: calidad y tests en verde.[/bold green]")
        return 0

    console.print("[bold red]Build fallido. Revisa los errores arriba.[/bold red]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
