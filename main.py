import os
import sys
import time
import threading
from itertools import cycle
from typing import Callable, TypeVar

from dotenv import load_dotenv

from src.commit_collector import get_today_commits
from src.ia_client import generate_summary
from src.email_sender import send_email


T = TypeVar("T")


def run_with_loading(
    message: str,
    action: Callable[..., T],
    *args,
    **kwargs
) -> T:
    stop_event = threading.Event()
    spinner = cycle(["\\", "|", "/", "-"])

    def animate() -> None:
        while not stop_event.is_set():
            frame = next(spinner)
            sys.stdout.write(f"\r{message} {frame}")
            sys.stdout.flush()
            time.sleep(0.12)

        sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
        sys.stdout.flush()

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()

    try:
        return action(*args, **kwargs)
    finally:
        stop_event.set()
        thread.join()


def main() -> None:
    load_dotenv()

    repo_path = os.getenv("REPO_PATH", ".")

    commits = run_with_loading(
        "Coletando commits do repositório...",
        get_today_commits,
        repo_path,
    )

    if not commits:
        print("Nenhum commit encontrado hoje.")
        return

    print(f"Commits coletados:\n{commits}\n")

    summary = run_with_loading(
        "Gerando resumo com IA...",
        generate_summary,
        commits,
    )

    print(f"Resumo gerado:\n{summary}\n")

    run_with_loading(
        "Enviando resumo por e-mail...",
        send_email,
        summary,
    )

    print("Resumo enviado por e-mail com sucesso.")


if __name__ == "__main__":
    main()