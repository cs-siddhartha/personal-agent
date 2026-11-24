import asyncio
from tools.registry import registry

async def run_shell(command: str) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    output = stdout.output() if stdout else ""
    errors = stderr.output() if stderr else ""

    if errors: 
        output += f"\nSTDERR: {errors}"
    return output.strip() or "(no output)"

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