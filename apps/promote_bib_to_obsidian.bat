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
  echo    o: promote_bib_to_obsidian.bat --all-pending [--dry-run] [--limit N] [--query TEXTO] [--year AAAA] [--author AUTOR] [--journal REVISTA] [--estado ESTADO] [--contexto C137-ART] [--sync]
  echo.
  echo Ejemplos:
  echo   promote_bib_to_obsidian.bat einstein2005 --sync
  echo   promote_bib_to_obsidian.bat garcia2023 --contexto C138-COM --sync
  echo   promote_bib_to_obsidian.bat --all-pending --dry-run --limit 10
  echo   promote_bib_to_obsidian.bat --all-pending --dry-run --query eating --limit 10
  echo   promote_bib_to_obsidian.bat --all-pending --dry-run --author Candido --limit 10
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
