@echo off
setlocal

cd /d "%~dp0\.."

set "ENV_FILE=%CD%\config\env.1password"

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

rem Ejecuta el cierre bajo 1Password. Si `op` no tiene sesion, veras el error.
op run --env-file="%ENV_FILE%" -- cmd /c "apps\cerrar_sesion.bat"
set "EXIT_CODE=%errorlevel%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [WARN] El cierre termino con codigo %EXIT_CODE%.
    echo        Si parece un problema de 1Password, ejecuta `op signin` y reintenta.
    echo.
)

endlocal & exit /b %EXIT_CODE%

