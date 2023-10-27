DIR=$(date +"%m-%d-%Y")
NAME="jupiter"

FRAMES=1 # Number of frames to take
FOCAL=300
ISO=3200
APERTURE=18

# Choice: 0 5.6
# Choice: 1 6.3
# Choice: 2 7.1
# Choice: 3 8
# Choice: 4 9
# Choice: 5 10
# Choice: 6 11
# Choice: 7 13
# Choice: 8 14
# Choice: 9 16
# Choice: 10 18
# Choice: 11 20
# Choice: 12 22
# Choice: 13 25
# Choice: 14 29
# Choice: 15 32
# Choice: 16 36

# ---------------
# LIGHTS
# ---------------
for COUNT in `seq 1 $FRAMES`
    do
        gphoto2 \
            --set-config imageformat=6 \
            --set-config-index picturestyle=1 \
            --set-config shutterspeed="1/200" \
            --set-config-value aperture=$APERTURE \
            --set-config iso=$ISO \
            --interval 1 \
            --frames 30 \
            --filename "/home/pi/captures/$DIR/$NAME/ISO$ISO-f$APERTURE-${EXPOSURE}s-${FOCAL}mm-%m-%d_%H:%M:%S.%C" \
            --capture-image-and-download
    done

# Choice: 17 0.8
# Choice: 18 0.6
# Choice: 19 0.5
# Choice: 20 0.4
# Choice: 21 0.3
# Choice: 22 1/4
# Choice: 23 1/5
# Choice: 24 1/6
# Choice: 25 1/8
# Choice: 26 1/10
# Choice: 27 1/13
# Choice: 28 1/15
# Choice: 29 1/20
# Choice: 30 1/25
# Choice: 31 1/30
# Choice: 32 1/40
# Choice: 33 1/50
# Choice: 34 1/60
# Choice: 35 1/80
# Choice: 36 1/100
# Choice: 37 1/125
# Choice: 38 1/160
# Choice: 39 1/200
# Choice: 40 1/250
# Choice: 41 1/320
# Choice: 42 1/400
# Choice: 43 1/500
# Choice: 44 1/640
# Choice: 45 1/800
# Choice: 46 1/1000