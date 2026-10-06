import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from src.commit_collector import get_today_commits
from src.ia_client import generate_summary
from src.email_sender import send_email
from src.logger import Logger


def resolve_project_path(project_path: str) -> Path:
    path = Path(project_path).expanduser()

    if path.is_absolute():
        return path.resolve()

    base_dir = Path(__file__).resolve().parent.parent

    return (base_dir / path).resolve()


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


def executable_exists(executable: str) -> bool:
    executable_path = Path(executable)

    if executable_path.is_absolute():
        return executable_path.is_file()

    return shutil.which(executable) is not None


def add_wait_argument(command: list[str]) -> list[str]:
    if not command:
        return command

    executable_name = Path(command[0]).name.lower()

    wait_arguments = {
        "code": "--wait",
        "code-insiders": "--wait",
        "codium": "--wait",
        "gedit": "--wait",
        "xed": "--wait",
        "kate": "--block",
        "subl": "--wait",
    }

    wait_argument = wait_arguments.get(executable_name)

    if wait_argument and wait_argument not in command:
        command.append(wait_argument)

    return command


def get_configured_editor_command(
    file_path: Path,
    editor_command: str | None,
) -> list[str] | None:
    if not editor_command:
        return None

    command = shlex.split(editor_command)

    if not command:
        return None

    if not executable_exists(command[0]):
        raise RuntimeError(
            f"O editor configurado não foi encontrado: {command[0]}"
        )

    command = add_wait_argument(command)
    command.append(str(file_path))

    return command


def get_linux_editor_command(
    file_path: Path,
    editor_command: str | None,
) -> list[str]:
    configured_command = get_configured_editor_command(
        file_path,
        editor_command,
    )

    if configured_command:
        return configured_command

    graphical_session_available = bool(
        os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")
    )

    graphical_editors = [
        ["gedit", "--wait"],
        ["xed", "--wait"],
        ["kate", "--block"],
        ["code", "--wait"],
        ["code-insiders", "--wait"],
        ["codium", "--wait"],
        ["subl", "--wait"],
        ["mousepad", "--disable-server"],
    ]

    terminal_editors = [
        ["nano"],
        ["vim"],
        ["vi"],
    ]

    if graphical_session_available:
        for editor_command in graphical_editors:
            if executable_exists(editor_command[0]):
                return [*editor_command, str(file_path)]

    for editor_command in terminal_editors:
        if executable_exists(editor_command[0]):
            return [*editor_command, str(file_path)]

    raise RuntimeError(
        "Nenhum editor de texto compatível foi encontrado no Linux."
    )


def open_editor_and_wait(
    file_path: Path,
    editor_command: str | None,
) -> None:
    if os.name == "nt":
        command = ["notepad.exe", str(file_path)]

    elif sys.platform.startswith("linux"):
        command = get_linux_editor_command(
            file_path,
            editor_command,
        )

    else:
        raise RuntimeError(
            f"Sistema operacional não suportado: {sys.platform}"
        )

    try:
        subprocess.run(
            command,
            check=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            f"O editor não foi encontrado: {command[0]}"
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"O editor foi encerrado com erro. "
            f"Código de saída: {error.returncode}"
        ) from error


def read_summary_file(file_path: Path) -> str:
    return file_path.read_text(
        encoding="utf-8"
    ).strip()


def delete_temp_file(file_path: Path) -> None:
    try:
        file_path.unlink(missing_ok=True)
    except OSError:
        pass


def collect_project_summary(
    project: dict[str, str],
    settings: dict,
    logger: Logger,
) -> str | None:
    project_name = project["name"]
    repository_path = resolve_project_path(project["path"])

    logger.info(f"Projeto: {project_name}")
    logger.info(f"Repositório: {repository_path}")

    if not repository_path.is_dir():
        logger.warning(
            f"Diretório do projeto não encontrado: "
            f"{repository_path}"
        )
        return None

    logger.info(
        f"Coletando commits de {project_name}..."
    )

    commits = get_today_commits(
        str(repository_path)
    )

    if not commits:
        logger.info(
            f"Nenhum commit encontrado hoje em {project_name}."
        )
        return None

    logger.info(
        f"Commits encontrados em {project_name}."
    )

    logger.info(
        f"Gerando resumo de {project_name} com IA..."
    )

    ai_settings = settings.get(
        "ai",
        {}
    )

    summary = generate_summary(
        commits,
        ai_settings,
    )

    logger.success(
        f"Resumo de {project_name} gerado."
    )

    return (
        f"{project_name}\n"
        f"{'─' * len(project_name)}\n"
        f"{summary.strip()}\n"
    )


def prepare_summary(
    projects: list[dict[str, str]],
    settings: dict,
    logger: Logger,
) -> str | None:
    summaries: list[str] = []

    for project in projects:
        summary = collect_project_summary(
            project,
            settings,
            logger,
        )

        if summary:
            summaries.append(summary)

    if not summaries:
        logger.info(
            "Nenhum commit encontrado nos projetos selecionados."
        )
        return None

    final_summary = "\n\n".join(summaries)

    temp_summary_file: Path | None = None

    try:
        temp_summary_file = create_temp_summary_file(
            final_summary
        )

        logger.info(
            "Resumo consolidado criado."
        )

        logger.info(
            f"Arquivo temporário: {temp_summary_file}"
        )

        editor_command = (
            settings
            .get("editor", {})
            .get("command")
        )

        logger.info(
            "Abrindo editor para revisão do resumo..."
        )

        open_editor_and_wait(
            temp_summary_file,
            editor_command,
        )

        edited_summary = read_summary_file(
            temp_summary_file
        )

        if not edited_summary:
            logger.warning(
                "O resumo ficou vazio."
            )
            return None

        logger.success(
            "Resumo revisado com sucesso."
        )

        return edited_summary

    finally:
        if temp_summary_file:
            delete_temp_file(temp_summary_file)


def send_summary_email(
    summary: str,
    settings: dict,
    logger: Logger,
) -> None:
    logger.info(
        "Enviando resumo consolidado por e-mail..."
    )

    email_settings = settings.get(
        "email",
        {},
    )

    send_email(
        summary,
        email_settings,
    )

    logger.success(
        "Resumo enviado por e-mail com sucesso."
    )