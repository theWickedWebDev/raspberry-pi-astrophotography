#!/bin/bash

echo ""
echo "Converting to Histogram:" $1
echo ""
convert $1 histogram:- | convert - ${1%.*}-hist.jpg
echo "Histogram saved: ${1%.*}.jpg"

echo $(date) >> $2/histogram.log
echo $1 >> $2/histogram.log
# echo ${1%.*}.jpg >> $2/histogram.log
convert $1  -colorspace gray -format "%[fx:100*mean]" info: >> $2/histogram.log
echo "" >> $2/histogram.log
