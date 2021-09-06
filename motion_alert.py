# libraries
from win10toast import ToastNotifier
import datetime
import sys
import cv2
import ctypes
import tkinter as tk
from tkinter import simpledialog

# Constants to stream
ip_address = "192.168.1.20"
username = "admin"
password = "ayman1351359"

# Constants to format
font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2


# Controls to run the script
show_globalstatuschangealerts = False

# Streaming Channel & Detection Frame Selection

if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    ROOT = tk.Tk()
    ROOT.withdraw()
    # the input dialog
    targetcam = simpledialog.askstring(
        title="Which cam ?", prompt="Camera Name [nole1,nole2,...,dawara]:")

if targetcam == "nole1":
    threshold = 500       # movement fail rate: 20%
    ix, iy, ix2, iy2 = 285, 63, 317, 124
    channel = '802'

elif targetcam == "nole2":
    threshold = 500       # movement fail rate: ??
    ix, iy, ix2, iy2 = 323, 141, 703, 191
    channel = '902'

elif targetcam == "nole3":
    threshold = 0       # movement fail rate: ??
    ix, iy, ix2, iy2 = 228, 307, 301, 385
    channel = '1002'

elif targetcam == "nole4":
    threshold = 500       # movement fail rate: ??
    ix, iy, ix2, iy2 = 462, 181, 548, 304
    channel = '1102'

elif targetcam == "nole5":
    # [x] tested
    threshold = 500       # movement fail rate: 15%
    ix, iy, ix2, iy2 = 34, 255, 230, 315
    channel = '1102'

elif targetcam == "nole6":
    threshold = 200       # movement fail rate: 50%
    ix, iy, ix2, iy2 = 452, 209, 605, 387
    channel = '1202'

elif targetcam == "nole7":
    threshold = 2000       # movement fail rate: 0%
    ix, iy, ix2, iy2 = 347, 7, 391, 94
    channel = '1302'

elif targetcam == "nole8":
    threshold = 0       # movement fail rate: ??
    ix, iy, ix2, iy2 = 426, 111, 501, 376
    channel = '1402'

elif targetcam == "nole9":
    threshold = 500       # movement fail rate: 25%
    ix, iy, ix2, iy2 = 326, 179, 393, 453
    channel = '1502'

elif targetcam == "nole10":
    threshold = 200      # movement fail rate: 0.5%
    ix, iy, ix2, iy2 = 301, 39, 449, 250
    channel = '1602'

elif targetcam == "nole11":
    threshold = 0       # movement fail rate: ??
    ix, iy, ix2, iy2 = 505, 76, 518, 120
    channel = '2002'

elif targetcam == "dawara":
    threshold = 0       # movement fail rate: ??
    ix, iy, ix2, iy2 = 626, 131, 752, 246
    channel = '602'

elif targetcam == "lazona":
    threshold = 0       # movement fail rate: ??
    ix, iy, ix2, iy2 = 18, 75, 278, 285
    channel = '702'

else:
    print("targetcam not supported, falling back to nole1")
    threshold = 500
    stickered = True
    ix, iy, ix2, iy2 = 280, 63, 312, 124
    channel = '802'


# Global state: global state only change when a certain windows has more stop frames than moving frames (or vice versa)
globalstate_flags = []
# 30 flags, for 30 frames, for 30 secs (waiting is 1000ms)
globalstate_flags_limit = 30
global_state = -1  # 0 for stopped, 1 for moving
global_state_msg = ""
global_state_lastchange_date = datetime.datetime.now()
global_state_mins_to_alert_onstop = 20
global_state_stopalert_displayed = False


# Initializers
streamUrl = 'rtsp://' + username + ':' + password + \
    '@' + ip_address + ':554/Streaming/channels/' + channel
toast = ToastNotifier()
file_object = open('logs_motion\log_motionalert_'+targetcam+'.txt', 'a')
ctypes.windll.kernel32.SetConsoleTitleW("tracking "+targetcam)
print("tracking "+targetcam)


# Starting the Logic
# cv2.namedWindow("selectionFrame")
#vc = cv2.VideoCapture(0)
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
