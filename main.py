import os
import sys
import time
import threading
import subprocess
import tempfile
from pathlib import Path
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


def create_temp_summary_file(summary: str) -> Path:
    file_descriptor, file_path = tempfile.mkstemp(
        prefix="commit_summary_",
        suffix=".txt",
        text=True,
    )

    path = Path(file_path)

    with os.fdopen(file_descriptor, "w", encoding="utf-8") as file:
        file.write(summary)

        if not summary.endswith("\n"):
            file.write("\n")

    return path


def open_notepad_and_wait(file_path: Path) -> None:
    if os.name != "nt":
        raise RuntimeError("Este fluxo foi configurado para abrir o Bloco de Notas no Windows.")

    subprocess.run(
        ["notepad.exe", str(file_path)],
        check=True,
    )


def read_summary_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8").strip()


def delete_temp_file(file_path: Path) -> None:
    try:
        file_path.unlink(missing_ok=True)
    except OSError as error:
        print(f"Não foi possível apagar o arquivo temporário: {error}")


def ask_send_by_email() -> bool:
    while True:
        answer = input("Enviar resumo por e-mail? (y/n): ").strip().lower()

        if answer in {"y", "yes", "s", "sim"}:
            return True

        if answer in {"n", "no", "nao", "não"}:
            return False

        print("Opção inválida. Digite y para enviar ou n para cancelar.")


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

    temp_summary_file: Path | None = None

    try:
        temp_summary_file = create_temp_summary_file(summary)

        print("Resumo salvo em arquivo temporário.")
        print(f"Arquivo: {temp_summary_file}")
        print("O Bloco de Notas será aberto.")
        print("Edite o resumo, salve o arquivo e feche o Bloco de Notas para continuar.\n")

        open_notepad_and_wait(temp_summary_file)

        edited_summary = read_summary_file(temp_summary_file)

        if not edited_summary:
            print("O resumo ficou vazio. Nenhum e-mail será enviado.")
            return

        should_send_email = ask_send_by_email()

        if should_send_email:
            run_with_loading(
                "Enviando resumo por e-mail...",
                send_email,
                edited_summary,
            )

            print("Resumo enviado por e-mail com sucesso.")
        else:
            print("Envio cancelado.")

    finally:
        if temp_summary_file is not None:
            delete_temp_file(temp_summary_file)


if __name__ == "__main__":
    main()