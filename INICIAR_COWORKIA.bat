@echo off
setlocal

cd /d "%~dp0"

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
