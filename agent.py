import os

from openai import AsyncOpenAI

from tools.registry import registry

LOCAL_ONLY_TOOLS = {"run_shell", "write_file"}


class Agent:
    def __init__(self):
        # Connect to OpenAI using the API key from environment variables
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = "gpt-4o-mini"
        # Store separate conversation histories keyed by session ID
        self.conversations: dict[str, list[dict]] = {}

    def _load_system_prompt(self) -> str:
        # Build the system prompt from PROMPT.md (personality) and MEMORY.md (persistent memory)
        base_dir = os.path.dirname(__file__)
        prompt_path = os.path.join(base_dir, "PROMPT.md")
        memory_path = os.path.join(base_dir, "MEMORY.md")

        prompt = ""
        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                prompt = f.read()

        memory = ""
        if os.path.exists(memory_path):
            with open(memory_path, "r") as f:
                memory = f.read()

        return f"{prompt}\n\n## Your Memory\n{memory}"

    def _get_history(self, session_id: str) -> list[dict]:
        # Return existing history or create a new empty list for this session
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        return self.conversations[session_id]

    async def run_conversation(
        self, session_id: str, user_message: str, *, channel_id: str, user_id: str
    ) -> str:
        history = self._get_history(session_id)
        history.append({"role": "user", "content": user_message})

        # Build the full message list: system prompt + conversation history
        messages = [
            {"role": "system", "content": self._load_system_prompt()},
            *history,
        ]

        # Get tool schemas so the model knows what tools are available
        tools = [
            schema
            for schema in registry.get_schemas()
            if channel_id == "cli" or schema["function"]["name"] not in LOCAL_ONLY_TOOLS
        ]
        allowed_tools = {schema["function"]["name"] for schema in tools}
        max_iterations = 10

        for _ in range(max_iterations):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
            )

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                # The model wants to call one or more tools
                assistant_message = choice.message
                messages.append(assistant_message.model_dump())

                # Execute each tool call and feed results back
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    if tool_name not in allowed_tools:
                        result = f"Tool '{tool_name}' is unavailable in this channel."
                    else:
                        context = (
                            {"channel_id": channel_id, "user_id": user_id}
                            if tool_name == "schedule_task"
                            else {}
                        )
                        result = await registry.dispatch(
                            tool_name, tool_call.function.arguments, **context
                        )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
            else:
                # The model produced a final text response
                assistant_content = choice.message.content or ""
                history.append({"role": "assistant", "content": assistant_content})
                return assistant_content

        return "I hit my tool-call limit. Please try a simpler request."
