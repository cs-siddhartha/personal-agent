import asyncio

from tools.registry import registry


async def run_shell(command: str) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    output = stdout.decode(errors="replace").strip()
    errors = stderr.decode(errors="replace").strip()

    result = [f"Exit code: {process.returncode}"]
    if output:
        result.append(output)
    if errors:
        result.append(f"STDERR: {errors}")
    return "\n".join(result)


registry.register(
    name="run_shell",
    description="Execute a shell command on the local machine and return the output.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            }
        },
        "required": ["command"],
    },
    handler=run_shell,
)
