#!/usr/bin/python3
from time import sleep
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput


# Receive the stream:
# gst-launch-1.0 -v udpsrc port=8080 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720),
                                                         "format": "YUV420"}))
picam2.start_recording(H264Encoder(), output=FfmpegOutput("-f rtp udp://192.168.0.61:8080"))
count = 0
while True:
    print(f'hello [{count}]')
    count += 1
    sleep(2)
