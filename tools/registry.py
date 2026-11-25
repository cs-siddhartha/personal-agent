import json
from collections.abc import Awaitable, Callable


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[..., Awaitable[str]],
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[..., Awaitable[str]],
    ):
        self._tools[name] = Tool(name, description, parameters, handler)

    def get_schemas(self) -> list[dict]:
        return [tool.schema() for tool in self._tools.values()]

    async def dispatch(self, name: str, arguments: str, **context: str) -> str:
        if name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            args = json.loads(arguments)
            # Caller-supplied context takes precedence over model-generated arguments.
            args.update(context)
            result = await self._tools[name].handler(**args)
            return result
        except Exception as e:  # noqa: BLE001 - tool failures are returned to the model
            return json.dumps({"error": str(e)})


registry = ToolRegistry()
