@echo off
setlocal
pushd "%~dp0\.."
python tools\reset_obsidian.py %*
set EXIT=%ERRORLEVEL%
popd
exit /b %EXIT%
