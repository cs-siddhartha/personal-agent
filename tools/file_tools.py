import os
from tools.registry import registry


# Read the contents of a file, with truncation for large files
async def read_file(path: str) -> str:
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return f"Error: File not found: {path}"
    with open(expanded, "r") as f:
        content = f.read()
    if len(content) > 10000:
        content = content[:10000] + "\n... (truncated)"
    return content


# Write content to a file, creating directories if needed
async def write_file(path: str, content: str) -> str:
    expanded = os.path.expanduser(path)
    os.makedirs(os.path.dirname(expanded) or ".", exist_ok=True)
    with open(expanded, "w") as f:
        f.write(content)
    return f"Successfully wrote {len(content)} characters to {path}"


registry.register(
    name="read_file",
    description="Read the contents of a file at the given path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The file path to read",
            }
        },
        "required": ["path"],
    },
    handler=read_file,
)

registry.register(
    name="write_file",
    description="Write content to a file at the given path. Creates directories if needed.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The file path to write to",
            },
            "content": {
                "type": "string",
                "description": "The content to write",
            },
        },
        "required": ["path", "content"],
    },
    handler=write_file,
)