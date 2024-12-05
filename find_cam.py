import cv2
import glob
import time
import os
available_cameras = []

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
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ret, img = cap.read() 
        cv2.imshow('img', img) 
        cv2.waitKey(0)
        cap.release()

