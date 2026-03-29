"""Pruebas unitarias para scripts/cli/utils/runner.py"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch


from scripts.cli.utils.runner import stream_command


class TestStreamCommand:
    """Pruebas para stream_command."""

    async def test_stream_command_calls_on_output_for_each_line(self):
        """Verifica que on_output se invoca por cada línea de salida."""
        lines_received: list[str] = []

        async def on_output(line: str):
            lines_received.append(line)

        async def on_exit(code: int):
            pass

        # Simular proceso que emite dos líneas y termina
        mock_process = MagicMock()
        mock_process.returncode = 0

        async def fake_readline():
            fake_readline._calls = getattr(fake_readline, "_calls", 0) + 1
            if fake_readline._calls == 1:
                return b"linea uno\n"
            elif fake_readline._calls == 2:
                return b"linea dos\n"
            else:
                return b""

        mock_process.stdout = MagicMock()
        mock_process.stdout.readline = fake_readline
        mock_process.wait = AsyncMock(return_value=0)

        with patch(
            "scripts.cli.utils.runner.asyncio.create_subprocess_shell",
            AsyncMock(return_value=mock_process),
        ):
            await stream_command("echo test", "/tmp", on_output, on_exit)

        assert lines_received == ["linea uno", "linea dos"]

    async def test_stream_command_calls_on_exit_with_return_code(self):
        """Verifica que on_exit recibe el código de retorno correcto."""
        exit_codes: list[int] = []

        async def on_output(line: str):
            pass

        async def on_exit(code: int):
            exit_codes.append(code)

        mock_process = MagicMock()
        mock_process.returncode = 1

        async def fake_readline():
            return b""

        mock_process.stdout = MagicMock()
        mock_process.stdout.readline = fake_readline
        mock_process.wait = AsyncMock(return_value=1)

        with patch(
            "scripts.cli.utils.runner.asyncio.create_subprocess_shell",
            AsyncMock(return_value=mock_process),
        ):
            await stream_command("false", "/tmp", on_output, on_exit)

        assert exit_codes == [1]

    async def test_stream_command_strips_trailing_newline(self):
        """Verifica que las líneas no tienen salto de línea al final."""
        lines_received: list[str] = []

        async def on_output(line: str):
            lines_received.append(line)

        async def on_exit(code: int):
            pass

        mock_process = MagicMock()

        async def fake_readline():
            fake_readline._calls = getattr(fake_readline, "_calls", 0) + 1
            if fake_readline._calls == 1:
                return b"hola mundo\n"
            return b""

        mock_process.stdout = MagicMock()
        mock_process.stdout.readline = fake_readline
        mock_process.wait = AsyncMock(return_value=0)

        with patch(
            "scripts.cli.utils.runner.asyncio.create_subprocess_shell",
            AsyncMock(return_value=mock_process),
        ):
            await stream_command("echo hola", "/tmp", on_output, on_exit)

        assert lines_received == ["hola mundo"]

    async def test_stream_command_sets_pythonpath(self):
        """Verifica que PYTHONPATH queda configurado en el entorno del subproceso."""
        captured_env: dict = {}

        mock_process = MagicMock()

        async def fake_readline():
            return b""

        mock_process.stdout = MagicMock()
        mock_process.stdout.readline = fake_readline
        mock_process.wait = AsyncMock(return_value=0)

        async def capture_subprocess(cmd, **kwargs):
            captured_env.update(kwargs.get("env", {}))
            return mock_process

        async def noop_output(line: str):
            pass

        async def noop_exit(code: int):
            pass

        with patch(
            "scripts.cli.utils.runner.asyncio.create_subprocess_shell",
            capture_subprocess,
        ):
            await stream_command("echo ok", "/proyecto", noop_output, noop_exit)

        assert "PYTHONPATH" in captured_env
        assert "/proyecto" in captured_env["PYTHONPATH"]

    async def test_stream_command_success_zero_exit(self):
        """Prueba de integración ligera: comando real que existe (exit 0)."""
        received_lines: list[str] = []
        exit_codes: list[int] = []

        async def on_output(line: str):
            received_lines.append(line)

        async def on_exit(code: int):
            exit_codes.append(code)

        await stream_command("echo yastubo", "/tmp", on_output, on_exit)

        assert exit_codes == [0]
        assert any("yastubo" in line for line in received_lines)
