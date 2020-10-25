@echo off
transferUserData\transferUserData.exe
if errorlevel 1 echo Failed to save data
echo You can now close this window
pause>NUL
