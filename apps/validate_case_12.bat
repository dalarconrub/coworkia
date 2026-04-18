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
echo === 1) Backfill vault -^> OBSIDIAN_DB (dry-run informativo) ===
"%VENV_PYTHON%" tools\backfill_obsidian_to_inx.py --dry-run
echo.
echo === 2) Log Obsidian (mtime-based) por si hay cambios recientes ===
"%VENV_PYTHON%" tools\log_obsidian_changes.py
if errorlevel 1 goto :end
echo.
echo === 3) Sync INX desde Obsidian ===
"%VENV_PYTHON%" tools\sync_inx_links.py --source obsidian --limit 200
if errorlevel 1 goto :end
echo.
echo === 4) Informe validacion caso 12 ===
"%VENV_PYTHON%" tools\validate_case_12.py
set "ERR=%errorlevel%"
:end
echo.
if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%
