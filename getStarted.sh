#!/bin/sh

echo "Hi. This is somewhat an automatic script made by gvaldebenit"
echo "and ported to *nix by veritas to help people" 
echo "use kavezo's ZipZap server. I think virtual environment is the hardest"
echo "stuff, so this script makes all the hard stuff. Just press Enter when"
echo "prompted. Enjoy."

echo ''
echo ''
echo ''

echo "Press Enter to Begin"
read $_

python3 -m venv ./env
source ./env/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r ./requirements.txt

echo "Virtual environment is installed, and configured."
echo "Now is time to follow the instructions to either get your account data"
echo "or just run the server."
echo "anyway, the next steps are to run startServer.sh, and configure the proxy on your"
echo "Magia Record device."

echo ''
echo ''
echo ''

echo "Press Enter to Finish"
read $_
