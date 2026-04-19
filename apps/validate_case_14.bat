@echo off
setlocal
pushd "%~dp0\.."
python tools\validate_case_14.py %*
set EXIT=%ERRORLEVEL%
popd
exit /b %EXIT%
