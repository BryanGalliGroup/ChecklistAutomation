import os
import subprocess
import smtplib
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv
from google import genai


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


def generate_summary(commits: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt_base = os.getenv("PROMPT_BASE", "")
    prompt = f"""
{prompt_base}

Commits do dia:

{commits}
""".strip()

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )

    return response.text or ""


def send_email(body: str) -> None:
    msg = EmailMessage()
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = os.getenv("EMAIL_TO")
    msg["Subject"] = os.getenv("EMAIL_SUBJECT", "Checklist de Atividades | [DAY]").replace("[DAY]", datetime.now().strftime("%d/%m"))
    msg.set_content(body)

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def main():
    load_dotenv()

    repo_path = os.getenv("REPO_PATH", ".")
    commits = get_today_commits(repo_path)

    if not commits:
        print("Nenhum commit encontrado hoje.")
        return

    summary = generate_summary(commits)
    send_email(summary)

    print("Resumo enviado por e-mail com sucesso.")


if __name__ == "__main__":
    main()