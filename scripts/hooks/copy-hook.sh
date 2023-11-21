#!/bin/bash
NEWFILENAME=$1 
BASENAME=$2

DEST=/home/pi/astrophotography/image-server/public/latest.jpg

cp $NEWFILENAME $DEST
echo "Converting $NEWFILENAME TO $DEST"

LUMINANCE=$(convert $NEWFILENAME -colorspace gray -format "%[fx:100*mean]" info:)

convert $DEST -gravity South \
    -stroke '#000C' -pointsize 80 -strokewidth 2 -annotate 0 $BASENAME \
    -stroke none -pointsize 80 -fill white -annotate 0 $BASENAME \
    $DEST

convert $DEST -gravity North \
    -stroke '#000C' -pointsize 80 -strokewidth 2 -annotate 0 $LUMINANCE \
    -stroke none -pointsize 80 -fill white -annotate 0 $LUMINANCE \
    $DEST
