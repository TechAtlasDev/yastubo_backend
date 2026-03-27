import sys
import os
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from textual import work


class DashboardScreen(Vertical):
    """Dashboard tab showing system status."""

    DEFAULT_CSS = """
    #dashboard-header {
        height: 3;
        content-align: center middle;
        background: $boost;
        margin-bottom: 1;
    }
    #dashboard-header Static {
        text-style: bold;
    }
    #system-checks {
        border: solid $accent;
        padding: 1;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="dashboard-header"):
            yield Static("Welcome to Yastubo Dev Machine 🚀", id="welcome-text")

        yield Static("FastAPI Monolithic Modular Backend", classes="subtitle")

        with Vertical(id="system-checks"):
            yield Static("Checking system status...", id="status-checks")

    def on_mount(self) -> None:
        self.check_system()

    @work
    async def check_system(self) -> None:
        status_text = []
        # Check python version
        status_text.append(f"✅ Python Version: {sys.version.split(' ')[0]}")
        # Check .env
        env_exists = os.path.exists(".env")
        status_text.append(
            f"{'✅' if env_exists else '❌'} .env File: {'Found' if env_exists else 'Missing'}"
        )

        # Check database settings in .env
        if env_exists:
            with open(".env", "r") as f:
                content = f.read()
                if "DATABASE_URL" in content:
                    status_text.append("✅ Database URL configured")
                if "STRIPE_SECRET_KEY" in content:
                    status_text.append("✅ Stripe connected")

        self.query_one("#status-checks", Static).update("\n\n".join(status_text))
