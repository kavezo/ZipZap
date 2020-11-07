#!/bin/bash

# get path to where this script (and the other ZipZap files) are located
SRC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# must be run as root
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

# install dependencies
echo "*** BEGINNING ZIPZAP VM SETUP ***"
echo ""
echo "# Installing packages..."
apt update -y -qq
apt install -y build-essential net-tools nginx python3 python3-dev python3-pip unbound -qq

# disable resolved
echo ""
echo "# Disabling Ubuntu DNS manager..."
systemctl disable systemd-resolved.service
systemctl stop systemd-resolved
rm -f /etc/resolv.conf
cat << _RESOLV_ > /etc/resolv.conf
nameserver 8.8.8.8
_RESOLV_

# set up nginx
echo ""
echo "# Setting up nginx web server in proxy mode..."
systemctl stop nginx.service
mv /etc/nginx /etc/nginx.bak
cp -r $SRC/windows/nginx_windows/nginx/conf /etc/nginx
cp -r $SRC/windows/nginx_windows/nginx/html /etc/nginx/html
cat << _EOF_HTML_ > /etc/nginx/html/index.html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to MadokaPriv!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to MadokaPriv!</h1>
<p>To use MadokaPriv to play with your Magia Record EN private server, you need to install the CA certificate and trust it</p>

<p><a href="ca.crt">Download CA Cert</a>.<br/></p>
<h2>Guides to enabling a CA Root Certificate</h2>
<p><a href="https://support.apple.com/en-us/HT204477">iOS/iPadOS</a></p>
<p><a href="https://www.lastbreach.com/blog/importing-private-ca-certificates-in-android">Android</a></p>
</body>
</html>
_EOF_HTML_
sed -e 's/^.*root.*html/root \/etc\/nginx\/html/' -i.bak /etc/nginx/nginx.conf
sed -e 's/^error_log.*$/error_log \/var\/log\/nginx\/error.log;/' -i.bak /etc/nginx/nginx.conf
sed -e 's/^.*access_log.*$/access_log \/var\/log\/nginx\/access.log combined;/' -i.bak /etc/nginx/nginx.conf
sed -e 's/^daemon/#daemon/' -i.bak /etc/nginx/nginx.conf
mkdir -p /var/log/nginx

# set up certificate
if [ -d ssl -a -f ssl/ca.crt ]; then
  echo ""
  echo "# Found an already existing SSL certificate. Not making a new one."
  cd ssl
else
  echo ""
  echo "# Generating SSL certificate..."
  cd $SRC && mkdir ssl && cd ssl
  python3 ../generate_cert.py .
fi

# install cert
echo ""
echo "# Installikng SSL certificate and starting up nginx..."
mkdir -p /etc/nginx/cert /etc/nginx/html
cp ca.crt /etc/nginx/html
for FILE in site.crt site.key; do
  cp "$FILE" /etc/nginx/cert/
done
# start nginx
systemctl start nginx.service

# install dependencies etc
echo ""
echo "# Installikng ZipZap python dependencies..."
cd $SRC && pip3 install -r requirements.txt

# enable rc.local
echo ""
echo "# Enabling ZipZap autostart at boot..."
cat << _RCLOCAL_ > /etc/systemd/system/rc-local.service
[Unit]
Description=/etc/rc.local Compatibility
ConditionPathExists=/etc/rc.local

[Service]
Type=forking
ExecStart=/etc/rc.local start
TimeoutSec=0
StandardOutput=tty
RemainAfterExit=yes
SysVStartPriority=99

[Install]
WantedBy=multi-user.target
_RCLOCAL_
cat << _RCLOCAL2_ > /etc/rc.local
#!/bin/bash
cd $SRC && ./startServer.sh &
exit 0
_RCLOCAL2_
chmod +x /etc/rc.local
systemctl enable rc-local

# start it up
echo ""
echo "# Starting ZipZap..."
cd $SRC && ./startServer.sh &

echo ""
echo "*** ALL DONE! ***"
echo ""
sh /etc/rc.local > /tmp/local 2>&1
i=`$SRC/getipaddress.sh`
echo "This VM's public IP is: $i"
echo "Set your device/emulator's DNS to that address."