@echo off
pushd %~dp0\nginx

if exist logs\nginx.pid goto :running
start nginx
goto :exit

:running
echo Looks like nginx is already running! You can close this window.
pause > NUL

:exit
popd