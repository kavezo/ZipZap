START /WAIT pyinstaller gevent_server.py --noconfirm
xcopy /s /h /y dist\gevent_server windows\gevent_server
START /WAIT pyinstaller generate_cert.py --noconfirm --onefile
copy /y dist\generate_cert.exe windows\generate_cert.exe