from __future__ import print_function
import cv2 as cv, cv2
import argparse
import imutils
import numpy as np
from imutils.video import FPS
from pythonosc import udp_client


max_value = 255

low_H = 217
high_H = max_value
cal_x = 0
cal_y = 0

window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
low_H_name = 'Low'
high_H_name = 'High'

def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H - 1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)

def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H + 1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)


# metodos para calibrar coord x e y
def on_cal_x(val):
    global cal_x
    cal_x = val - 800


def on_cal_y(val):
    global cal_y
    cal_y = val - 600

parser = argparse.ArgumentParser(description='Code for Thresholding Operations using inRange tutorial.')
parser.add_argument('--camera', help='Camera divide number.', default=0, type=int)
args = parser.parse_args()
cap = cv.VideoCapture(args.camera)

print("Frame default resolution: (" + str(cap.get(cv.CAP_PROP_FRAME_WIDTH)) + "; " + str(cap.get(cv.CAP_PROP_FRAME_HEIGHT)) + ")")
cap.set(cv.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 600)
print("Frame resolution set to: (" + str(cap.get(cv.CAP_PROP_FRAME_WIDTH)) + "; " + str(cap.get(cv.CAP_PROP_FRAME_HEIGHT)) + ")")

cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
# posicion de las ventanas en el escritorio
cv.moveWindow(window_detection_name, 0, 540)
cv.moveWindow(window_capture_name, 0, 0)

# trackbar para los niveles de canny
#cv.createTrackbar(low_H_name, window_detection_name, low_H, max_value, on_low_H_thresh_trackbar)
#cv.createTrackbar(high_H_name, window_detection_name, high_H, max_value, on_high_H_thresh_trackbar)

# trackbar para calibrar la posicion
# como solo podemos 0 - max_Value
# hacemos el doble del valor y lo empezamos en el medio
# en los metodos on_ restamos el max para obtener -800 a 800 y -600 a 600

cv.createTrackbar("x", window_capture_name, 800, 1600, on_cal_x)
cv.createTrackbar("y", window_capture_name, 600, 1200, on_cal_y)


# Frame por segundos
# cap.set(cv2.CAP_PROP_FPS,24)
fps = FPS().start()
print(fps)

# define osc client
client = udp_client.SimpleUDPClient("192.168.1.130", 8010)

while True:

    grabbed, image = cap.read()
    if not grabbed:
        break
    # frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # frame_HSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    # frame_threshold = cv.inRange(frame_HSV, (34, 82, 140), (143, 141, 255))

    # redimensionamos, cuanto mas pequeña  mas rapido
    # pero perdemos definicion
    #image = imutils.resize(image, height=270, width=480)
    # flip para que sea espejo
    # image = cv.flip(image, 1)
    # trabajamos con grises
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    blur = cv.GaussianBlur(gray, (5, 5), 0)
    bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
    # contornos con Canny
    # limites
    # print(str(low_H) + ':' + str(high_H))
    edged = cv.Canny(bilateral, low_H, high_H)
    # buscamos contornos
    # tenemos que hacer la copia de la imagen porque el metodo la destruye
    # https://docs.opencv.org/master/d9/d8b/tutorial_py_contours_hierarchy.html
    cnts = cv.findContours(edged.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # si queremos trabajar con hierarchy
    # https://stackoverflow.com/questions/11782147/python-opencv-contour-tree-hierarchy
    # fcnts, hierar = cv.findContours(edged.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # hierar = hierar[0]

    cnts = imutils.grab_contours(cnts)
    # Nos quedamos con el mayor
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)[:1]

    # loop over our contours
    for c in cnts:

        # approximate the contour
        peri = cv2.arcLength(c, True)
        # 3 precision 1.5%
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)
        '''
        # valores de los contornos
        M = cv2.moments(c)
        # centro de los contornos
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        '''
        # if our approximated contour has four points, then
        # we can assume that we have found our screens
        if len(approx) == 4:
            screenCnt = approx
            # dibujamos los contornos de 4 esquinas VERDE
            cv.drawContours(image, [screenCnt], -1, (0, 200, 0), 2)
            # dibujamos rectangulo que lo contiene no tiene en cuenta la rotacion AMARILLO

            x, y, w, h = cv.boundingRect(screenCnt)
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)
            '''
            # dibujamos rect teniendo en cuenta la rotacion ROJO
            '''
            rect = cv.minAreaRect(screenCnt)
            box = cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(image, [box], 0, (0, 0, 255), 2)

            # send new position to madmapper
            # mover el quad
            client.send_message("/surfaces/Quad-1/output/handles/0/x", float(screenCnt[1][0][0])+cal_x)
            client.send_message("/surfaces/Quad-1/output/handles/0/y", float(screenCnt[1][0][1])+cal_y)
            client.send_message("/surfaces/Quad-1/output/handles/1/x", float(screenCnt[2][0][0])+cal_x)
            client.send_message("/surfaces/Quad-1/output/handles/1/y", float(screenCnt[2][0][1])+cal_y)
            client.send_message("/surfaces/Quad-1/output/handles/2/x", float(screenCnt[3][0][0])+cal_x)
            client.send_message("/surfaces/Quad-1/output/handles/2/y", float(screenCnt[3][0][1])+cal_y)
            client.send_message("/surfaces/Quad-1/output/handles/3/x", float(screenCnt[0][0][0])+cal_x)
            client.send_message("/surfaces/Quad-1/output/handles/3/y", float(screenCnt[0][0][1])+cal_y)
            # datos
            datos = "{}:{}:{}:{}".format(
                screenCnt[0][0], screenCnt[1][0],
                screenCnt[2][0], screenCnt[3][0])
            # cv2.putText(image, datos, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)
            for i in range(4):
                cv2.putText(image, "{}".format(screenCnt[i][0]),
                            (screenCnt[i][0][0], screenCnt[i][0][1]),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 200, 0), 1)
            # break
        # dibujamos el resto de los contornos
        # cv.drawContours(image, [c], -1, (200, 0, 0), 1)

    # ventana original mas contorno
    cv.imshow(window_capture_name, image)
    # ventana de canny
    cv.imshow(window_detection_name, edged)


    # update the FPS counter
    fps.update()

    key = cv.waitKey(1)
    if key == ord('q') or key == 27:
        break

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
