@echo off
REM Script alternativo para actualizar GitHub (más simple)
REM Uso: actualizar_github.bat

echo.
echo Actualizando GitHub...
echo.

git add .
git commit -m "Actualización automática - %date% %time%"
git push

if %errorlevel% equ 0 (
    echo.
    echo GitHub actualizado exitosamente!
    echo.
) else (
    echo.
    echo Error al actualizar GitHub
    echo.
)

pause
