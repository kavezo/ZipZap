@echo.
@echo Hi. This is somewhat an automatic script made by gvaldebenit to help people 
@echo use kavezo's ZipZap server. I think virtual environment is the hardest
@echo stuff, so this script makes all the hard stuff. Just press Start when 
@echo prompted. Enjoy.
@echo.
@echo.

pause

python -m venv ./env
CALL .\env\Scripts\Activate
python -m pip install --upgrade pip
python -m pip install -r ./requirements.txt

@echo.
@echo.
@echo Virtual environment is installed, and configured.
@echo Now is time to follow the instructions to either get your account data
@echo or just run the server.
@echo anyway, next steep is to run startServer.bat, and configure the proxy on your
@echo Magia Record device.
@echo.
@echo.

pause

@echo. 
@echo Now the preparations are done. You should configure the proxy on the 
@echo Magia Record Device
@echo.

pause

CALL .\showIpAddress.bat
