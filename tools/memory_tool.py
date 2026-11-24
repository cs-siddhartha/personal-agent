import os
from tools.registry import registry

# Path to the persistent memory file at the project root
MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "MEMORY.md")


# Append a fact to MEMORY.md so it persists across sessions
async def remember(fact: str) -> str:
    with open(MEMORY_FILE, "a") as f:
        f.write(f"\n- {fact}")
    return f"Remembered: {fact}"


registry.register(
    name="remember",
    description="Save an important fact about the user to persistent memory. Use this when you learn something worth remembering across sessions.",
    parameters={
        "type": "object",
        "properties": {
            "fact": {
                "type": "string",
                "description": "The fact to remember",
            }
        },
        "required": ["fact"],
    },
    handler=remember,
)