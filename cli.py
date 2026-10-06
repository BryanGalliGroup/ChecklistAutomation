import sys

from src.automation import (
    prepare_summary,
    send_summary_email,
)
from src.config import load_config
from src.logger import Logger


def ask_send_by_email() -> bool:
    while True:
        answer = input(
            "\nDeseja enviar o resumo por e-mail? [S/n]: "
        ).strip().lower()

        if answer in ("", "s", "sim"):
            return True

        if answer in ("n", "nao", "não"):
            return False

        print("Resposta inválida. Digite S ou N.")


def select_projects(projects: list[dict]) -> list[dict]:
    if not projects:
        print("Nenhum projeto configurado.")
        return []

    print("\nProjetos disponíveis:\n")

    for index, project in enumerate(projects, start=1):
        print(
            f"  {index}. "
            f"{project['name']} "
            f"({project['key']})"
        )

    print("\nDigite os números dos projetos separados por vírgula.")
    print("Digite 'a' para selecionar todos.")

    while True:
        value = input("\nProjetos: ").strip().lower()

        if value == "a":
            return projects

        try:
            indexes = [
                int(item.strip())
                for item in value.split(",")
            ]
        except ValueError:
            print("Seleção inválida.")
            continue

        if not indexes:
            print("Selecione pelo menos um projeto.")
            continue

        if any(
            index < 1 or index > len(projects)
            for index in indexes
        ):
            print("Um ou mais números são inválidos.")
            continue

        selected = []
        seen = set()

        for index in indexes:
            if index in seen:
                continue

            seen.add(index)
            selected.append(projects[index - 1])

        return selected


def main() -> int:
    try:
        config = load_config()

        projects = config["projects"]
        settings = config["settings"]

        selected_projects = select_projects(
            projects
        )

        if not selected_projects:
            print("\nNenhum projeto selecionado.")
            return 0

        logger = Logger(
            callback=lambda message: print(message)
        )

        summary = prepare_summary(
            selected_projects,
            settings,
            logger,
        )

        if not summary:
            print("\nNenhum resumo foi gerado.")
            return 0

        print("\n========================================")
        print("RESUMO CONSOLIDADO")
        print("========================================")
        print()
        print(summary)
        print("========================================")

        if not ask_send_by_email():
            print("\nEnvio de e-mail cancelado.")
            return 0

        send_summary_email(
            summary,
            settings,
            logger,
        )

        return 0

    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        return 130

    except Exception as error:
        print()
        print(f"Erro: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())