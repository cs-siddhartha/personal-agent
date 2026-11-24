import asyncio
import json
import os
from datetime import datetime, timedelta

JOBS_DIR = os.path.expanduser("~/.my-agent")
JOBS_FILE = os.path.join(JOBS_DIR, "jobs.json")


class CronScheduler:
    def __init__(self, agent, gateway):
        self.agent = agent
        self.gateway = gateway
        self._running = False

    def _load_jobs(self) -> list[dict]:
        """Load scheduled jobs from the JSON file."""
        if not os.path.exists(JOBS_FILE):
            return []
        with open(JOBS_FILE, "r") as f:
            return json.load(f)

    def _save_jobs(self, jobs: list[dict]):
        """Save the current jobs list back to disk."""
        os.makedirs(JOBS_DIR, exist_ok=True)
        with open(JOBS_FILE, "w") as f:
            json.dump(jobs, f, indent=2)

    def add_job(self, prompt: str, channel_id: str, user_id: str, interval_minutes: int) -> dict:
        """Add a new scheduled job and compute its next_run time."""
        jobs = self._load_jobs()
        job = {
            "prompt": prompt,
            "channel_id": channel_id,
            "user_id": user_id,
            "interval_minutes": interval_minutes,
            "next_run": (datetime.now() + timedelta(minutes=interval_minutes)).isoformat(),
        }
        jobs.append(job)
        self._save_jobs(jobs)
        return job

    async def _check_and_run_jobs(self):
        """Check all jobs and fire any that are due."""
        jobs = self._load_jobs()
        now = datetime.now()
        updated = False

        for job in jobs:
            next_run = datetime.fromisoformat(job["next_run"])
            if now >= next_run:
                # Run the job's prompt through a fresh conversation
                session_id = f"cron:{job['channel_id']}:{job['user_id']}"
                response = await self.agent.run_conversation(session_id, job["prompt"])

                # Deliver the response to the target channel
                channel = self.gateway.channels.get(job["channel_id"])
                if channel:
                    await channel.send_message(job["user_id"], response)

                # Schedule the next run
                job["next_run"] = (
                    now + timedelta(minutes=job["interval_minutes"])
                ).isoformat()
                updated = True

        if updated:
            self._save_jobs(jobs)

    async def start(self):
        """Main loop that checks for due jobs every 60 seconds."""
        self._running = True
        print("Cron scheduler started.")
        while self._running:
            await self._check_and_run_jobs()
            await asyncio.sleep(60)

    def stop(self):
        self._running = False