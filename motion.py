# libraries
import datetime
from tkinter.constants import FALSE
import matplotlib.pyplot as plt
import cv2
import ctypes
import numpy as np
import imutils
from win10toast import ToastNotifier
from configparser import ConfigParser
import sys
import os

# Initializers
config = ConfigParser()
config.read('config.ini')
toast = ToastNotifier()


# Controls to run the script
# Streaming Channel & Detection Frame Selection
targetcam = "homecam"
show_motionplot = True
show_selectionwindow = True
show_motionframe = True
show_livefeed = True
# Constants to format
font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
# Constants to stream
ip_address = config.get('stream', 'ip_address')
username = config.get('stream', 'username')
password = config.get('stream', 'password')
# vars for plot
motionplot_limit = 400
motionplot_dates = []
motionplot_values = []
# counters
moving_frames = 0
freeze_frames = 0
# Global state: global state only change when a certain windows has more stop frames than moving frames (or vice versa)
globalstate_flags = []
# 30 flags, for 30 frames, for 30 secs (waiting is 1000ms)
globalstate_flags_limit = 30
global_state = -1  # 0 for stopped, 1 for moving
global_state_msg = ""
global_state_lastchange_date = datetime.datetime.now()
global_state_mins_to_alert_onstop = 20
global_state_stopalert_displayed = False


# mouse callback function for frame selection
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


# Constants to stream channel
try:
    threshold = config.getint(targetcam, 'threshold')
    ix = config.getint(targetcam, 'ix')
    iy = config.getint(targetcam, 'iy')
    ix2 = config.getint(targetcam, 'ix2')
    iy2 = config.getint(targetcam, 'iy2')
    channel = config.get(targetcam, 'channel')
    streamUrl = 'rtsp://' + username + ':' + password + '@' + \
        ip_address + ':554/Streaming/channels/' + channel
    ctypes.windll.kernel32.SetConsoleTitleW("tracking "+targetcam)
    print("tracking "+targetcam)
except ConfigParser.NoOptionError:
    print('could not read targetcam '+targetcam+'from configuration file')
    sys.exit(1)


# Starting the Logic

# cv2.namedWindow("selectionFrame")

if channel == "webcam":
    vc = cv2.VideoCapture(0)
else:
    vc = cv2.VideoCapture(streamUrl)

width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
print("starting camera frame: ", width, height)


if vc.isOpened():  # try to get the first frame
    print("starting loop")
    cv2.waitKey(100)

if show_selectionwindow:
    rval1, selectionFrame = vc.read()
    cv2.imshow("selectionFrame", selectionFrame)
    cv2.setMouseCallback('selectionFrame', handleMouse)


