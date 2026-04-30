import subprocess
from datetime import datetime


def get_today_commits(repo_path: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    command = [
        "git",
        "-C",
        repo_path,
        "log",
        f"--since={today} 00:00",
        f"--until={today} 23:59",
        "--pretty=format:%h - %s%n%b%n---",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )

    return result.stdout.strip()