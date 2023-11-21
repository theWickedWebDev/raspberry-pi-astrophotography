#!/bin/bash

if [ $ARGUMENT ]; then
    if [[ $ARGUMENT =~ .+\.[jpg|JPG] ]]; then
        DIRNAME=$(dirname "$ARGUMENT")
        BASENAME=$(basename "$ARGUMENT")
        NEWFILENAME="$DIRNAME/$BASENAME"

        REMOTE_CAPTURE_DIRECTORY="/home/telescope/captures"
        REMOTE_FILENAME="$REMOTE_CAPTURE_DIRECTORY/$BASENAME"

        # Move Image
        scp $NEWFILENAME sg1:/home/telescope/captures/

        # ssh sg1 "python3 /home/telescope/solve-calibrate-goto.py --image $REMOTE_FILENAME --expectedRA 6h30m26.89s --expectedDEC 4d44m4.2s"
        ssh sg1 ". /home/telescope/histogram.sh $REMOTE_FILENAME $REMOTE_CAPTURE_DIRECTORY" 
        ssh sg1 ". /home/telescope/preview-with-data.sh $REMOTE_FILENAME $BASENAME" 
        rm $NEWFILENAME
        # . /home/pi/astrophotography/scripts/beta/hooks/histogram.sh $NEWFILENAME $DIRNAME 
        # . /home/pi/astrophotography/scripts/beta/hooks/copy-hook.sh $NEWFILENAME $BASENAME &
    fi
fi
