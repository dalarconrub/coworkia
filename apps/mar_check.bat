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

REM Uso:
REM   apps\mar_check.bat
REM   apps\mar_check.bat 200
REM   apps\mar_check.bat 200 --no-pause
REM
REM Param 1: LIMIT (default 200)
REM Param 2: --no-pause (opcional)
set "LIMIT=%~1"
if "%LIMIT%"=="" set "LIMIT=200"
set "NO_PAUSE=%~2"

echo.
echo === Coworkia: MAR check (sync + doctor) ===
echo Repo: %CD%
echo Python: %VENV_PYTHON%
echo Limit: %LIMIT%
echo.

REM 1) Sync Todoist -> Notion (recalcula Tipo MAR y propiedades)
"%VENV_PYTHON%" tools\sync_todoist_to_notion.py --limit %LIMIT%
set "ERR=%errorlevel%"
if not "%ERR%"=="0" goto :end

echo.
REM 2) Doctor (todos los checks MAR + consistencia)
"%VENV_PYTHON%" apps\mar_doctor.py ^
  --check-duplicates ^
  --check-missing-tipo ^
  --check-evento-hora ^
  --check-habito-recurrencia ^
  --check-meta-deadline ^
  --check-tarea-fecha ^
  --check-idea-sin-fechas ^
  --check-tipo-consistency ^
  --max 20
set "ERR=%errorlevel%"

:end
echo.
if not "%ERR%"=="0" echo ERROR: MAR check termino con exit code %ERR%.
echo.
if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%

