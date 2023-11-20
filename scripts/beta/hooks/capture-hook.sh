#!/bin/bash

if [ $ARGUMENT ]; then
    echo $ARGUMENT
    if [[ $ARGUMENT =~ .+\.[jpg|JPG] ]]; then
    DIRNAME=$(dirname "$ARGUMENT")
    BASENAME=$(basename "$ARGUMENT")
    NEWFILENAME="$DIRNAME/$BASENAME"

    . /home/pi/astrophotography/scripts/beta/hooks/histogram.sh $NEWFILENAME $DIRNAME 
    # . /home/pi/astrophotography/scripts/beta/hooks/copy-hook.sh $NEWFILENAME $BASENAME &
    fi
fi