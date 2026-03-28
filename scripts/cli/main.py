import os
import sys

# Ensure app root is in path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
from scripts.cli.screens.dashboard import DashboardScreen
from scripts.cli.screens.modules import ModulesScreen
from scripts.cli.screens.testing import TestingScreen
from scripts.cli.screens.docs import DocsScreen
from scripts.cli.screens.ops import OpsScreen


class YastuboDevApp(App):
    """Consola de desarrollo para Yastubo Backend."""

    TITLE = "Yastubo Dev CLI 🚀"
    SUB_TITLE = "Panel de Control del Desarrollador"
    CSS = """
    TabbedContent {
        height: 100%;
    }
    TabPane {
        padding: 1 2;
    }
    .section-title {
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }
    """

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("d", "toggle_dark", "Cambiar Tema"),
        ("1", "switch_tab('dashboard-tab')", "Inicio"),
        ("2", "switch_tab('modules-tab')", "Módulos"),
        ("3", "switch_tab('test-tab')", "Tests"),
        ("4", "switch_tab('docs-tab')", "Docs"),
        ("5", "switch_tab('ops-tab')", "Operaciones"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="dashboard-tab"):
            with TabPane("🏠 Inicio", id="dashboard-tab"):
                yield DashboardScreen()
            with TabPane("📂 Módulos", id="modules-tab"):
                yield ModulesScreen()
            with TabPane("🧪 Laboratorio de Tests", id="test-tab"):
                yield TestingScreen()
            with TabPane("📚 Centro de Docs", id="docs-tab"):
                yield DocsScreen()
            with TabPane("🛠️ Operaciones", id="ops-tab"):
                yield OpsScreen()
        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        """Cambia a la pestaña indicada por su id."""
        self.query_one(TabbedContent).active = tab_id


if __name__ == "__main__":
    app = YastuboDevApp()
    app.run()
