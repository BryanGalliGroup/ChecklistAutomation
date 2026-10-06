@echo off
setlocal EnableExtensions

REM ============================================================
REM CONFIGURAÇÃO
REM ============================================================

set "AUTOMATION_DIR=%~dp0"

if "%AUTOMATION_DIR:~-1%"=="\" set "AUTOMATION_DIR=%AUTOMATION_DIR:~0,-1%"

set "VENV_PYTHON=%AUTOMATION_DIR%\.venv\Scripts\python.exe"
set "MAIN_FILE=%AUTOMATION_DIR%\main.py"
set "CLI_FILE=%AUTOMATION_DIR%\cli.py"
set "ENV_FILE=%AUTOMATION_DIR%\.env"


REM ============================================================
REM VALIDAÇÕES
REM ============================================================

if not exist "%ENV_FILE%" (
    echo.
    echo Erro: arquivo .env nao encontrado:
    echo %ENV_FILE%
    echo.
    pause
    exit /b 1
)

if not exist "%AUTOMATION_DIR%\.venv\" (
    echo.
    echo Erro: ambiente virtual nao encontrado em:
    echo %AUTOMATION_DIR%\.venv
    echo.
    echo Crie o ambiente executando:
    echo python -m venv "%AUTOMATION_DIR%\.venv"
    echo.
    pause
    exit /b 1
)

if not exist "%VENV_PYTHON%" (
    echo.
    echo Erro: executavel Python do ambiente virtual nao encontrado:
    echo %VENV_PYTHON%
    echo.
    pause
    exit /b 1
)


REM ============================================================
REM DEFINIÇÃO DO MODO
REM ============================================================

set "MODE=gui"

if /I "%~1"=="--cli" (
    set "MODE=terminal"
) else if not "%~1"=="" (
    echo.
    echo Erro: argumento invalido: %~1
    echo.
    echo Uso:
    echo   script.bat
    echo   script.bat --cli
    echo.
    pause
    exit /b 1
)


REM ============================================================
REM VALIDAÇÃO DO ARQUIVO DE EXECUÇÃO
REM ============================================================

if "%MODE%"=="gui" (
    if not exist "%MAIN_FILE%" (
        echo.
        echo Erro: arquivo principal nao encontrado:
        echo %MAIN_FILE%
        echo.
        pause
        exit /b 1
    )
) else (
    if not exist "%CLI_FILE%" (
        echo.
        echo Erro: arquivo CLI nao encontrado:
        echo %CLI_FILE%
        echo.
        pause
        exit /b 1
    )
)


REM ============================================================
REM EXECUÇÃO
REM ============================================================

cd /d "%AUTOMATION_DIR%"

echo.
echo ========================================
echo       AUTOMACAO DE CHECKLIST
echo ========================================
echo.

if "%MODE%"=="gui" (
    "%VENV_PYTHON%" "%MAIN_FILE%"
) else (
    "%VENV_PYTHON%" "%CLI_FILE%"
)

set "EXIT_CODE=%ERRORLEVEL%"

echo.

if "%EXIT_CODE%"=="0" (
    echo Automacao finalizada com sucesso.
) else (
    echo Automacao finalizada com erro.
    echo Codigo de saida: %EXIT_CODE%
)

echo.
pause

exit /b %EXIT_CODE%