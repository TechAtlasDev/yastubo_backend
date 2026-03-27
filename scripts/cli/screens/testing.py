import os
from textual.app import ComposeResult
from textual.widgets import Label, Button, RichLog, Select
from textual.containers import Vertical, Horizontal
from textual import on, work
from scripts.cli.utils.runner import stream_command


class TestingScreen(Vertical):
    """Test Lab interface for executing pytest."""

    DEFAULT_CSS = """
    #test-controls {
        height: 3;
        margin-bottom: 1;
        align-vertical: middle;
    }
    #test-log {
        height: 1fr;
        border: solid $accent;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("🧪 Test Lab", classes="section-title")

        with Horizontal(id="test-controls"):
            yield Select([], prompt="Select Target...", id="test-target-select")
            yield Button("Run Tests", variant="success", id="run-tests-btn")
            yield Button("Clear Log", variant="default", id="clear-log-btn")

        yield RichLog(id="test-log", highlight=True, markup=True)

    def on_mount(self) -> None:
        self.populate_targets()

    def populate_targets(self) -> None:
        options = [("All Tests (tests/)", "all")]

        tests_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            ),
            "tests",
            "modules",
        )

        if os.path.exists(tests_dir):
            for d in sorted(os.listdir(tests_dir)):
                options.append((f"Module: {d}", f"tests/modules/{d}"))

        self.query_one("#test-target-select", Select).set_options(options)

    @on(Button.Pressed, "#clear-log-btn")
    def clear_log(self) -> None:
        self.query_one("#test-log", RichLog).clear()

    @on(Button.Pressed, "#run-tests-btn")
    def start_tests(self) -> None:
        target_select = self.query_one("#test-target-select", Select)
        target = target_select.value

        if not target:
            self.query_one("#test-log", RichLog).write(
                "[red]Select a target first.[/red]"
            )
            return

        cmd = "uv run pytest -v" if target == "all" else f"uv run pytest {target} -v"

        log = self.query_one("#test-log", RichLog)
        log.write(f"\n[bold yellow]Running: {cmd}[/bold yellow]")

        # Disable button during run
        self.query_one("#run-tests-btn", Button).disabled = True

        cwd = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        self.execute_tests(cmd, cwd)

    @work(exclusive=True)
    async def execute_tests(self, cmd: str, cwd: str) -> None:
        log = self.query_one("#test-log", RichLog)

        async def on_output(line: str):
            log.write(line)

        async def on_exit(code: int):
            color = "green" if code == 0 else "red"
            msg = (
                f"\n[bold {color}]Tests finished with exit code: {code}[/bold {color}]"
            )
            log.write(msg)
            self.query_one("#run-tests-btn", Button).disabled = False

        await stream_command(cmd, cwd, on_output, on_exit)
