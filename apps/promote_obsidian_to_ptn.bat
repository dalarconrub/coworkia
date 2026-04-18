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
  echo Uso: promote_obsidian_to_ptn.bat "^<nombre-nota^>" [--proyecto "^<ref^>"] [--tarea "^<ref^>"] [--sync]
  echo.
  echo Ejemplos:
  echo   promote_obsidian_to_ptn.bat "N260316-Reunion" --proyecto "Tesis Fran" --sync
  echo   promote_obsidian_to_ptn.bat "N260316-Reunion" --tarea "T12601.03" --sync
  echo   promote_obsidian_to_ptn.bat "N260316-Reunion" --proyecto "Sofia" --tarea "^<uuid^>" --sync
  pause
  exit /b 1
)

echo.
echo === Coworkia: Promote Obsidian -^> PTN-Notas ===
echo Repo: %CD%
echo.

"%VENV_PYTHON%" tools\promote_obsidian_to_ptn.py %*
set "ERR=%errorlevel%"

echo.
if not "%ERR%"=="0" echo ERROR: promote fallo (exit code %ERR%).

pause
exit /b %ERR%
