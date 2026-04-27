@echo off
setlocal

cd /d "%~dp0\.."

set "VENV_PY=.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    set "PY=%VENV_PY%"
) else (
    set "PY=python"
)

set "INPUT=%CD%\config\secrets.1p.json"
set "OUTPUT=%CD%\.env"

if not exist "%INPUT%" (
    echo [ERROR] No existe "%INPUT%".
    echo         Crea el archivo copiando: config\secrets.1p.json.example ^> config\secrets.1p.json
    echo         y pega ahi el JSON descargado desde 1Password.
    echo.
    pause
    exit /b 1
)

echo Generando %OUTPUT% desde %INPUT% ...
%PY% tools\generate_env_from_json.py --input "%INPUT%" --output "%OUTPUT%" --force
if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo generar .env.
    pause
    exit /b 1
)

echo.
echo [OK] .env generado.
endlocal

