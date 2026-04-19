@echo off
setlocal
cd /d "%~dp0\.."
set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
  echo No se encontro .venv. Ejecuta apps\setup_venv.bat
  pause
  exit /b 1
)
"%VENV_PYTHON%" tools\sync_bib_reading_state.py %*
set "ERR=%errorlevel%"
echo.
pause
exit /b %ERR%
