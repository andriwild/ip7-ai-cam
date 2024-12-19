import cv2
import glob
import time
import os
available_cameras = []

# find cameras
# Picamera2.global_camera_info()
# v4l2-ctl --list-devices

# image not displayed: wayland issues: QT_QPA_PLATFORM=xcb

for camera in glob.glob("/dev/video?"):
    c = cv2.VideoCapture(camera)
    time.sleep(1)
    print(f"camera {camera}: {c.isOpened()}")
    if c.isOpened():
        available_cameras.append(camera)

    for cam in available_cameras:
        cap = cv2.VideoCapture(cam)
        time.sleep(1)
        if not cap.isOpened():
            print(f"camera {cam} is not opened")
            continue
        ret, img = cap.read() 
        cap.release()



