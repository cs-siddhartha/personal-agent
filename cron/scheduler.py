import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

JOBS_DIR = os.path.expanduser("~/.my-agent")
JOBS_FILE = os.path.join(JOBS_DIR, "jobs.json")
logger = logging.getLogger(__name__)


class CronScheduler:
    def __init__(self, agent, gateway):
        self.agent = agent
        self.gateway = gateway
        self._running = False

    def _load_jobs(self) -> list[dict]:
        """Load scheduled jobs from the JSON file."""
        if not os.path.exists(JOBS_FILE):
            return []
        with open(JOBS_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _save_jobs(self, jobs: list[dict]):
        """Replace the jobs file only after the full list has been written."""
        os.makedirs(JOBS_DIR, exist_ok=True)
        with TemporaryDirectory(dir=JOBS_DIR) as directory:
            temp_path = Path(directory) / "jobs.json"
            with temp_path.open("w", encoding="utf-8") as temp_file:
                json.dump(jobs, temp_file, indent=2)
            os.replace(temp_path, JOBS_FILE)

    def add_job(
        self, prompt: str, channel_id: str, user_id: str, interval_minutes: int
    ) -> dict:
        """Add a new scheduled job and compute its next_run time."""
        if type(interval_minutes) is not int or interval_minutes < 1:
            raise ValueError("interval_minutes must be a positive integer")

        jobs = self._load_jobs()
        job = {
            "prompt": prompt,
            "channel_id": channel_id,
            "user_id": user_id,
            "interval_minutes": interval_minutes,
            "next_run": (
                datetime.now() + timedelta(minutes=interval_minutes)
            ).isoformat(),
        }
        jobs.append(job)
        self._save_jobs(jobs)
        return job

    async def _check_and_run_jobs(self):
        """Check all jobs and fire any that are due."""
        jobs = self._load_jobs()
        now = datetime.now()
        due_jobs = []

        for job in jobs:
            next_run = datetime.fromisoformat(job["next_run"])
            if now >= next_run:
                job["next_run"] = (
                    now + timedelta(minutes=job["interval_minutes"])
                ).isoformat()
                due_jobs.append(job)

        if due_jobs:
            # Save before yielding so new jobs cannot be overwritten by this snapshot.
            self._save_jobs(jobs)

        for job in due_jobs:
            channel_id = job["channel_id"]
            user_id = job["user_id"]
            try:
                response = await self.agent.run_conversation(
                    f"cron:{channel_id}:{user_id}",
                    job["prompt"],
                    channel_id=channel_id,
                    user_id=user_id,
                )
                channel = self.gateway.channels.get(channel_id)
                if channel:
                    await channel.send_message(user_id, response)
            except Exception:
                logger.exception("Scheduled job failed for channel %s", channel_id)

    async def start(self):
        """Main loop that checks for due jobs every 60 seconds."""
        self._running = True
        print("Cron scheduler started.")
        while self._running:
            await self._check_and_run_jobs()
            await asyncio.sleep(60)

    def stop(self):
        self._running = False
