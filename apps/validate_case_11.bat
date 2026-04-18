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
echo === 1) Regenerar timeline de hoy (incluye seccion Journal) ===
"%VENV_PYTHON%" tools\timeline.py
if errorlevel 1 goto :end
echo.
echo === 2) Informe validacion caso 11 ===
"%VENV_PYTHON%" tools\validate_case_11.py
set "ERR=%errorlevel%"
:end
echo.
if /I "%NO_PAUSE%"=="--no-pause" exit /b %ERR%
pause
exit /b %ERR%
