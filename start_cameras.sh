#!/bin/bash
cd ../raspivid_mjpeg_server/

#!/bin/bash

v4l2-ctl -d 4 -c exposure_auto=1,exposure_absolute=300,brightness=0,gain=100 &

v4l2-ctl -d 4 -v width=1024,height=768,pixelformat='MJPG' --stream-mmap --stream-to - | raspivid_mjpeg_server -p 8554 &

v4l2-ctl -d 0 -v width=1024,height=768,pixelformat='MJPG' --stream-mmap --stream-to - | raspivid_mjpeg_server -p 8555 &

wait