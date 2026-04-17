@echo off
setlocal

cd /d "%~dp0\.."

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
  echo No se encontro el entorno virtual en .venv
  echo Ejecuta primero apps\setup_venv.bat
  pause
  exit /b 1
)

set "LIMIT=%~1"
if "%LIMIT%"=="" set "LIMIT=200"
set "FLAG=%~2"

echo.
echo === Coworkia: INX daily ===
echo Repo: %CD%
echo Limit: %LIMIT%
echo.

if /I "%FLAG%"=="--allow-missing-ptn" (
  "%VENV_PYTHON%" apps\inx_daily.py --limit %LIMIT% --allow-missing-ptn
) else (
  "%VENV_PYTHON%" apps\inx_daily.py --limit %LIMIT%
)
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: inx_daily finalizo con exit code %ERR%.

pause
exit /b %ERR%
