from __future__ import print_function
import cv2 as cv, cv2
import argparse
import imutils
import numpy as np

max_value = 255

low_H = 217
high_H = max_value

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


parser = argparse.ArgumentParser(description='Code for Thresholding Operations using inRange tutorial.')
parser.add_argument('--camera', help='Camera divide number.', default=2, type=int)
args = parser.parse_args()
cap = cv.VideoCapture(args.camera)
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
cv.createTrackbar(low_H_name, window_detection_name, low_H, max_value, on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name, window_detection_name, high_H, max_value, on_high_H_thresh_trackbar)

while True:

    ret, image = cap.read()
    if image is None:
        break
    #frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    #frame_HSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    #frame_threshold = cv.inRange(frame_HSV, (34, 82, 140), (143, 141, 255))
    # redimensionamos, cuanto mas pequeña  mas rapido
    # pero perdemos definicion
    image = imutils.resize(image, height=600)
    # flip para que sea espejo
    image = cv.flip(image, 1)
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
    # Nos quedamos con los 5 mayores
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)[:1]

    # loop over our contours
    for c in cnts:
        '''
        currentContour = component[0]
        currentHierarchy = component[1]
        x, y, w, h = cv2.boundingRect(currentContour)
        if currentHierarchy[2] < 0:
            # these are the innermost child components
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
        elif currentHierarchy[3] < 0:
            # these are the outermost parent components
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)
        '''

        # approximate the contour
        peri = cv2.arcLength(c, True)
        #3 precision 1.5%
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)
        # valores de los contornos
        M = cv2.moments(c)
        # centro de los contornos
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])


        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            # dibujamos los contornos de 4 esquinas VERDE
            cv.drawContours(image, [screenCnt], -1, (0, 200, 0), 2)
            # dibujamos rectangulo que lo contiene no tiene en cuenta la rotacion AMARILLO
            '''
            x, y, w, h = cv.boundingRect(screenCnt)
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)
            '''
            # dibujamos rect teniendo en cuenta la rotacion ROJO
            '''
            rect = cv.minAreaRect(screenCnt)
            box = cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(image, [box], 0, (0, 0, 255), 2)
            '''
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
            #break
        # dibujamos el resto de los contornos
        # cv.drawContours(image, [c], -1, (200, 0, 0), 1)

    cv.imshow(window_capture_name, image)
    cv.imshow(window_detection_name, edged)
    cv.moveWindow(window_detection_name, 1200, 620)
    cv.moveWindow(window_capture_name, 1200, 0)

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        break
