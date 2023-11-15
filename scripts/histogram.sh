echo ""
echo "Converting to Histogram:"
echo $1
echo ""

convert $1 histogram:- | convert - ${1%.*}-hist.jpg
echo "Histogram saved: ${1%.*}.jpg"