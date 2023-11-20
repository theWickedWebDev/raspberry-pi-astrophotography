DIR=$(date +"%m-%d-%Y")
NAME="auto-expose"

FRAMES=1 # Number of frames to take
FOCAL=55
ISO=100
APERTURE=36
EXPOSURE=3 # Exposure, in seconds 

gphoto2 \
    --hook-script=hist-hook.sh \
    --set-config imageformat=0 \
    --set-config-index picturestyle=1 \
    --set-config shutterspeed="1/10" \
    --set-config autoexposuremode=3 \
    --set-config iso=$ISO \
    --interval 5 \
    --frames ${FRAMES} \
    --filename "/home/pi/astrophotography/captures/$NAME-biases/$DIR/biases-ISO$ISO-${APERTURE}-bulb-${EXPOSURE}s-${FOCAL}-mm-%m-%d-%y_%H:%M:%S__${COUNT}.%C" \
    --capture-image-and-download