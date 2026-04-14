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

echo.
echo === Coworkia: Ensure schema TODOIST-TAREAS ===
echo Repo: %CD%
echo Python: %VENV_PYTHON%
echo.

"%VENV_PYTHON%" tools\ensure_todoist_tasks_schema.py
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: no se pudo asegurar el schema (exit code %ERR%).
if not "%ERR%"=="0" echo Sugerencia: ejecuta apps\notion_doctor.bat para verificar acceso/IDs.

echo.
pause

