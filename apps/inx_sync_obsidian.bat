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
set "NO_PAUSE=%~2"

echo.
echo === Coworkia: INX sync desde OBSIDIAN (log) ===
echo Repo: %CD%
echo Limit: %LIMIT%
echo.

"%VENV_PYTHON%" tools\sync_inx_links.py --source obsidian --limit %LIMIT%
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: sync INX fallo (exit code %ERR%).

if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%
