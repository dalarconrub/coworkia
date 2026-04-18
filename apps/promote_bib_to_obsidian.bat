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
  echo Uso: promote_bib_to_obsidian.bat "^<citekey^>" [--contexto C137-ART] [--force] [--sync]
  echo.
  echo Ejemplos:
  echo   promote_bib_to_obsidian.bat einstein2005 --sync
  echo   promote_bib_to_obsidian.bat garcia2023 --contexto C138-COM --sync
  pause
  exit /b 1
)

echo.
echo === Coworkia: Promote BIB -^> ficha Obsidian ===
echo Repo: %CD%
echo.

"%VENV_PYTHON%" tools\promote_bib_to_obsidian.py %*
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: promote fallo (exit code %ERR%).

pause
exit /b %ERR%
