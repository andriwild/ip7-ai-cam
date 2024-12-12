from imutils.video import VideoStream

import threading
import cv2
import time

vs = VideoStream(src=0).start()
time.sleep(2.0)
frame = vs.read()
cv2.imshow("frame", frame)
cv2.waitKey(0)

