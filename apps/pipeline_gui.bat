@echo off
setlocal
pushd "%~dp0\.."
python apps\pipeline_gui.py %*
set EXIT=%ERRORLEVEL%
popd
exit /b %EXIT%
