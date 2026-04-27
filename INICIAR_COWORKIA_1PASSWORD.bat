@echo off
setlocal

cd /d "%~dp0"

rem Arranca Coworkia inyectando env vars desde 1Password CLI.
rem Requisitos:
rem   - 1Password instalado + CLI `op` disponible en PATH
rem   - sesion iniciada: `op signin` (o `op account add` + `op signin`)
rem   - archivo de referencias: `config\env.1password` (ver `config\env.1password.example`)

set "ENV_FILE=%~dp0config\env.1password"

if not exist "%ENV_FILE%" (
    echo [ERROR] No existe "%ENV_FILE%".
    echo         Crea el archivo copiando: config\env.1password.example ^> config\env.1password
    echo.
    pause
    exit /b 1
)

where op >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro el comando "op" (1Password CLI) en PATH.
    echo         Instala 1Password CLI y reinicia la terminal.
    echo.
    pause
    exit /b 1
)

rem `op run` inyecta variables para el proceso hijo. No escribe secretos a disco.
op run --env-file="%ENV_FILE%" -- cmd /c "%~dp0INICIAR_COWORKIA.bat"
set "EXIT_CODE=%errorlevel%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] Coworkia termino con codigo %EXIT_CODE%.
    echo         Si parece un problema de tokens, verifica tu sesion `op` y el item referenciado.
    echo.
    pause
)

endlocal & exit /b %EXIT_CODE%

