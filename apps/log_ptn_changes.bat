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

set "NO_PAUSE=%~1"

echo.
echo === Coworkia: PTN log -^> NOTION_DB ===
echo Repo: %CD%
echo.

"%VENV_PYTHON%" tools\log_ptn_changes.py
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: log PTN fallo (exit code %ERR%).

if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%

