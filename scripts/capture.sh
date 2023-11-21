#!/bin/bash

# ./capture.sh -c /home/pi/astrophotography/scripts/beta/config.ini

set -a   
PWD=`pwd`
while getopts ":c:" opt; do
  case $opt in
    c) CONFIG="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac

  case $OPTARG in
    -*) echo "Option $opt needs a valid argument"
    exit 1
    ;;
  esac
done

set -e
source $CONFIG
set +a

for COUNT in `seq 1 $FRAMES`
  do
    echo ""
    echo "${COUNT}/${FRAMES}"
    echo ""

    set -a               
    source config.ini
    set +a

    FILENAME="${CAPTURE_DIRECTORY}/$NAME/$DATE/%m-%d-%y_%H:%M:%S__ISO${ISO}__f${APERTURE}__${EXPOSURE}s__${FOCAL}mm__${COUNT}.%C"

    gphoto2 \
        --set-config imageformat=$IMAGEFORMAT \
        --set-config picturestyle=$PICTURESTYLE \
        --set-config autoexposuremode="$AUTOEXPOSUREMODE" \
        --set-config aperture=$APERTURE \
        --set-config shutterspeed=bulb \
        --set-config iso=$ISO \
        --filename $FILENAME \
        --set-config eosremoterelease=5 \
        --wait-event=${EXPOSURE}s \
        --set-config eosremoterelease=11 \
        --wait-event-and-download=7s \
        --hook-script=./hooks/capture-hook.sh
  done
