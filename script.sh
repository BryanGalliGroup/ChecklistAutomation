#!/usr/bin/env bash

set -Eeuo pipefail


# ============================================================
# CONFIGURAÇÃO
# ============================================================

AUTOMATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_PYTHON="$AUTOMATION_DIR/.venv/bin/python"
MAIN_FILE="$AUTOMATION_DIR/main.py"
CLI_FILE="$AUTOMATION_DIR/cli.py"
ENV_FILE="$AUTOMATION_DIR/.env"


# ============================================================
# VALIDAÇÕES
# ============================================================

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Erro: arquivo .env não encontrado:"
    echo "$ENV_FILE"
    exit 1
fi

if [[ ! -d "$AUTOMATION_DIR/.venv" ]]; then
    echo "Erro: ambiente virtual não encontrado:"
    echo "$AUTOMATION_DIR/.venv"
    echo
    echo "Crie o ambiente executando:"
    echo "python3 -m venv \"$AUTOMATION_DIR/.venv\""
    exit 1
fi

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "Erro: executável Python do ambiente virtual não encontrado:"
    echo "$VENV_PYTHON"
    exit 1
fi


# ============================================================
# DEFINIÇÃO DO MODO
# ============================================================

MODE="gui"

if [[ "${1:-}" == "--cli" ]]; then
    MODE="terminal"
elif [[ -n "${1:-}" ]]; then
    echo "Erro: argumento inválido: $1"
    echo
    echo "Uso:"
    echo "  ./script.sh"
    echo "  ./script.sh --cli"
    exit 1
fi


# ============================================================
# VALIDAÇÃO DO ARQUIVO DE EXECUÇÃO
# ============================================================

if [[ "$MODE" == "gui" ]]; then
    if [[ ! -f "$MAIN_FILE" ]]; then
        echo "Erro: arquivo principal não encontrado:"
        echo "$MAIN_FILE"
        exit 1
    fi
else
    if [[ ! -f "$CLI_FILE" ]]; then
        echo "Erro: arquivo CLI não encontrado:"
        echo "$CLI_FILE"
        exit 1
    fi
fi


# ============================================================
# EXECUÇÃO
# ============================================================

cd "$AUTOMATION_DIR"

echo
echo "========================================"
echo "       AUTOMAÇÃO DE CHECKLIST"
echo "========================================"
echo

if [[ "$MODE" == "gui" ]]; then
    exec "$VENV_PYTHON" "$MAIN_FILE"
else
    exec "$VENV_PYTHON" "$CLI_FILE"
fi