@echo off
setlocal
cd /d "%~dp0\.."
set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
  echo No se encontro .venv. Ejecuta apps\setup_venv.bat
  pause
  exit /b 1
)
if "%~1"=="" (
  echo Uso: apps\close_obsidian_checkboxes_to_todoist.bat "Nombre de nota" [--sync]
  pause
  exit /b 1
)
"%VENV_PYTHON%" tools\close_obsidian_checkboxes_to_todoist.py %*
set "ERR=%errorlevel%"
echo.
pause
exit /b %ERR%
