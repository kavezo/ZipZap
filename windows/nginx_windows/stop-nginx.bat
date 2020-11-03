@echo off
pushd %~dp0\nginx
nginx -s stop
rem Give it some time for graceful shutdown
ping localhost -n 2 > NUL
taskkill /f /im nginx.exe
del logs\nginx.pid
popd