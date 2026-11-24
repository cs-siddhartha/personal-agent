import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import tool modules to trigger self-registration
import tools.shell_tool
import tools.file_tools
import tools.web_tool
import tools.memory_tool
import tools.schedule_tool
from cron.scheduler import CronScheduler

from agent import Agent
from gateway import Gateway
from channels.cli_channel import CLIChannel
from channels.telegram_channel import TelegramChannel


async def main():
    agent = Agent()
    gateway = Gateway(agent)

    # Register channels
    telegram = TelegramChannel()
    cli = CLIChannel()

    gateway.register_channel(telegram)
    gateway.register_channel(cli)

    # Start Telegram in background
    await telegram.start()
    scheduler = CronScheduler(agent, gateway)
    tools.schedule_tool.set_scheduler(scheduler)
    scheduler_task = asyncio.create_task(scheduler.start())

    # Run CLI in foreground (blocks until user exits)
    await cli.start()

    # Cleanup
    await telegram.stop()
    scheduler.stop()
    scheduler_task.cancel()
    await telegram.stop()


if __name__ == "__main__":
    asyncio.run(main())