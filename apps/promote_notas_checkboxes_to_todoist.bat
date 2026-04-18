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

if "%~1"=="" (
  echo Uso: promote_notas_checkboxes_to_todoist.bat "^<nombre-nota^>" [--sync]
  echo.
  echo Ejemplo:
  echo   promote_notas_checkboxes_to_todoist.bat "N251104-Analisis Estudio 2" --sync
  pause
  exit /b 1
)

echo.
echo === Coworkia: Checkboxes Obsidian -^> Todoist ===
echo Repo: %CD%
echo.

"%VENV_PYTHON%" tools\promote_notas_checkboxes_to_todoist.py %*
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: promote fallo (exit code %ERR%).

pause
exit /b %ERR%
