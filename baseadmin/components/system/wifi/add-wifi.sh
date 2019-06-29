#!/bin/bash

# wrapper script to allow for easy adding of wifi credentials

# go to repository root
cd "$(dirname "$0")"/..

SSID=$1
PSK=$2
ID=$3
WPA=/etc/wpa_supplicant/wpa_supplicant.conf

printf "\n\n" | sudo tee -a ${WPA}

wpa_passphrase "${SSID}" "${PSK}" | grep -v "#psk" | sed "\$i\        id_str=\"${ID}\"" | sudo tee -a ${WPA} > /dev/null
