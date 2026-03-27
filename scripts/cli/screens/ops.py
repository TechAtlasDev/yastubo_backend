import os
from textual.app import ComposeResult
from textual.widgets import Label, Button, RichLog
from textual.containers import Vertical, Horizontal
from textual import on, work
from scripts.cli.utils.runner import stream_command


class OpsScreen(Vertical):
    """Operations Panel for running Makefile and infrastructure commands."""

    DEFAULT_CSS = """
    #ops-buttons {
        height: auto;
        margin-bottom: 2;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 2;
    }
    #ops-log {
        height: 1fr;
        border: solid $accent;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("🛠️ Ops Panel (Makefile & System)", classes="section-title")

        with Horizontal(id="ops-buttons"):
            yield Button("📦 make setup", id="btn-make-setup", variant="primary")
            yield Button("🛡️ make build", id="btn-make-build", variant="warning")
            yield Button("🧹 make lint", id="btn-make-lint")
            yield Button("🔥 make smoke", id="btn-make-smoke", variant="error")
            yield Button("📥 uv sync", id="btn-uv-sync")
            yield Button("🧹 Clear Log", id="btn-clear-log", variant="default")

        yield RichLog(id="ops-log", highlight=True, markup=True)

    @on(Button.Pressed, "#btn-clear-log")
    def clear_log(self) -> None:
        self.query_one("#ops-log", RichLog).clear()

    @on(Button.Pressed)
    def handle_button(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "btn-clear-log":
            return

        cmd_map = {
            "btn-make-setup": "make setup",
            "btn-make-build": "make build",
            "btn-make-lint": "make lint",
            "btn-make-smoke": "make smoke",
            "btn-uv-sync": "uv sync --dev",
        }

        if button_id in cmd_map:
            cmd = cmd_map[button_id]
            self.run_ops_command(cmd)

    def run_ops_command(self, cmd: str) -> None:
        log = self.query_one("#ops-log", RichLog)
        log.write(f"\n[bold yellow]Running: {cmd}[/bold yellow]")

        # Disable all buttons
        for btn in self.query("Button"):
            btn.disabled = True

        cwd = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        self.execute_command_async(cmd, cwd)

    @work(exclusive=True)
    async def execute_command_async(self, cmd: str, cwd: str) -> None:
        log = self.query_one("#ops-log", RichLog)

        async def on_output(line: str):
            log.write(line)

        async def on_exit(code: int):
            color = "green" if code == 0 else "red"
            msg = f"\n[bold {color}]Command finished with exit code: {code}[/bold {color}]"
            log.write(msg)

            # Re-enable buttons
            for btn in self.query("Button"):
                btn.disabled = False

        await stream_command(cmd, cwd, on_output, on_exit)
