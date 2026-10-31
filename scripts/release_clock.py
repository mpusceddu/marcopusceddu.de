"""Start the existing publisher at today's approved time; never alter releases."""
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import os
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def todays_due(root, now):
    local_day = now.astimezone(ZoneInfo("Europe/Berlin")).date()
    times = set()
    for manifest in (root / "_scheduled").glob("*/release.json"):
        due = datetime.fromisoformat(json.loads(manifest.read_text())["publish_at"])
        if due.tzinfo is None:
            raise ValueError("Release time must include timezone")
        if due.astimezone(ZoneInfo("Europe/Berlin")).date() == local_day:
            times.add(due)
    return sorted(times)

if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    for due in todays_due(ROOT, now):
        wait = max(0, (due - datetime.now(timezone.utc)).total_seconds())
        if wait > 7200:
            print("Outside two-hour warmup window:", due.isoformat(), flush=True)
            continue
        print("Approved time:", due.isoformat(), flush=True)
        while datetime.now(timezone.utc) < due:
            time.sleep(min(30, (due - datetime.now(timezone.utc)).total_seconds()))
        # Dispatch current main, not the early checkout. The builder rechecks all gates.
        req = urllib.request.Request(
            "https://api.github.com/repos/" + os.environ["GITHUB_REPOSITORY"] +
            "/actions/workflows/pages.yml/dispatches",
            data=json.dumps({"ref": "main"}).encode(), method="POST",
            headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                     "Accept": "application/vnd.github+json", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status != 204:
                raise RuntimeError("Dispatch not accepted")
        print("Publisher requested; this is NOT live confirmation.", flush=True)
