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
REM   apps\mar_doctor.bat
REM   apps\mar_doctor.bat --require-desc
REM   apps\mar_doctor.bat --max 100

"%VENV_PYTHON%" apps\mar_doctor.py %*

echo.
pause

