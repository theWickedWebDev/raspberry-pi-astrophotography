#!/bin/bash

if [ $ARGUMENT ]; then
    if [[ $ARGUMENT =~ .+\.[jpg|JPG] ]]
    then
    DIRNAME=$(dirname "$ARGUMENT")
    BASENAME=$(basename "$ARGUMENT")
    NEWFILENAME="$DIRNAME/$BASENAME"

    # echo ""
    # echo "--------------------------------------"
    # echo "DIRNAME: $DIRNAME"
    # echo "BASENAME: $BASENAME"
    # echo "NEWFILENAME: $NEWFILENAME"
    # echo "--------------------------------------"
    # echo ""

    . /home/pi/astrophotography/scripts/histogram.sh $NEWFILENAME
    fi
fi