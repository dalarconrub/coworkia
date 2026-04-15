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
echo === Coworkia: INX sync desde NOTION (log PTN) ===
echo Repo: %CD%
echo Limit: %LIMIT%
echo.

echo --- 1) Log PTN -^> NOTION_DB ---
"%VENV_PYTHON%" tools\log_ptn_changes.py
if errorlevel 1 goto :end

echo.
echo --- 2) Sync INX desde Notion (PTN log) ---
"%VENV_PYTHON%" tools\sync_inx_links.py --source notion --limit %LIMIT%
set "ERR=%errorlevel%"

:end
echo.
if not "%ERR%"=="0" echo ERROR: sync INX notion fallo (exit code %ERR%).

if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%

