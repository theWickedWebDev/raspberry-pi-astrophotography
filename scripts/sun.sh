DIR=$(date +"%m-%d-%Y")
NAME="sun2"

APERTURE="5.6"
SHUTTERSPEED="100"
ISO=800

gphoto2 \
    --set-config-index imageformat=6 \
    --set-config-index picturestyle=1 \
    --set-config shutterspeed="1/$SHUTTERSPEED" \
    --set-config-value aperture=$APERTURE \
    --set-config iso=$ISO

gphoto2 \
    --filename "/home/pi/astrophotography/captures/$DIR/$NAME/300mm-%m-%d-%y_%H:%M:%S-f${APERTURE}-${SHUTTERSPEED}.%C" \
    --frames 1\
    --interval 2 \
    --capture-image-and-download



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
# Choice: 47 1/1250
# Choice: 48 1/1600
# Choice: 49 1/2000
# Choice: 50 1/2500
# Choice: 51 1/3200
# Choice: 52 1/4000