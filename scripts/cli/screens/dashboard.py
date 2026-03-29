import sys
import os
import platform
from textual.app import ComposeResult
from textual.widgets import Static, Rule
from textual.containers import Vertical, Horizontal
from textual import work

BANNER = r"""
 __   __           _         _
 \ \ / /__ _  ___ | |_ _   _| |__   ___
  \ V / _ | / __|| __| | | | '_ \ / _ \
   | | (_| |\__ \| |_| |_| | |_) | (_) |
   |_|\__,_||___/ \__|\__,_|_.__/ \___/
"""


def _get_modules_dir() -> str:
    return os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ),
        "app",
        "modules",
    )


def _get_root_dir() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )


def _count_modules(modules_dir: str) -> int:
    if not os.path.exists(modules_dir):
        return 0
    return sum(
        1
        for d in os.listdir(modules_dir)
        if os.path.isdir(os.path.join(modules_dir, d)) and not d.startswith("__")
    )


def _count_test_files(root_dir: str) -> int:
    tests_dir = os.path.join(root_dir, "tests")
    if not os.path.exists(tests_dir):
        return 0
    count = 0
    for _, _, files in os.walk(tests_dir):
        count += sum(1 for f in files if f.startswith("test_") and f.endswith(".py"))
    return count


def _check_env_vars(root_dir: str) -> dict:
    env_path = os.path.join(root_dir, ".env")
    result = {
        "env_file": os.path.exists(env_path),
        "database_url": False,
        "stripe_key": False,
        "secret_key": False,
        "redis_url": False,
    }
    if result["env_file"]:
        try:
            with open(env_path, "r") as f:
                content = f.read()
            result["database_url"] = "DATABASE_URL" in content
            result["stripe_key"] = "STRIPE_SECRET_KEY" in content
            result["secret_key"] = "SECRET_KEY" in content
            result["redis_url"] = "REDIS_URL" in content
        except OSError:
            pass
    return result


