#!/bin/bash

# updates orientation settings in Xconfig and sets new splash screen
# (requires sudo rights)

ORIENTATION=$1

# go to script location
cd "$(dirname "$0")"

XCONF=/usr/share/X11/xorg.conf.d/99-fbturbo.conf
SPLASH=/usr/share/plymouth/themes/pix/splash.png

case "${ORIENTATION}" in
"CW")
  sudo cp 99-fbturbo-cw.conf  ${XCONF}
  if [ -f ~/splash-cw.png ]; then
    sudo cp ~/splash-cw.png   ${SPLASH}
  fi
  ;;
"CCW")
  sudo cp 99-fbturbo-ccw.conf ${XCONF}
  if [ -f ~/splash-ccw.png ]; then
    sudo cp ~/splash-ccw.png   ${SPLASH}
  fi
  ;;
"UD")
  sudo cp 99-fbturbo-ud.conf  ${XCONF}
  if [ -f ~/splash-ud.png ]; then
    sudo cp ~/splash-ud.png   ${SPLASH}
  fi
  ;;
*)
  sudo cp 99-fbturbo.conf     ${XCONF}
  if [ -f ~/splash.png ]; then
    sudo cp ~/splash.png   ${SPLASH}
  fi
  ;;
esac
