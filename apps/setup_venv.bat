@echo off
setlocal

cd /d "%~dp0\.."

set "BOOTSTRAP_PY=python"
set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

where py >nul 2>nul
if not errorlevel 1 set "BOOTSTRAP_PY=py -3"

if not exist "%VENV_PY%" (
    echo Creando entorno virtual en %VENV_DIR%...
    %BOOTSTRAP_PY% -m venv %VENV_DIR%
    if errorlevel 1 (
        echo.
        echo No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo El entorno virtual ya existe en %VENV_DIR%.
)

echo.
echo Actualizando pip...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo No se pudo actualizar pip.
    pause
    exit /b 1
)

echo.
echo Instalando dependencias desde requirements.txt...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo Entorno virtual preparado correctamente.
echo Python activo: %VENV_PY%
pause

endlocal
