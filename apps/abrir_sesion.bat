@echo off
setlocal

rem Apertura de sesion multiagente:
rem   1) Resuelve/crea el chat del dia e imprime briefing (memoria + devlog reciente).
rem   2) Valida la capa memory/ (ficheros presentes, enlaces, TREE al dia).
rem
rem No ejecuta sync-chat-memory: ese comando pertenece al cierre
rem (ver apps\cerrar_sesion.bat). Ver devlog/DEVLOG.md para la racional.

cd /d "%~dp0\.."

set "VENV_PY=.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    set "PY=%VENV_PY%"
) else (
    set "PY=python"
)

echo === Apertura de sesion ===
echo.
echo [1/2] init_chat: resolviendo chat del dia y briefing...
"%PY%" tools\init_chat.py
if errorlevel 1 (
    echo.
    echo [ERROR] init_chat.py fallo. Revisa chats/ y multiagents/chat_template.md.
    exit /b 1
)

echo.
echo [2/2] memory_check: validando memory/...
"%PY%" tools\memory_check.py
if errorlevel 1 (
    echo.
    echo [WARN] memory_check detecto desalineacion. Revisa memory/ antes de trabajar.
    exit /b 2
)

echo.
echo Apertura OK. Chat del dia y memory/ listos.
endlocal
