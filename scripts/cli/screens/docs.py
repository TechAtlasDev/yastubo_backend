import os
import signal
import asyncio
from textual.app import ComposeResult
from textual.widgets import Label, Button, RichLog
from textual.containers import Vertical, Horizontal
from textual import on


class DocsScreen(Vertical):
    """Documentation Center for running Starlight docs."""

    DEFAULT_CSS = """
    #docs-controls {
        height: 3;
        margin-bottom: 1;
        align-vertical: middle;
    }
    #docs-log {
        height: 1fr;
        border: solid $accent;
    }
    """

    process_task = None

    def compose(self) -> ComposeResult:
        yield Label("📚 Docs Center (Astro Starlight)", classes="section-title")

        with Horizontal(id="docs-controls"):
            yield Button(
                "🚀 Launch Docs Server", variant="success", id="launch-docs-btn"
            )
            yield Button(
                "🛑 Stop Server", variant="error", id="stop-docs-btn", disabled=True
            )
            yield Button("Clear Log", variant="default", id="clear-docs-log-btn")

        yield RichLog(id="docs-log", highlight=True, markup=True)

    @on(Button.Pressed, "#clear-docs-log-btn")
    def clear_log(self) -> None:
        self.query_one("#docs-log", RichLog).clear()

    @on(Button.Pressed, "#launch-docs-btn")
    def launch_docs(self) -> None:
        self.query_one("#launch-docs-btn", Button).disabled = True
        self.query_one("#stop-docs-btn", Button).disabled = False

        cwd = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            ),
            "docs",
        )

        log = self.query_one("#docs-log", RichLog)
        log.write(
            "\n[bold yellow]Starting Astro Docs Server (npm run dev)...[/bold yellow]"
        )

        self.process_task = asyncio.create_task(self.run_server(cwd))

    @on(Button.Pressed, "#stop-docs-btn")
    def stop_docs(self) -> None:
        if self.process_task:
            self.process_task.cancel()
            self.process_task = None

        self.query_one("#launch-docs-btn", Button).disabled = False
        self.query_one("#stop-docs-btn", Button).disabled = True
        self.query_one("#docs-log", RichLog).write(
            "[bold red]Server stopped manually.[/bold red]"
        )

    async def run_server(self, cwd: str) -> None:
        log = self.query_one("#docs-log", RichLog)

        try:
            # We use process directly to be able to kill it
            process = await asyncio.create_subprocess_shell(
                "npm run dev",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=cwd,
                preexec_fn=os.setsid,  # Create process group to kill all children
            )

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                log.write(line.decode().rstrip())

            code = await process.wait()
            log.write(f"[bold cyan]Server exited with code {code}[/bold cyan]")

        except asyncio.CancelledError:
            if process.returncode is None:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                log.write("[bold cyan]Process group terminated.[/bold cyan]")

        finally:
            self.query_one("#launch-docs-btn", Button).disabled = False
            self.query_one("#stop-docs-btn", Button).disabled = True
