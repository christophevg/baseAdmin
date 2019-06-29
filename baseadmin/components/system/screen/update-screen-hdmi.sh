#!/bin/bash

# updates HDMI settings in /boot/config.txt (requires sudo rights)

GROUP=$1
MODE=$1

CONFIG=/boot/config.txt
TMPCONFIG=/tmp/config.txt

if [ $? -ne 0 ]; then
  cat ${CONFIG} | grep -v "^hdmi_group" | grep -v "^hdmi_mode" > ${TMPCONFIG}
  printf "\n\n"                  >> ${TMPCONFIG}
  printf "hdmi_group=${GROUP}\n" >> ${TMPCONFIG} 
  printf "hdmi_mode=${MODE}\n"   >> ${TMPCONFIG} 
  sudo cp ${TMPCONFIG} ${CONFIG}
  rm ${TMPCONFIG}
fi
