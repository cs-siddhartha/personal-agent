import asyncio
from contextlib import suppress

from dotenv import load_dotenv

# Import tool modules to trigger self-registration
import tools.file_tools
import tools.memory_tool
import tools.schedule_tool
import tools.shell_tool
import tools.web_tool
from agent import Agent
from channels.cli_channel import CLIChannel
from channels.telegram_channel import TelegramChannel
from cron.scheduler import CronScheduler
from gateway import Gateway


async def main():
    load_dotenv()
    agent = Agent()
    gateway = Gateway(agent)

    # Register channels
    telegram = TelegramChannel()
    cli = CLIChannel()

    gateway.register_channel(telegram)
    gateway.register_channel(cli)

    scheduler = CronScheduler(agent, gateway)
    tools.schedule_tool.set_scheduler(scheduler)

    try:
        await telegram.start()
        scheduler_task = asyncio.create_task(scheduler.start())
        try:
            await cli.start()
        finally:
            scheduler.stop()
            scheduler_task.cancel()
            with suppress(asyncio.CancelledError):
                await scheduler_task
    finally:
        await telegram.stop()


if __name__ == "__main__":
    asyncio.run(main())
