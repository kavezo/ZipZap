@echo off
CALL windows\nginx_windows\stop-nginx.bat > NUL 2>&1
START /B windows\nginx_windows\start-nginx.bat
windows\gevent_server\gevent_server.exe