#!/bin/bash
cd /ZipZap
i=`./showIpAddress.sh`
echo "IP address is $i"
echo "Updating DNS"
cat << _EOF_UNBOUND_ > /etc/unbound/unbound.conf
server:
        verbosity: 1
        interface: 0.0.0.0
        port: 53
        do-ip4: yes
        do-udp: yes
        do-tcp: yes
        access-control: 0.0.0.0/0 allow
        local-data: "ios.magica-us.com A $i"
        local-data: "android.magica-us.com A $i"
        local-data: "magica-us.com A $i"
        local-data: "app.adjust.com A $i"

python:
remote-control:
        control-enable: yes
        control-interface: 127.0.0.1
        control-port: 8953
        control-use-cert: "no"

forward-zone:
   name: "."
   forward-addr: 8.8.4.4
   forward-addr: 8.8.8.8
_EOF_UNBOUND_
systemctl restart unbound
echo "starting gevent server"
python3 gevent_server.py > /tmp/log 2>&1
