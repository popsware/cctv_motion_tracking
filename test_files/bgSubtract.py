import numpy as np
import cv2

ip_address = "192.168.1.20"
username = "admin"
password = "ayman1351359"
channel = "1302"
streamUrl = 'rtsp://' + username + ':' + password + '@' + \
    ip_address + ':554/Streaming/channels/' + channel
cap = cv2.VideoCapture(streamUrl)
fgbg = cv2.createBackgroundSubtractorMOG2()

while(1):
    ret, frame = cap.read()

    fgmask = fgbg.apply(frame)

    cv2.imshow('fgmask', frame)
    cv2.imshow('frame', fgmask)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break


cap.release()
cv2.destroyAllWindows()
