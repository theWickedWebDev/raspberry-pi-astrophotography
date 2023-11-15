DIR=$(date +"%m-%d-%Y")
NAME="barnards-loop"

FRAMES=1 # Number of frames to take
FOCAL=30
ISO=800
APERTURE=5

EXPOSURE=90 # Exposure, in seconds 

# FOCAL_REDUCER="fr6.3-"
# BARLOW=""

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
# for COUNT in `seq 1 $FRAMES`
#     do
#         echo ""
#         echo "${COUNT}/${FRAMES}"
#         echo ""


#             # --hook-script=hist-hook.sh \

#         gphoto2 \
#             --set-config imageformat=6 \
#             --set-config-index picturestyle=6 \
#             --set-config shutterspeed=bulb \
#             --set-config iso=$ISO \
#             --set-config autoexposuremode=3 \
#             --filename "/home/pi/astrophotography/captures/$DIR/$NAME/ISO$ISO-${APERTURE}-bulb-${EXPOSURE}s-${FOCAL}-mm-%m-%d-%y_%H:%M:%S__${COUNT}.%C" \
#             --set-config eosremoterelease=5 \
#             --wait-event=${EXPOSURE}s \
#             --set-config eosremoterelease=11 \
#             --wait-event-and-download=6s
#     done

# ---------------
# DARKS
# ---------------

# FRAMES=70 # Number of frames to take

# for COUNT in `seq 1 $FRAMES`
#     do
#         gphoto2 \
#             --set-config-index imageformat=7 \
#             --set-config-index picturestyle=1 \
#             --set-config autoexposuremode=3 \
#             --set-config shutterspeed=bulb \
#             --set-config-value aperture=$APERTURE \
#             --set-config iso=$ISO \
#             --filename "/home/pi/astrophotography/captures/$DIR/$NAME/darks-ISO$ISO-${APERTURE}-bulb-${EXPOSURE}s-${FOCAL}-mm-%m-%d-%y_%H:%M:%S__${COUNT}.%C" \
#             --set-config eosremoterelease=5 \
#             --wait-event=${EXPOSURE}s \
#             --set-config eosremoterelease=11 \
#             --wait-event-and-download=6s
#     done

# ---------------
# BIASES
# ---------------
# gphoto2 \
#     --set-config imageformat=7 \
#     --set-config-index picturestyle=1 \
#     --set-config shutterspeed="1/2000" \
#     --set-config autoexposuremode=3 \
#     --set-config iso=$ISO \
#     --interval 5 \
#     --frames ${FRAMES} \
#     --filename "/home/pi/astrophotography/captures/$DIR/$NAME/biases-ISO$ISO-${APERTURE}-bulb-${EXPOSURE}s-${FOCAL}-mm-%m-%d-%y_%H:%M:%S.%C" \
#     --capture-image-and-download

# ---------------
# FLATS
# ---------------
# --set-config autoexposuremode=2 \ this is Av (aperture priority)
# --set-config autoexposuremode=3 \ this is Manual

    # --hook-script=hist-hook.sh \
gphoto2 \
    --set-config imageformat=7 \
    --set-config-index picturestyle=1 \
    --set-config autoexposuremode=2 \
    --set-config aperture=36 \
    --set-config iso=$ISO \
    --set-config shutterspeed="1/4000" \
    --interval 5 \
    --frames ${FRAMES} \
    --filename "/home/pi/astrophotography/captures/$DIR/$NAME/flats-ISO$ISO-${APERTURE}-bulb-${EXPOSURE}s-${FOCAL}-mm-%m-%d-%y_%H:%M:%S.%C" \
    --capture-image-and-download

# Choice: 10 18
# Choice: 11 20
# Choice: 12 22
# Choice: 13 25
# Choice: 14 29
# Choice: 15 32
# Choice: 16 36

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
# Choice: 47 1/1250
# Choice: 48 1/1600
# Choice: 49 1/2000
# Choice: 50 1/2500
# Choice: 51 1/3200
# Choice: 52 1/4000