from datetime import datetime
import imagezmq
import cv2


# initialize the ImageHub object
imageHub = imagezmq.ImageHub()

# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()


cv2.namedWindow("Stream")

# start looping over all the frames
while True:
    # receive RPi name and frame from the RPi and acknowledge
    # the receipt
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    # if a device is not in the last active dictionary then it means
    # that its a newly connected device
    if rpiName not in lastActive.keys():
        print("[INFO] receiving data from {}...".format(rpiName))
    # record the last active time for the device from which we just
    # received a frame
    lastActive[rpiName] = datetime.now()
    #print("{}:{}".format(rpiName,datetime.now()))


    cv2.imshow("Stream", frame)

    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF
