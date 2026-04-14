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

REM Permite pasar un limite opcional: apps\sync_todoist_to_notion.bat 200
set "LIMIT=%~1"
if "%LIMIT%"=="" set "LIMIT=200"

REM Modo no interactivo: apps\sync_todoist_to_notion.bat 200 --no-pause
set "NO_PAUSE=%~2"

echo.
echo === Coworkia: Sync Todoist -> Notion ===
echo Repo: %CD%
echo Python: %VENV_PYTHON%
echo Limit: %LIMIT%
echo.

"%VENV_PYTHON%" tools\sync_todoist_to_notion.py --limit %LIMIT%
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" (
  echo ERROR: el sync fallo con exit code %ERR%.
  echo Sugerencia: ejecuta apps\config_doctor.bat para ver variables faltantes.
)

echo.
if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause

