# libraries
import datetime
import matplotlib.pyplot as plt
import cv2
import numpy as np
import imutils
from win10toast import ToastNotifier

ip_address = "192.168.1.20"
username = "admin"
password = "ayman1351359"
font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
showmotionplot = True
showselectionwindow = True
showmotionframe = True
showlivefeed = True

ix, iy, ix2, iy2 = 626, 131, 752, 246
channel = '602'


dates = []
values = []
streamUrl = 'rtsp://' + username + ':' + password + \
    '@' + ip_address + ':554/Streaming/channels/' + channel
toast = ToastNotifier()


# mouse callback function
def handleMouse(event, x, y, flags, param):
    global ix, iy, ix2, iy2
    #print("click ", ix, iy)
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        print("draw started ", x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        ix2 = x
        iy2 = y
        print("draw ended ", x, y)
        rval1, selectionFrame = vc.read()
        cv2.rectangle(selectionFrame, (ix, iy),
                      (ix2, iy2), (0, 255, 0), 2)
        cv2.putText(selectionFrame, str(ix)+" x "+str(iy), (ix, iy), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        cv2.circle(selectionFrame, (ix, iy), 5, color, -1)
        cv2.putText(selectionFrame, str(ix2)+" x "+str(iy2), (ix2, iy2), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        cv2.circle(selectionFrame, (ix2, iy2), 5, color, -1)
        cv2.imshow("selectionFrame", selectionFrame)


# cv2.namedWindow("selectionFrame")
#vc = cv2.VideoCapture(0)
vc = cv2.VideoCapture(streamUrl)

width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
print("camera frame: ", width, height)
#img = np.zeros((int(height), int(width), 3), np.uint8)
#img = np.full((H, W, 4), (0, 0, 0, 0), np.uint8)


if vc.isOpened():  # try to get the first frame
    print("starting loop")
    cv2.waitKey(100)

if showselectionwindow:
    rval1, selectionFrame = vc.read()
    cv2.imshow("selectionFrame", selectionFrame)
    cv2.setMouseCallback('selectionFrame', handleMouse)


while 1:
    rval1, frame1 = vc.read()
    rval2, frame2 = vc.read()

    if (not rval1) or (not rval2):
        print("skipping this loop")
        continue
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    #gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    #gray2 = cv2.GaussianBlur(gray1, (21, 21), 0)
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

    if showmotionframe:
        cv2.imshow("motionframe", thresh)

    if showmotionplot:
        dates.append(datetime.datetime.now())
        values.append(number)
        if len(values) > 400:
            dates.pop(0)
            values.pop(0)
            plt.clf()
        plt.plot(dates, values)
        plt.pause(0.5)

    if showlivefeed:
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # loop over the contours
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame1, (ix+x, iy+y),
                          (ix+x + w, iy+y + h), (0, 255, 0), 2)

        cv2.rectangle(frame1, (ix, iy), (ix2, iy2), (0, 255, 0), 2)
        cv2.circle(frame1, (ix, iy), 5, color, -1)
        cv2.circle(frame1, (ix2, iy2), 5, color, -1)
        cv2.putText(frame1, str(number), (ix, iy), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        cv2.imshow("frame1", frame1)

    # print("waiting...")
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
    # print("resuming.")

    rval1, frame1 = vc.read()
    rval2, frame2 = vc.read()

# cv2.destroyWindow("selection")
cv2.destroyAllWindows()
toast.show_toast("WOW!!", "script completed",
                 duration=3, icon_path="python_icon.ico")
