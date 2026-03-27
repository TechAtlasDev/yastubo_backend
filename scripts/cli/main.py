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
    """The developer concierge for Yastubo."""

    TITLE = "Yastubo Dev CLI 🚀"
    CSS = """
    TabbedContent {
        height: 100%;
    }
    TabPane {
        padding: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit CLI"),
        ("d", "toggle_dark", "Toggle Dark/Light Mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="dashboard-tab"):
            with TabPane("🏠 Dashboard", id="dashboard-tab"):
                yield DashboardScreen()
            with TabPane("📂 Modules", id="modules-tab"):
                yield ModulesScreen()
            with TabPane("🧪 Test Lab", id="test-tab"):
                yield TestingScreen()
            with TabPane("📚 Docs Center", id="docs-tab"):
                yield DocsScreen()
            with TabPane("🛠️ Ops Panel", id="ops-tab"):
                yield OpsScreen()
        yield Footer()


if __name__ == "__main__":
    app = YastuboDevApp()
    app.run()
