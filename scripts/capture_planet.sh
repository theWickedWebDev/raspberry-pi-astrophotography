DATE=$(date +"%m-%d-%Y")
NAME="venus"

FRAMES=1 # Number of frames to take
FOCAL=55
ISO=3200
APERTURE=5.6

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

gphoto2 \
    --set-config-index imageformat=7 \
    --set-config-index picturestyle=1 \
    --set-config shutterspeed="1/4000" \
    --set-config autoexposuremode=3 \
    --set-config aperture=20 \
    --set-config iso=1600

# --hook-script=/home/pi/astrophotography/scripts/beta/hooks/capture-hook.sh \

gphoto2 \
    --filename "/home/pi/astrophotography/captures/$NAME/$DATE/flat%m-%d-%y_%H:%M:%S__ISO${ISO}__f${APERTURE}s__${FOCAL}mm.%C" \
    --capture-image-and-download

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
# Choice: 17 40
# Choice: 18 45

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
# Choice: 47 1/1250
# Choice: 48 1/1600
# Choice: 49 1/2000
# Choice: 50 1/2500
# Choice: 51 1/3200
# Choice: 52 1/4000






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
# Choice: 17 40
# Choice: 18 45