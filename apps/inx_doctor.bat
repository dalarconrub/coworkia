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
REM   apps\inx_doctor.bat

"%VENV_PYTHON%" apps\inx_doctor.py %*

echo.
pause
