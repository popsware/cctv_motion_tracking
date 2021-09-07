# libraries
from win10toast import ToastNotifier
import datetime
import sys
import cv2
import ctypes
import tkinter as tk
from tkinter import simpledialog
from configparser import ConfigParser
import sys
from pathlib import Path
import os


# Initializers
config = ConfigParser()
config.read('config.ini')
toast = ToastNotifier()

# Controls to run the script
show_globalstatuschangealerts = False
# Constants to stream
ip_address = config.get('stream', 'ip_address')
username = config.get('stream', 'username')
password = config.get('stream', 'password')
# Global state: global state only change when a certain windows has more stop frames than moving frames (or vice versa)
globalstate_flags = []
# 30 flags, for 30 frames, for 30 secs (waiting is 1000ms)
globalstate_flags_limit = 30
global_state = -1  # 0 for stopped, 1 for moving
global_state_msg = ""
global_state_lastchange_date = datetime.datetime.now()
global_state_mins_to_alert_onstop = 20
global_state_stopalert_displayed = False

# Streaming Channel & Detection Frame Selection
if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    ROOT = tk.Tk()
    ROOT.withdraw()
    # the input dialog
    targetcam = simpledialog.askstring(
        title="Which cam ?", prompt="Camera Name [nole1,nole2,...,dawara]:")

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

#Path("/logs_motion").mkdir(parents=True, exist_ok=True)
os.makedirs("logs_motion", exist_ok=True)
file_object = open('logs_motion\log_motionalert_'+targetcam+'.txt', 'a')


# Starting the Logic

if channel == "webcam":
    vc = cv2.VideoCapture(0)
else:
    vc = cv2.VideoCapture(streamUrl)

width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
print("starting camera frame: ", width, height)


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

    # calculating the differences
    diff = cv2.absdiff(frame1_cropped_gray, frame2_cropped_gray)

    # thresholding the motion
    th, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

    # dilating
    if not thresh is None:
        thresh = cv2.dilate(thresh, None, iterations=6)

    # numizing the motion factor
    number = cv2.countNonZero(thresh)

    # Algorithm to define Moving vs Stop
    if threshold >= 0:
        if number > threshold:
            globalstate_flags.append(1)
            #print("Frame: moving", len(globalstate_flags))
        else:
            globalstate_flags.append(0)
            #print("Frame: not moving", len(globalstate_flags))

        # limit moving flags to the counter
        if len(globalstate_flags) > globalstate_flags_limit:
            globalstate_flags.pop(0)

        # check if moving flags are more than half
        if globalstate_flags.count(1) > globalstate_flags_limit / 2:
            # most of the flags are "moving", switching the status
            if not global_state == 1:
                # changing status from not moving to moving
                stopping_period = (datetime.datetime.now(
                ) - global_state_lastchange_date).total_seconds()/60
                msg = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + \
                    " - Global State: Moving, after being stopped for " + \
                    str(stopping_period)+" min"
                print(msg)
                if show_globalstatuschangealerts:
                    toast.show_toast(
                        "Machine "+targetcam, "Machine just started running again", duration=3, icon_path="python_icon.ico")
                file_object.write(msg + "\n")
                file_object.flush()

                global_state_lastchange_date = datetime.datetime.now()
                global_state = 1
                global_state_stopalert_displayed = False

        else:
            # most of the flags are "not moving", switching the status
            if not global_state == 0:
                # changing status from moving to not moving
                running_period = (datetime.datetime.now(
                ) - global_state_lastchange_date).total_seconds()/60
                msg = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + \
                    " - Global State: Not Moving, after being running for " + \
                    str(running_period)+" min"
                print(msg)
                if show_globalstatuschangealerts:
                    toast.show_toast(
                        "Machine "+targetcam, "Machine just stopped", duration=3, icon_path="python_icon.ico")
                file_object.write(msg + "\n")
                file_object.flush()

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
                    msg = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " - Machine Not Moving since " + \
                        global_state_lastchange_date.strftime(
                            "%Y/%m/%d %H:%M:%S")
                    print(msg)
                    file_object.write(msg + "\n")
                    file_object.flush()

    key = cv2.waitKey(1000)
    if key == 27:  # exit on ESC
        break


cv2.destroyAllWindows()
