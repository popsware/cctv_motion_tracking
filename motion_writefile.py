import datetime
import sys
import matplotlib.pyplot as plt
import cv2
import numpy as np
import imutils
from win10toast import ToastNotifier


ip_address = "192.168.1.20"
username = "admin"
password = "ayman1351359"

if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    targetcam = "nole1"

if targetcam == "nole1":
    ix, iy, ix2, iy2 = 588, 128, 702, 301
    channel = '802'
elif targetcam == "nole2":
    ix, iy, ix2, iy2 = 323, 141, 703, 191
    channel = '902'
elif targetcam == "nole3":
    ix, iy, ix2, iy2 = 228, 307, 301, 385
    channel = '1002'
elif targetcam == "nole4":
    ix, iy, ix2, iy2 = 400, 94, 543, 295
    channel = '1102'
elif targetcam == "nole5":
    ix, iy, ix2, iy2 = 199, 85, 315, 261
    channel = '1102'
elif targetcam == "nole6":
    ix, iy, ix2, iy2 = 397, 124, 506, 322
    channel = '1202'
elif targetcam == "nole7":
    ix, iy, ix2, iy2 = 547, 141, 632, 327
    channel = '1302'
elif targetcam == "nole8":
    ix, iy, ix2, iy2 = 426, 111, 501, 376
    channel = '1402'
elif targetcam == "nole9":
    ix, iy, ix2, iy2 = 235, 169, 297, 347
    channel = '1502'
elif targetcam == "nole10":
    ix, iy, ix2, iy2 = 308, 177, 514, 294
    channel = '1602'
elif targetcam == "dawara":
    ix, iy, ix2, iy2 = 626, 131, 752, 246
    channel = '602'
else:
    print("targetcam not specified in args")
    targetcam = "nole1"
    ix, iy, ix2, iy2 = 588, 128, 702, 301
    channel = '802'


print("tracking "+targetcam)

streamUrl = 'rtsp://' + username + ':' + password + \
    '@' + ip_address + ':554/Streaming/channels/' + channel
toast = ToastNotifier()


vc = cv2.VideoCapture(streamUrl)


file_object = open('logs_motion\log_motion_'+targetcam+'.txt', 'a')

if vc.isOpened():  # try to get the first frame
    print("starting loop")
    cv2.waitKey(100)

while 1:
    rval1, frame1 = vc.read()
    rval2, frame2 = vc.read()

    if (not rval1) or (not rval2):
        print("skipping this loop")
        continue
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    minx = min(ix, ix2)
    maxx = max(ix, ix2)
    miny = min(iy, iy2)
    maxy = max(iy, iy2)
    gray1_cropped = gray1[miny:maxy, minx:maxx]
    gray2_cropped = gray2[miny:maxy, minx:maxx]
    diff = cv2.absdiff(gray1_cropped, gray2_cropped)

    th, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
    if not thresh is None:
        thresh = cv2.dilate(thresh, None, iterations=6)
    number = cv2.countNonZero(thresh)
    file_object.write(datetime.datetime.now().strftime(
        "%Y/%m/%d %H:%M:%S") + " "+str(number) + "\n")
    file_object.flush()

    key = cv2.waitKey(1000)
    if key == 27:  # exit on ESC
        break

    rval1, frame1 = vc.read()
    rval2, frame2 = vc.read()

cv2.destroyAllWindows()
file_object.close()