class DashboardScreen(Vertical):
    """Pantalla principal del dashboard."""

    DEFAULT_CSS = """
    DashboardScreen {
        overflow-y: auto;
    }
    #banner-container {
        height: auto;
        content-align: center middle;
        background: $boost;
        padding: 0 2;
        margin-bottom: 1;
    }
    #banner-text {
        color: $accent;
        text-style: bold;
        content-align: center middle;
    }
    #tagline {
        color: $text-muted;
        content-align: center middle;
    }
    .info-grid {
        layout: grid;
        grid-size: 2;
        grid-gutter: 1 2;
        height: auto;
        margin-bottom: 1;
    }
    .info-card {
        border: round $primary;
        padding: 1 2;
        height: auto;
    }
    .info-card-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 0;
    }
    .info-card-value {
        margin-top: 0;
    }
    #system-status {
        border: round $accent;
        padding: 1 2;
        height: auto;
        margin-bottom: 1;
    }
    #env-status {
        border: round $warning;
        padding: 1 2;
        height: auto;
        margin-bottom: 1;
    }
    #atajos {
        border: round $success;
        padding: 1 2;
        height: auto;
    }
    .status-title {
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="banner-container"):
            yield Static(BANNER, id="banner-text")
            yield Static(
                "Backend Monolítico Modular · FastAPI · Python 3.12+", id="tagline"
            )

        yield Rule()

        with Horizontal(classes="info-grid"):
            with Vertical(classes="info-card"):
                yield Static("🐍 Versión de Python", classes="info-card-title")
                yield Static(
                    "Cargando...", id="python-version", classes="info-card-value"
                )
            with Vertical(classes="info-card"):
                yield Static("📦 Módulos del Proyecto", classes="info-card-title")
                yield Static(
                    "Cargando...", id="module-count", classes="info-card-value"
                )
            with Vertical(classes="info-card"):
                yield Static("🧪 Archivos de Test", classes="info-card-title")
                yield Static("Cargando...", id="test-count", classes="info-card-value")
            with Vertical(classes="info-card"):
                yield Static("💻 Sistema Operativo", classes="info-card-title")
                yield Static("Cargando...", id="os-info", classes="info-card-value")

        with Vertical(id="system-status"):
            yield Static("⚙️ Estado del Sistema", classes="status-title")
            yield Static("Verificando...", id="status-checks")

        with Vertical(id="env-status"):
            yield Static("🔑 Variables de Entorno (.env)", classes="status-title")
            yield Static("Verificando...", id="env-checks")

        with Vertical(id="atajos"):
            yield Static("⌨️ Atajos de Teclado", classes="status-title")
            yield Static(
                "[bold]1[/bold] → Inicio  "
                "[bold]2[/bold] → Módulos  "
                "[bold]3[/bold] → Tests  "
                "[bold]4[/bold] → Docs  "
                "[bold]5[/bold] → Operaciones  "
                "[bold]d[/bold] → Cambiar Tema  "
                "[bold]q[/bold] → Salir",
                id="shortcuts-info",
            )

    def on_mount(self) -> None:
        self.load_dashboard_data()

    @work
    async def load_dashboard_data(self) -> None:
        root_dir = _get_root_dir()
        modules_dir = _get_modules_dir()

        # Static info (no async needed)
        self.query_one("#python-version", Static).update(
            f"[green]{sys.version.split(' ')[0]}[/green]"
        )
        self.query_one("#os-info", Static).update(
            f"[cyan]{platform.system()} {platform.release()}[/cyan]"
        )

        # Module count
        module_count = _count_modules(modules_dir)
        self.query_one("#module-count", Static).update(
            f"[bold yellow]{module_count}[/bold yellow] módulos activos"
        )

        # Test file count
        test_count = _count_test_files(root_dir)
        self.query_one("#test-count", Static).update(
            f"[bold magenta]{test_count}[/bold magenta] archivos de test"
        )

        # System status
        status_lines = []
        status_lines.append(
            f"✅ Python {sys.version.split(' ')[0]} detectado correctamente"
        )

        uv_available = os.path.exists(
            os.path.join(root_dir, ".python-version")
        ) or os.path.exists(os.path.join(root_dir, "uv.lock"))
        status_lines.append(
            f"{'✅' if uv_available else '⚠️'} "
            f"Gestor de paquetes uv: {'disponible' if uv_available else 'no detectado'}"
        )

        makefile_exists = os.path.exists(os.path.join(root_dir, "Makefile"))
        status_lines.append(
            f"{'✅' if makefile_exists else '⚠️'} "
            f"Makefile: {'encontrado' if makefile_exists else 'no encontrado'}"
        )

        docker_exists = os.path.exists(os.path.join(root_dir, "docker-compose.yml"))
        status_lines.append(
            f"{'✅' if docker_exists else '⚠️'} "
            f"Docker Compose: {'configurado' if docker_exists else 'no encontrado'}"
        )

        alembic_exists = os.path.exists(os.path.join(root_dir, "alembic.ini"))
        status_lines.append(
            f"{'✅' if alembic_exists else '⚠️'} "
            f"Alembic (migraciones): {'configurado' if alembic_exists else 'no encontrado'}"
        )

        self.query_one("#status-checks", Static).update("\n".join(status_lines))

        # Env variables
        env_info = _check_env_vars(root_dir)
        env_lines = []
        env_lines.append(
            f"{'✅' if env_info['env_file'] else '❌'} "
            f"Archivo .env: {'encontrado' if env_info['env_file'] else 'FALTA — copia .env.example'}"
        )
        env_lines.append(
            f"{'✅' if env_info['database_url'] else '❌'} "
            f"DATABASE_URL: {'configurada' if env_info['database_url'] else 'no configurada'}"
        )
        env_lines.append(
            f"{'✅' if env_info['stripe_key'] else '⚠️'} "
            f"STRIPE_SECRET_KEY: {'configurada' if env_info['stripe_key'] else 'no configurada'}"
        )
        env_lines.append(
            f"{'✅' if env_info['secret_key'] else '❌'} "
            f"SECRET_KEY: {'configurada' if env_info['secret_key'] else 'no configurada'}"
        )
        env_lines.append(
            f"{'✅' if env_info['redis_url'] else '⚠️'} "
            f"REDIS_URL: {'configurada' if env_info['redis_url'] else 'no configurada'}"
        )

        self.query_one("#env-checks", Static).update("\n".join(env_lines))
