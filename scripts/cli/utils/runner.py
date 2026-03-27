import os
import asyncio
from typing import Callable, Awaitable


async def stream_command(
    command: str,
    cwd: str,
    on_output: Callable[[str], Awaitable[None]],
    on_exit: Callable[[int], Awaitable[None]],
):
    """Executes a command asynchronously and streams the combined stdout/stderr to a callback."""
    env = os.environ.copy()
    # Ensure current directory is in python path for the subprocess
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{cwd}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = cwd

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd,
        env=env,
    )

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        await on_output(line.decode().rstrip())

    returncode = await process.wait()
    await on_exit(returncode)
