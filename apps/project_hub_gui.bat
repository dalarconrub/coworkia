@echo off
setlocal

cd /d "%~dp0\.."

set "BOOTSTRAP_PY=python"
set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

where py >nul 2>nul
if not errorlevel 1 set "BOOTSTRAP_PY=py -3"

if not exist "%VENV_PY%" (
    echo No existe el entorno virtual del proyecto en %VENV_DIR%.
    echo.
    set /p CREATE_VENV="Crear entorno virtual e instalar dependencias ahora? [S/N]: "
    if /i "%CREATE_VENV%"=="S" (
        %BOOTSTRAP_PY% -m venv %VENV_DIR%
        if errorlevel 1 (
            echo.
            echo No se pudo crear el entorno virtual.
            pause
            exit /b 1
        )

        "%VENV_PY%" -m pip install --upgrade pip
        "%VENV_PY%" -m pip install -r requirements.txt
        if errorlevel 1 (
            echo.
            echo No se pudieron instalar las dependencias en el entorno virtual.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Creacion del entorno virtual cancelada.
        pause
        exit /b 1
    )
)

"%VENV_PY%" -c "import dotenv" >nul 2>nul
if errorlevel 1 (
    echo Faltan dependencias Python en %VENV_DIR%.
    echo.
    set /p INSTALL_DEPS="Instalar dependencias desde requirements.txt ahora? [S/N]: "
    if /i "%INSTALL_DEPS%"=="S" (
        "%VENV_PY%" -m pip install -r requirements.txt
    ) else (
        echo.
        echo Instalacion cancelada.
        pause
        exit /b 1
    )
)

"%VENV_PY%" apps\project_hub_gui.py

if errorlevel 1 (
    echo.
    echo Error al iniciar Coworkia Project Hub.
    echo Verifica que el entorno virtual %VENV_DIR% y sus dependencias esten correctos.
    pause
)

endlocal