while 1:
    rval1, frame1 = vc.read()
    rval2, frame2 = vc.read()

    if (not rval1) or (not rval2):
        print("can't capture, restarting the stream....")
        vc.release()
        if channel == "webcam":
            vc = cv2.VideoCapture(0)
        else:
            vc = cv2.VideoCapture(streamUrl)
        cv2.waitKey(1000)
        continue

    # Comparing for motion detection

    # Cropping
    minx = min(ix, ix2)
    maxx = max(ix, ix2)
    miny = min(iy, iy2)
    maxy = max(iy, iy2)
    frame1_cropped = frame1[miny:maxy, minx:maxx]
    frame2_cropped = frame2[miny:maxy, minx:maxx]

    # Grey Scale
    frame1_cropped_gray = cv2.cvtColor(frame1_cropped, cv2.COLOR_BGR2GRAY)
    frame2_cropped_gray = cv2.cvtColor(frame2_cropped, cv2.COLOR_BGR2GRAY)

    # Grey Scale
    #gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    #gray2 = cv2.GaussianBlur(gray1, (21, 21), 0)

    # calculating the differences
    diff = cv2.absdiff(frame1_cropped_gray, frame2_cropped_gray)

    # thresholding the motion
    th, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

    # dilating
    if not thresh is None:
        thresh = cv2.dilate(thresh, None, iterations=6)

    # numizing the motion factor
    number = cv2.countNonZero(thresh)

    if show_motionframe:
        if not thresh is None:
            cv2.imshow("motionframe", thresh)

    if show_motionplot:
        motionplot_dates.append(datetime.datetime.now())
        motionplot_values.append(number)
        if len(motionplot_values) > motionplot_limit:
            motionplot_dates.pop(0)
            motionplot_values.pop(0)
            plt.clf()
        plt.plot(motionplot_dates, motionplot_values)
        plt.pause(0.5)

    if show_livefeed:

        # display the motion detected
        if not thresh is None:
            cnts = cv2.findContours(
                thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame1, (ix+x, iy+y),
                              (ix+x + w, iy+y + h), (0, 255, 0), 2)

        # display the motion detection area
        cv2.rectangle(frame1, (ix, iy), (ix2, iy2), (0, 255, 0), 2)
        cv2.circle(frame1, (ix, iy), 5, color, -1)
        cv2.circle(frame1, (ix2, iy2), 5, color, -1)
        cv2.putText(frame1, str(number), (ix, iy), font,
                    fontScale, color, thickness, cv2.LINE_AA)

        # Algorithm to define Moving vs Stop
        if threshold >= 0:
            if number > threshold:
                moving_frames += 1
                cv2.putText(frame1, "Current Frame: Moving", (10, 50), font,
                            0.5, (255, 255, 255), 1, cv2.LINE_AA)
                globalstate_flags.append(1)
            else:
                freeze_frames += 1
                cv2.putText(frame1, "Current Frame: Not moving", (10, 50), font,
                            0.5, (0, 0, 255), 1, cv2.LINE_AA)
                globalstate_flags.append(0)

            # limit moving flags to the counter
            if len(globalstate_flags) > globalstate_flags_limit:
                globalstate_flags.pop(0)

            # check if moving flags are more than half
            if globalstate_flags.count(1) > globalstate_flags_limit / 2:
                # most of the flags are "moving", switching the status
                if not global_state == 1:
                    # changing status from not moving to moving
                    toast.show_toast(
                        "Machine "+targetcam, "Machine just started running again", duration=3, icon_path="python_icon.ico")
                    global_state_lastchange_date = datetime.datetime.now()
                    global_state = 1
                    global_state_msg = "Moving since " + \
                        datetime.datetime.now().strftime(
                            "%Y/%m/%d %H:%M:%S")
                    global_state_stopalert_displayed = False

            else:
                # most of the flags are "not moving", switching the status
                if not global_state == 0:
                    # changing status from moving to not moving
                    toast.show_toast(
                        "Machine "+targetcam, "Machine just stopped", duration=3, icon_path="python_icon.ico")
                    global_state_msg = "Not Moving since " + \
                        datetime.datetime.now().strftime(
                            "%Y/%m/%d %H:%M:%S")
                    global_state = 0
                    global_state_lastchange_date = datetime.datetime.now()
                else:
                    # already on not moving status
                    minutes_from_first_stop = (datetime.datetime.now(
                    ) - global_state_lastchange_date).total_seconds() / 60
                    if minutes_from_first_stop >= global_state_mins_to_alert_onstop and not global_state_stopalert_displayed:
                        global_state_stopalert_displayed = True
                        toast.show_toast("Alert - Machine "+targetcam, "Machine was stopped for "+str(
                            global_state_mins_to_alert_onstop)+" mins", duration=3, icon_path="python_icon.ico")

            cv2.putText(frame1, "moving_frames="+str(moving_frames),
                        (10, 70), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame1, "freeze_frames="+str(freeze_frames),
                        (10, 90), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(frame1, "Current Status="+str(global_state_msg),
                    (10, 110), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("frame1", frame1)

    key = cv2.waitKey(20)  # also pausing on plotting
    if key == 27:  # exit on ESC
        break


# cv2.destroyWindow("selection")
cv2.destroyAllWindows()
toast.show_toast("WOW!!", "script completed",
                 duration=3, icon_path="python_icon.ico")
