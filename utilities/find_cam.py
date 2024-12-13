import cv2
import glob
import time
import os
available_cameras = []

# Picamera2.global_camera_info()
# image not displayed: wayland issues: QT_QPA_PLATFORM=xcb

for camera in glob.glob("/dev/video?"):
    c = cv2.VideoCapture(camera)
    print(f"camera {camera}: {c.isOpened()}")
    if c.isOpened():
        available_cameras.append(camera)

    for cam in available_cameras:
        cap = cv2.VideoCapture(cam)
        if not cap.isOpened():
            print(f"camera {cam} is not opened")
            continue
        ret, img = cap.read() 
        cv2.imshow('img', img) 
        cv2.waitKey(0)
        cap.release()



