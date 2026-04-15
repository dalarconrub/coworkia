@echo off
setlocal
cd /d "%~dp0\.."
set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
  echo No se encontro .venv. Ejecuta apps\setup_venv.bat
  pause
  exit /b 1
)
set "NO_PAUSE=%~1"
echo.
echo === 1) Sync Todoist -^> TODOIST-TAREAS ===
"%VENV_PYTHON%" tools\sync_todoist_to_notion.py --limit 200
if errorlevel 1 goto :end
echo.
echo === 2) Sync INX desde Todoist ===
"%VENV_PYTHON%" tools\sync_inx_links.py --source todoist --limit 200
if errorlevel 1 goto :end
echo.
echo === 3) Informe validacion caso 2 ===
"%VENV_PYTHON%" tools\validate_case_02.py
set "ERR=%errorlevel%"
:end
echo.
if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%
