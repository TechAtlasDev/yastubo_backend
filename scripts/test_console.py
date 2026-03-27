from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()
ROOT = Path(__file__).resolve().parents[1]

MODULE_PATHS = {
    "auth": "tests/modules/auth/",
    "plans": "tests/modules/plans/",
    "emission": "tests/modules/emission/",
    "payments": "tests/modules/payments/",
    "audit": "tests/modules/audit/",
    "portal": "tests/modules/portal/",
    "integrations": "tests/integrations/",
    "infra": "tests/test_infra.py",
}


def run_pytest(extra_args: list[str]) -> int:
    command = ["uv", "run", "pytest", *extra_args]
    console.print(f"[bold cyan]Ejecutando:[/bold cyan] [dim]{' '.join(command)}[/dim]")
    completed = subprocess.run(command, cwd=ROOT)
    return completed.returncode


def menu() -> int:
    console.print(
        Panel(
            "[bold]Yastubo Test Console[/bold]\nSelecciona qué quieres testear",
            border_style="magenta",
        )
    )

    while True:
        table = Table(title="Opciones")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Acción")
        table.add_row("1", "Todo el proyecto")
        table.add_row("2", "Un módulo completo")
        table.add_row("3", "Un archivo específico")
        table.add_row("4", "Un test puntual (node id)")
        table.add_row("5", "Parte específica por -k")
        table.add_row("6", "Comando pytest personalizado")
        table.add_row("0", "Salir")
        console.print(table)

        option = Prompt.ask(
            "Elige una opción", choices=["0", "1", "2", "3", "4", "5", "6"], default="2"
        )

        args: list[str] = ["-v"]

        if option == "0":
            console.print("[yellow]Saliendo...[/yellow]")
            return 0

        if option == "1":
            pass
        elif option == "2":
            module = Prompt.ask("Módulo", choices=list(MODULE_PATHS.keys()))
            args.insert(0, MODULE_PATHS[module])
        elif option == "3":
            file_path = Prompt.ask(
                "Ruta del archivo de test", default="tests/modules/plans/test_plans.py"
            )
            args.insert(0, file_path)
        elif option == "4":
            node_id = Prompt.ask(
                "Node id",
                default="tests/modules/plans/test_plans.py::test_create_plan_as_admin_returns_201",
            )
            args.insert(0, node_id)
        elif option == "5":
            target = Prompt.ask(
                "Target (archivo/carpeta)", default="tests/modules/payments/"
            )
            keyword = Prompt.ask("Expresión -k", default="webhook and failed")
            args = [target, "-k", keyword, "-v"]
        elif option == "6":
            raw = Prompt.ask("Argumentos pytest", default="tests/modules/audit/ -v")
            args = raw.split()

        if Confirm.ask("¿Agregar -x (fail fast)?", default=False):
            args.append("-x")

        if Confirm.ask("¿Mostrar warnings (-W default)?", default=False):
            args.extend(["-W", "default"])

        code = run_pytest(args)
        if code == 0:
            console.print("[bold green]✓ Tests completados correctamente[/bold green]")
        else:
            console.print("[bold red]✗ Hubo fallos en los tests[/bold red]")

        if not Confirm.ask("¿Quieres ejecutar otra selección?", default=True):
            return code


def main() -> int:
    parser = argparse.ArgumentParser(description="Runner de tests interactivo con Rich")
    parser.add_argument(
        "--all", action="store_true", help="Ejecutar toda la suite sin menú"
    )
    parser.add_argument(
        "--module", choices=list(MODULE_PATHS.keys()), help="Ejecutar un módulo"
    )
    parser.add_argument("--target", help="Ruta o node id específico")
    parser.add_argument("-k", "--keyword", help="Filtro por expresión -k")
    parser.add_argument("--fail-fast", action="store_true", help="Agregar -x")
    args = parser.parse_args()

    if args.all:
        test_args = ["-v"]
    elif args.module:
        test_args = [MODULE_PATHS[args.module], "-v"]
    elif args.target:
        test_args = [args.target, "-v"]
    elif args.keyword:
        test_args = ["-k", args.keyword, "-v"]
    else:
        return menu()

    if args.keyword and args.target:
        test_args = [args.target, "-k", args.keyword, "-v"]

    if args.fail_fast:
        test_args.append("-x")

    return run_pytest(test_args)


if __name__ == "__main__":
    raise SystemExit(main())
