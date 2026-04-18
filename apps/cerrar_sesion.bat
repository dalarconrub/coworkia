@echo off
setlocal

rem Cierre de sesion multiagente:
rem   1) Regenera memoria derivada desde el chat (artifacts/multiagent/* + memory/SNAPSHOT.md).
rem   2) Revalida la capa memory/.
rem
rem Correr despues de que el chat del dia tenga sus MEMORIA:/CERRADO: finales.
rem No correr al abrir: ver Claude msg #8 en chat 2026-04-18.

cd /d "%~dp0\.."

set "VENV_PY=.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    set "PY=%VENV_PY%"
) else (
    set "PY=python"
)

echo === Cierre de sesion ===
echo.
echo [1/2] sync-chat-memory: regenerando artifacts/multiagent y memory/SNAPSHOT.md...
"%PY%" agents\orchestrator_agent.py sync-chat-memory
if errorlevel 1 (
    echo.
    echo [ERROR] sync-chat-memory fallo. Revisa el chat del dia y reintenta.
    exit /b 1
)

echo.
echo [2/2] memory_check: validando memory/...
"%PY%" tools\memory_check.py
if errorlevel 1 (
    echo.
    echo [WARN] memory_check detecto desalineacion despues del sync.
    exit /b 2
)

echo.
echo Cierre OK. Memoria derivada al dia.
endlocal
