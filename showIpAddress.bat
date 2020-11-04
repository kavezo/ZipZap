@echo off
echo IP Address List
echo.
netsh interface ip show address | findstr "IP Address"
echo. 
echo.
echo Now you should configure a proxy with address like
echo the first one showed above (Usually is the first. 
echo looks like 192.168.1.xxx)
echo and port 8080 on your Magia Record device
echo.
echo.

pause