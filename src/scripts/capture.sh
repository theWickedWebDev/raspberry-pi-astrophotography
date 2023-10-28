#!/usr/bin/env bash


# gphoto2 \
#     --set-config-value aperture="16" \
#     --set-config-value iso="800" \
#     --set-config-value shutterspeed="1/1250" \
#     --interval 1 \
#     --frames 100 \
#     --filename "/home/pi/captures/moon/%m-%d_%H:%M:%S.%C" \
#     --capture-image-and-download

EXPOSURE=30
FRAMES=140

for COUNT in `seq 1 $FRAMES`
    do
        gphoto2 \
            --set-config imageformat="7" \
            --set-config-index picturestyle="1" \
            --set-config shutterspeed="bulb" \
            --set-config-value aperture="10" \
            --set-config iso="1600" \
            --filename "/home/pi/captures/polaris-star-trail/%m-%d_%H:%M:%S.%C" \
            --set-config eosremoterelease="5" \
            --wait-event=${EXPOSURE}s \
            --set-config eosremoterelease="11" \
            --wait-event-and-download=6s
    done


gphoto2 \
    --set-config imageformat="7" \
    --set-config-index picturestyle="1" \
    --set-config-value aperture="5" \
    --set-config iso="800" \
    --set-config shutterspeed="bulb" \
    --filename "home/pi/captures/frame-%m-%d_%H:%M:%S.%C" \
    --set-config eosremoterelease="5" \
    --wait-event=5s \
    --set-config eosremoterelease="11" \
    --wait-event-and-download=6s

# Current: 8
# Choice: 0 3.5
# Choice: 1 4
# Choice: 2 4.5
# Choice: 3 5
# Choice: 4 5.6
# Choice: 5 6.3
# Choice: 6 7.1
# Choice: 7 8
# Choice: 8 9
# Choice: 9 10
# Choice: 10 11
# Choice: 11 13
# Choice: 12 14
# Choice: 13 16
# Choice: 14 18
# Choice: 15 20
# Choice: 16 22


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

# jupiter: 1/500 f/11 ISO1600
# jupiter: 1/60 f/5.6 ISO6400 (W/ MOONS)