@echo off
pip3 install requests
echo.
echo.
echo.
set /p id="Enter Transfer ID: "
set /p pass="Enter Password: "
set py="python3"
python3 --version 2>NUL
if errorlevel 1 set py="python"
%py% transferUserData.py %id% %pass%
pause > NUL