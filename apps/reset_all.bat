@echo off
setlocal
pushd "%~dp0\.."
python tools\reset_all.py %*
set EXIT=%ERRORLEVEL%
popd
exit /b %EXIT%
