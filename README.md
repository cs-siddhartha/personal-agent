# Personal Agent

A local AI assistant with a terminal interface, an optional Telegram bot, and recurring tasks.

## Quickstart

Install `uv`, then run `uv sync --locked` from the project directory. The project uses Python 3.14.

Create a `.env` file in the project directory and set `OPENAI_API_KEY`.

```dotenv
OPENAI_API_KEY=your-openai-api-key
```

Run `uv run --locked python main.py`. With only the OpenAI key configured, the agent runs in the terminal. Press Ctrl+C to exit.

## Telegram

To enable Telegram, add both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_OWNER_ID` to `.env`. Set `TELEGRAM_OWNER_ID` to your numeric Telegram user ID. The bot responds only in a private chat with that account. Shell commands and file writes are available from the terminal.

## Local data

Conversation history lasts until the process exits. The agent saves remembered facts in `MEMORY.md` and recurring jobs in `~/.my-agent/jobs.json`. Keep the process running for scheduled jobs to execute.

## Development

Ruff checks lint and formatting through pre-commit. The commit message hook checks the Conventional Commits format.

Project reference [NextWork](https://nextwork.ai/projects/bab2476c-4b41-41a4-9dd7-7379d7b8bd4e)
