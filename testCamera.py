import cv2 as cv
import imutils
from imutils.video import FPS
from imutils.video import VideoStream

# cap = cv.VideoCapture(1)
vs = VideoStream(src=1).start()

fps = FPS.start()

while True:

    success, frame = vs.read()
    frame = imutils.resize(frame, width=500)
    cv.imshow('Video', frame)
    fps.update()

cap.release()
