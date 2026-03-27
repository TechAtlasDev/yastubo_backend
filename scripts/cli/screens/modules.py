import os
from textual.app import ComposeResult
from textual.widgets import Input, Button, Label, ListView, ListItem, RichLog
from textual.containers import Vertical, Horizontal
from textual import on
from scripts.cli.utils.scaffolder import scaffold_module


class ModulesScreen(Vertical):
    """Screen for browsing existing modules and scaffolding new ones."""

    DEFAULT_CSS = """
    #modules-container {
        layout: horizontal;
        height: 1fr;
    }
    #modules-list {
        width: 30%;
        border-right: solid $primary;
        height: 100%;
    }
    #module-actions {
        width: 70%;
        padding: 1 2;
        height: 100%;
    }
    .scaffold-box {
        border: round $accent;
        padding: 1;
        height: auto;
        margin-bottom: 2;
    }
    #scaffold-input {
        margin-bottom: 1;
    }
    #scaffold-log {
        height: 1fr;
        border: solid $panel;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="modules-container"):
            # Left panel: List existing modules
            with Vertical(id="modules-list-container", classes="modules-list"):
                yield Label("📦 Existing Modules", classes="section-title")
                yield ListView(id="modules-list")

            # Right panel: Actions (Scaffold)
            with Vertical(id="module-actions"):
                with Vertical(classes="scaffold-box"):
                    yield Label("🛠️ Scaffold New Module", classes="section-title")
                    yield Label(
                        "Generates models.py, schemas.py, service.py, router.py"
                    )
                    yield Input(
                        placeholder="Module name (e.g. invoices, claims)",
                        id="scaffold-input",
                    )
                    yield Button(
                        "Generate Scaffold", id="scaffold-btn", variant="primary"
                    )

                yield Label("Output Log:")
                yield RichLog(id="scaffold-log", wrap=True)

    def on_mount(self) -> None:
        self.refresh_modules()

    def refresh_modules(self) -> None:
        """Loads modules from app/modules directory."""
        app_modules_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            ),
            "app",
            "modules",
        )
        list_view = self.query_one("#modules-list", ListView)
        list_view.clear()

        if os.path.exists(app_modules_dir):
            modules = [
                d
                for d in os.listdir(app_modules_dir)
                if os.path.isdir(os.path.join(app_modules_dir, d))
                and not d.startswith("__")
            ]
            for mod in sorted(modules):
                list_view.append(ListItem(Label(f"📁 {mod}")))

    @on(Button.Pressed, "#scaffold-btn")
    def handle_scaffold(self) -> None:
        input_widget = self.query_one("#scaffold-input", Input)
        module_name = input_widget.value.strip().lower()
        log_widget = self.query_one("#scaffold-log", RichLog)

        if not module_name:
            log_widget.write("[red]Error: Please specify a module name.[/red]")
            return

        result = scaffold_module(module_name)
        if result.startswith("Success"):
            log_widget.write(f"[green]{result}[/green]")
            input_widget.value = ""
            self.refresh_modules()
        else:
            log_widget.write(f"[red]{result}[/red]")
