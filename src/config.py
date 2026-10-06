import json
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

PROJECTS_FILE = BASE_DIR / "projects.json"
SETTINGS_FILE = BASE_DIR / "settings.json"
ENV_FILE = BASE_DIR / ".env"


load_dotenv(ENV_FILE)


def _load_json(file_path, default):
    if not file_path.exists():
        return default

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"Não foi possível carregar o arquivo "
            f"{file_path.name}: {error}"
        ) from error


def _save_json(file_path, data):
    try:
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    except OSError as error:
        raise RuntimeError(
            f"Não foi possível salvar o arquivo "
            f"{file_path.name}: {error}"
        ) from error


# ----------------------------------------------------------------------
# Projetos
# ----------------------------------------------------------------------


def load_projects():
    data = _load_json(
        PROJECTS_FILE,
        {"projects": []},
    )

    projects = data.get("projects", [])

    if not isinstance(projects, list):
        raise ValueError(
            "O campo 'projects' do projects.json deve ser uma lista."
        )

    return projects


def save_projects(projects):
    if not isinstance(projects, list):
        raise ValueError("projects deve ser uma lista.")

    _save_json(
        PROJECTS_FILE,
        {
            "projects": projects,
        },
    )


# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------


def load_settings():
    return _load_json(
        SETTINGS_FILE,
        {
            "ai": {
                "model": "gemini-2.5-flash",
                "prompt": "",
            },
            "email": {
                "subject": "",
                "from_name": "",
                "to": [],
            },
            "editor": {
                "command": "",
            },
        },
    )


def save_settings(settings):
    if not isinstance(settings, dict):
        raise ValueError("settings deve ser um objeto.")

    _save_json(
        SETTINGS_FILE,
        settings,
    )


# ----------------------------------------------------------------------
# Variáveis sensíveis / ambiente
# ----------------------------------------------------------------------


def get_env(name, default=None, required=False):
    value = os.getenv(name, default)

    if required and not value:
        raise RuntimeError(
            f"A variável de ambiente '{name}' não está configurada."
        )

    return value


def get_gemini_api_key():
    return get_env(
        "GEMINI_API_KEY",
        required=True,
    )


def get_smtp_config():
    return {
        "host": get_env("SMTP_HOST", required=True),
        "port": int(get_env("SMTP_PORT", "587")),
        "username": get_env("SMTP_USER", required=True),
        "password": get_env("SMTP_PASSWORD", required=True),
    }


# ----------------------------------------------------------------------
# Configuração completa
# ----------------------------------------------------------------------


def load_config():
    return {
        "projects": load_projects(),
        "settings": load_settings(),
    }