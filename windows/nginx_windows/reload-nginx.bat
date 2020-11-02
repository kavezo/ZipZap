@echo off
pushd %~dp0\nginx
nginx -s reload
popd