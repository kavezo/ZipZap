@echo off
pushd %~dp0\nginx
nginx -s stop
taskkill /f /im nginx.exe
del logs\nginx.pid
popd