#!/bin/bash
set -e
set -o pipefail
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 update_archive private_key"
  exit 1
fi
openssl=/usr/bin/openssl
$openssl dgst -sha1 -binary < "Web Assets/Binaries/Wallpiper-$1.zip" | $openssl dgst -dss1 -sign "/Users/tassilo/Google Drive/Dev/Wallpiper/dsa_priv.pem" | $openssl enc -base64
