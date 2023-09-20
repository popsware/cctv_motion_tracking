# libraries

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
from Helpers.Notifier import *
from Helpers.Th_SendRequests import Requester


# ---------------------------------------------------------------------------
# Constants -----------------------------------------------------------------
# ---------------------------------------------------------------------------
write_motionchange = True
GLOBALMOTION_STOPPED = 0
GLOBALMOTION_MOVING = 1

# ---------------------------------------------------------------------------
# Variables -----------------------------------------------------------------
# ---------------------------------------------------------------------------

# Global Motion: global state only change when a certain windows has more stop frames than moving frames (or vice versa)
globalmotion_flags = []
# 60 flags, for 60 frames, for 60 secs (waiting is 1000ms)
globalmotion_flags_limit = 60
globalmotion_status = GLOBALMOTION_MOVING  # will start as moving until proven otherwise
globalmotion_msg = ""
globalmotion_lastchange_date = datetime.datetime.now()
globalmotion_deepsleep_mins = 20
globalmotion_isdeepsleeping = False

# ---------------------------------------------------------------------------
# Initializers ---------------------------------------------------
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Configuration -------------------------------------------------------------
# ---------------------------------------------------------------------------
config_stream = ConfigParser()
config_stream.read("config/config_stream.ini")
config_cam = ConfigParser()
config_cam.read("config/config_cam.ini")
ip_address = config_stream.get("stream", "ip_address")
username = config_stream.get("stream", "username")
password = config_stream.get("stream", "password")


# Streaming Channel & Detection Frame Selection
if len(sys.argv) > 1:
    targetcam = sys.argv[1]
else:
    ROOT = tk.Tk()
    ROOT.withdraw()
    # the input dialog
    targetcam = simpledialog.askstring(
        title="Which cam ?", prompt="Camera Name [nole1,nole2,...,dawara]:"
    )
print("targetcam=" + targetcam)

# ---------------------------------------------------------------------------
# stream channel URL ---------------------------------------------------
# ---------------------------------------------------------------------------

try:
    threshold = config_cam.getint(targetcam, "threshold")
    ix = config_cam.getint(targetcam, "ix")
    iy = config_cam.getint(targetcam, "iy")
    ix2 = config_cam.getint(targetcam, "ix2")
    iy2 = config_cam.getint(targetcam, "iy2")
    machineid = config_cam.getint(targetcam, "machineid")
    channel = config_cam.get(targetcam, "channel")
    streamUrl = (
        "rtsp://"
        + username
        + ":"
        + password
        + "@"
        + ip_address
        + ":554/Streaming/channels/"
        + channel
    )
    print("streaming ", streamUrl)
    ctypes.windll.kernel32.SetConsoleTitleW(targetcam + " Tracking")
    print(targetcam, " Tracking")
except:
    print("could not read targetcam " + targetcam + "from configuration file")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Prepare the Log Files ----------------------------------------------------------------
# ---------------------------------------------------------------------------

# Path("\logs\motion_tracking").mkdir(parents=True, exist_ok=True)
logdir = "logs\motion_tracking\\" + targetcam
os.makedirs(logdir, exist_ok=True)
file_deepsleep = open(logdir + "\log_deepsleep_" + targetcam + ".log", "a")
file_globalstatechange = open(
    logdir + "\log_globalstatechange_" + targetcam + ".log", "a"
)
file_motion = open(logdir + "\log_motion_" + targetcam + ".log", "a")

try:
    factSystemRequester = Requester(machineid)
    factSystemRequester.resetMachine()
except:
    print("Requester Failed. Can't Connect to FactSystem API and to IFTTT")


# ---------------------------------------------------------------------------
# Starting the Logic -----------------------------------------------------------------------------
# ---------------------------------------------------------------------------

if channel == "webcam":
    vc = cv2.VideoCapture(0)
else:
    vc = cv2.VideoCapture(streamUrl)

width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
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
    print(str(number))

    # write movement to file
    if write_motionchange:
        file_motion.write(
            datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            + " "
            + str(number)
            + "\n"
        )
        file_motion.flush()

    # Algorithm to define Moving vs Stop
    if threshold >= 0:
        if number > threshold:
            globalmotion_flags.append(1)
            # print("Frame: moving", len(globalmotion_flags))
        else:
            globalmotion_flags.append(0)
            # print("Frame: stopped", len(globalmotion_flags))

        # limit moving flags to the counter
        if len(globalmotion_flags) > globalmotion_flags_limit:
            globalmotion_flags.pop(0)

        # check if moving flags are more than half
        if globalmotion_flags.count(GLOBALMOTION_MOVING) > globalmotion_flags_limit / 2:
            ################## Global Status: Moving_State (most of the flags are "moving"), switching the status #####################

            if not globalmotion_status == GLOBALMOTION_MOVING:
                ################## changing status from stopped to moving #####################
                ################## Alert that machine is now moving #####################

                stopping_period = int(
                    (
                        datetime.datetime.now() - globalmotion_lastchange_date
                    ).total_seconds()
                    / 60
                )
                notify_StartMoving(
                    stopping_period,
                    targetcam,
                    file_globalstatechange,
                    factSystemRequester,
                )

                globalmotion_lastchange_date = datetime.datetime.now()
                globalmotion_status = GLOBALMOTION_MOVING

                if globalmotion_isdeepsleeping:
                    ################## Deep sleep: Waking Up #####################

                    globalmotion_isdeepsleeping = False

                    notify_DeepSleepWakeup(
                        stopping_period,
                        targetcam,
                        factSystemRequester,
                        file_deepsleep,
                    )

        else:
            ################## Global Status: Stopped_State (most of the flags are "stopped"), switching the status #####################

            if not globalmotion_status == GLOBALMOTION_STOPPED:
                ################## changing status from moving to stopped #####################
                ################## Alert that machine is stopped (for a while now) #####################

                notify_StopMoving(
                    targetcam, file_globalstatechange, factSystemRequester
                )

                globalmotion_status = GLOBALMOTION_STOPPED
                globalmotion_lastchange_date = datetime.datetime.now()

            else:
                # already on stopped status
                minutes_from_first_stop = (
                    datetime.datetime.now() - globalmotion_lastchange_date
                ).total_seconds() / 60
                enterDeepSleep = (
                    minutes_from_first_stop >= globalmotion_deepsleep_mins
                ) and not globalmotion_isdeepsleeping

                if enterDeepSleep:
                    ################## Deep sleep: Entering Deep Sleep #####################
                    ################## Alert that machine is now in deepsleep #####################
                    globalmotion_isdeepsleeping = True
                    notify_DeepSleep(
                        targetcam,
                        globalmotion_deepsleep_mins,
                        factSystemRequester,
                        file_deepsleep,
                    )

    key = cv2.waitKey(1000)
    if key == 27:  # exit on ESC
        break


cv2.destroyAllWindows()
file_motion.close()
file_globalstatechange.close()
file_deepsleep.close()


# stop the cmd terminal from closing if the code breaks
input("Press Enter to continue...")
