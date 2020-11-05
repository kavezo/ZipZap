rem nginx needs to be restarted before it'll accept the new cert generated
START windows\nginx_windows\stop-nginx.bat > NUL 2>&1
START /WAIT windows\generate_cert.exe
copy /y windows\nginx_windows\nginx\conf\cert\ca.crt ca.crt