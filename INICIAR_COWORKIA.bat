@echo off
setlocal

cd /d "%~dp0"

rem Hint: si el usuario usa 1Password CLI, recomendamos el launcher dedicado
rem para inyectar env vars sin depender de `.env`.
if exist "config\env.1password" (
    echo.
    echo [INFO] Detectado config\env.1password.
    echo        Si usas 1Password CLI, arranca con: INICIAR_COWORKIA_1PASSWORD.bat
    echo.
)

rem Apertura de sesion multiagente (chat del dia + briefing + memory_check).
rem Si falla no bloquea el arranque del GUI, solo avisa.
call apps\abrir_sesion.bat
if errorlevel 1 (
    echo.
    echo [WARN] Apertura de sesion incompleta. El GUI se abrira igualmente.
    echo        Ejecuta apps\abrir_sesion.bat manualmente para ver el detalle.
    echo.
)

call apps\project_hub_gui.bat

endlocal
