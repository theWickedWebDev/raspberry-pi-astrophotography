DIR=$(date +"%m-%d-%Y")
NAME="pleiades"

FRAMES=1 # Number of frames to take
EXPOSURE=30 # Exposure, in seconds 
FOCAL=55
#e
ISO=400
APERTURE=5.6
# Choice: 0 3.5
# Choice: 1 4
# Choice: 2 4.5
# Choice: 3 5
# Choice: 4 5.6
# Choice: 5 6.3
# Choice: 6 7.1
# Choice: 7 8
# Choice: 8 9
# image format: 6 | 0

gphoto2 \
    --set-config-index imageformat=6 \
    --set-config-index picturestyle=1 \
    --set-config shutterspeed=bulb \
    --set-config-value aperture=$APERTURE \
    --set-config iso=$ISO

for COUNT in `seq 1 $FRAMES`
    do
        gphoto2 \
            --filename "/home/pi/astropitography/photos/$DIR/$NAME/ISO$ISO-f$APERTURE-${EXPOSURE}s-${FOCAL}mm-%m-%d_%H:%M:%S.%C" \
            --set-config eosremoterelease=5 \
            --wait-event=${EXPOSURE}s \
            --set-config eosremoterelease=11 \
            --wait-event-and-download=6s
    done
