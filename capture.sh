DIR=$(date +"%m-%d-%Y")
NAME="orion"

FRAMES=100 # Number of frames to take
FOCAL=18
ISO=1600
APERTURE=5.6

EXPOSURE=30 # Exposure, in seconds 

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
            --set-config shutterspeed=bulb \
            --set-config-value aperture=$APERTURE \
            --set-config iso=$ISO \
            --filename "/home/pi/captures/$DIR/$NAME/ISO$ISO-f$APERTURE-${EXPOSURE}s-${FOCAL}mm-%m-%d_%H:%M:%S.%C" \
            --set-config eosremoterelease=5 \
            --wait-event=${EXPOSURE}s \
            --set-config eosremoterelease=11 \
            --wait-event-and-download=6s
    done

# ---------------
# BIASES
# ---------------

# FRAMES=30 # Number of frames to take

# for COUNT in `seq 1 $FRAMES`
#     do
#         gphoto2 \
#             --set-config-value imageformat=6 \
#             --set-config-index picturestyle=1 \
#             --set-config shutterspeed=bulb \
#             --set-config-value aperture=$APERTURE \
#             --set-config iso=$ISO \
#             --filename "/home/pi/captures/$DIR/$NAME-bias/ISO$ISO-f$APERTURE-${EXPOSURE}s-${FOCAL}mm-%m-%d_%H:%M:%S.%C" \
#             --set-config eosremoterelease=5 \
#             --wait-event=${EXPOSURE}s \
#             --set-config eosremoterelease=11 \
#             --wait-event-and-download=6s
#     done

# ---------------
# DARKS
# ---------------
# gphoto2 \
#     --set-config imageformat=7 \
#     --set-config-index picturestyle=1 \
#     --set-config shutterspeed="1/4000" \
#     --set-config-value aperture=$APERTURE \
#     --set-config iso=$ISO \
#     --interval 1 \
#     --frames 50 \
#     --filename "/home/pi/captures/$DIR/$NAME-darks/ISO$ISO-f$APERTURE-${EXPOSURE}s-${FOCAL}mm-%m-%d_%H:%M:%S.%C" \
#     --capture-image-and-download