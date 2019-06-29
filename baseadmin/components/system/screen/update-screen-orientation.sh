#!/bin/bash

# updates orientation settings in Xconfig and sets new splash screen
# (requires sudo rights)

ORIENTATION=$1

# go to repository root
cd "$(dirname "$0")"/..

XCONF=/usr/share/X11/xorg.conf.d/99-fbturbo.conf
SPLASH=/usr/share/plymouth/themes/pix/splash.png
BOOTSTRAP=install/files

case "${ORIENTATION}" in
"CW")
  sudo cp ${BOOTSTRAP}/99-fbturbo-cw.conf  ${XCONF}
  sudo cp ${BOOTSTRAP}/splash-cw.png       ${SPLASH}
  ;;
"CCW")
  sudo cp ${BOOTSTRAP}/99-fbturbo-ccw.conf ${XCONF}
  sudo cp ${BOOTSTRAP}/splash-ccw.png      ${SPLASH}
  ;;
"UD")
  sudo cp ${BOOTSTRAP}/99-fbturbo-ud.conf  ${XCONF}
  sudo cp ${BOOTSTRAP}/splash-ud.png       ${SPLASH}
  ;;
*)
  sudo cp ${BOOTSTRAP}/99-fbturbo.conf     ${XCONF}
  sudo cp ${BOOTSTRAP}/splash.png          ${SPLASH}
  ;;
esac
