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
echo === 1) Log Obsidian -^> OBSIDIAN_DB ===
"%VENV_PYTHON%" tools\log_obsidian_changes.py
if errorlevel 1 goto :end
echo.
echo === 2) Log PTN -^> NOTION_DB (detecta filas recien creadas en PTN-Notas) ===
"%VENV_PYTHON%" tools\log_ptn_changes.py
if errorlevel 1 goto :end
echo.
echo === 3) Sync INX desde Obsidian ===
"%VENV_PYTHON%" tools\sync_inx_links.py --source obsidian --limit 200
if errorlevel 1 goto :end
echo.
echo === 4) Sync INX desde Notion (cruce ptn:^<id^> de PTN-Notas via log) ===
"%VENV_PYTHON%" tools\sync_inx_links.py --source notion --limit 200
if errorlevel 1 goto :end
echo.
echo === 5) Informe validacion caso 7 ===
"%VENV_PYTHON%" tools\validate_case_07.py
set "ERR=%errorlevel%"
:end
echo.
if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%
