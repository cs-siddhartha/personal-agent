from tools.registry import registry

# This will be set by main.py after the scheduler is created
_scheduler = None


def set_scheduler(scheduler):
    """Called by main.py to inject the scheduler instance."""
    global _scheduler
    _scheduler = scheduler


async def schedule_task(
    prompt: str, interval_minutes: int, channel_id: str, user_id: str
) -> str:
    """Schedule a recurring task for the agent."""
    if _scheduler is None:
        return "Error: Scheduler not initialized."
    job = _scheduler.add_job(prompt, channel_id, user_id, interval_minutes)
    return (
        f"Scheduled! I will run '{prompt}' every {interval_minutes} minutes. "
        f"Next run: {job['next_run']}"
    )


registry.register(
    name="schedule_task",
    description="Schedule a recurring task. The agent will run the given prompt at the specified interval and deliver the response to the user's channel.",
    parameters={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt to run on each scheduled execution",
            },
            "interval_minutes": {
                "type": "integer",
                "description": "How often to run this task, in minutes",
            },
            "channel_id": {
                "type": "string",
                "description": "The channel to deliver results to (e.g. 'telegram')",
            },
            "user_id": {
                "type": "string",
                "description": "The user ID to send results to",
            },
        },
        "required": ["prompt", "interval_minutes", "channel_id", "user_id"],
    },
    handler=schedule_task,
)