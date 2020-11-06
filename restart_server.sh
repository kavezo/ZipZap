#!/bin/bash
PID=$(ps ax | grep gevent_server | grep -v grep | awk '{ print $1 }')
echo $PID
kill $PID
