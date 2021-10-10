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
#import requests

from Th_SendRequests import Requester


# Initializers
config_stream = ConfigParser()
config_stream.read('config_stream.ini')
config_cam = ConfigParser()
config_cam.read('config_cam.ini')
toast = ToastNotifier()

# Controls to run the script
alert_globalmotion_change = False
alert_deepsleep_warn = True
write_motion = True
write_globalmotion_change = True
write_deepsleep_warn = True

# Constants to stream
ip_address = config_stream.get('stream', 'ip_address')
username = config_stream.get('stream', 'username')
password = config_stream.get('stream', 'password')
ifttt_key = config_stream.get('ifttt', 'ifttt_key')
ifttt_event = config_stream.get('ifttt', 'ifttt_event')
# Global Motion: global state only change when a certain windows has more stop frames than moving frames (or vice versa)
globalmotion_flags = []
# 30 flags, for 30 frames, for 30 secs (waiting is 1000ms)
globalmotion_flags_limit = 30
globalmotion_status = -1  # 0 for stopped, 1 for moving
globalmotion_msg = ""
globalmotion_lastchange_date = datetime.datetime.now()
globalmotion_deepsleep_mins = 20
globalmotion_deepsleep_alertdisplayed = False

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
    threshold = config_cam.getint(targetcam, 'threshold')
    ix = config_cam.getint(targetcam, 'ix')
    iy = config_cam.getint(targetcam, 'iy')
    ix2 = config_cam.getint(targetcam, 'ix2')
    iy2 = config_cam.getint(targetcam, 'iy2')
    machineid = config_cam.getint(targetcam, 'machineid')
    channel = config_cam.get(targetcam, 'channel')
    streamUrl = 'rtsp://' + username + ':' + password + '@' + ip_address + ':554/Streaming/channels/' + channel
    print("streaming ", streamUrl)
    ctypes.windll.kernel32.SetConsoleTitleW("Tracking "+targetcam)
    print("Tracking ", targetcam)
except:
    print('could not read targetcam '+targetcam+'from configuration file')
    sys.exit(1)

#Path("/logs_motion").mkdir(parents=True, exist_ok=True)
os.makedirs("logs_motion", exist_ok=True)
file_deepsleep_warn = open('logs_motion\log_deepsleep_warn_'+targetcam+'.txt', 'a')
file_globalmotion_change = open('logs_motion\log_globalmotion_change_'+targetcam+'.txt', 'a')
file_motion = open('logs_motion\log_motion_'+targetcam+'.txt', 'a')


req = Requester()
response = req.startMachine(machineid)


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
    print(str(number))

    # write movement to file
    if write_motion:
        file_motion.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " "+str(number) + "\n")
        file_motion.flush()

    # Algorithm to define Moving vs Stop
    if threshold >= 0:
        if number > threshold:
            globalmotion_flags.append(1)
            #print("Frame: moving", len(globalmotion_flags))
        else:
            globalmotion_flags.append(0)
            #print("Frame: stopped", len(globalmotion_flags))

        # limit moving flags to the counter
        if len(globalmotion_flags) > globalmotion_flags_limit:
            globalmotion_flags.pop(0)

        # check if moving flags are more than half
        if globalmotion_flags.count(1) > globalmotion_flags_limit / 2:
            #
            # Global Status: Moving_State
            # most of the flags are "moving", switching the status
            #
            #
            #
            if not globalmotion_status == 1:
                # changing status from stopped to moving
                stopping_period = int((datetime.datetime.now() - globalmotion_lastchange_date).total_seconds()/60)

                title = "Moving_State "+targetcam
                message = "was stopped for " + str(stopping_period)+" min"
                message_withdate = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " - "+title + " - "+message

                print(message_withdate)

                if alert_globalmotion_change:
                    toast.show_toast(
                        "Machine "+targetcam, "Machine status changed to running (was stopped for "+str(stopping_period)+"mins)", icon_path="python_icon.ico", duration=3)

                if write_globalmotion_change:
                    file_globalmotion_change.write(message_withdate + "\n")
                    file_globalmotion_change.flush()

                globalmotion_lastchange_date = datetime.datetime.now()
                globalmotion_status = 1

                if globalmotion_deepsleep_alertdisplayed:

                    #
                    # Deep sleep: Waking Up
                    #
                    #
                    globalmotion_deepsleep_alertdisplayed = False

                    title = "Woke_Up: "+targetcam
                    message = "Idle time: " + str(stopping_period)+" min"
                    message_withdate = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " - "+title + " - "+message

                    print(message_withdate)

                    response = req.post('https://maker.ifttt.com/trigger/'+ifttt_event+'/with/key/'+ifttt_key, params={
                        "value1": title, "value2": message, "value3": "none"})

                    if response is None:
                        print("request failed to trigger IFTTT")
                        file_deepsleep_warn.write("request failed to trigger IFTTT\n")
                        file_deepsleep_warn.flush()
                    elif not (response.status_code == 200):
                        print(response.text)
                        file_deepsleep_warn.write(str(response.text) + "\n")
                        file_deepsleep_warn.flush()

                    response = req.startMachine(machineid)

                    if alert_deepsleep_warn:
                        toast.show_toast(title, message, icon_path="python_icon.ico", duration=3)

                    if write_deepsleep_warn:
                        file_deepsleep_warn.write(message_withdate + "\n")
                        file_deepsleep_warn.flush()

        else:
            #
            # Global Status: Stopped_State
            # most of the flags are "stopped", switching the status
            #
            #
            #
            if not globalmotion_status == 0:
                # changing status from moving to stopped

                title = "Stopped_State "+targetcam
                message = ""
                message_withdate = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " - "+title + " - "+message

                print(message_withdate)

                if alert_globalmotion_change:
                    toast.show_toast(title, message, icon_path="python_icon.ico", duration=3)

                if write_globalmotion_change:
                    file_globalmotion_change.write(message_withdate + "\n")
                    file_globalmotion_change.flush()

                globalmotion_status = 0
                globalmotion_lastchange_date = datetime.datetime.now()

            else:
                # already on stopped status
                minutes_from_first_stop = (datetime.datetime.now() - globalmotion_lastchange_date).total_seconds() / 60

                if minutes_from_first_stop >= globalmotion_deepsleep_mins:

                    #
                    # Deep sleep: Entering Deep Sleep
                    #
                    #
                    if not globalmotion_deepsleep_alertdisplayed:
                        globalmotion_deepsleep_alertdisplayed = True

                        title = "Deep_Sleep: "+targetcam
                        message = "stopped " + str(globalmotion_deepsleep_mins)+" mins ago"
                        message_withdate = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " - "+title + " - "+message
                        print(message_withdate)

                        response = req.post('https://maker.ifttt.com/trigger/'+ifttt_event+'/with/key/'+ifttt_key,
                                            params={"value1": title, "value2": message, "value3": "none"})

                        if response is None:
                            print("request failed to trigger IFTTT")
                            file_deepsleep_warn.write("request failed to trigger IFTTT\n")
                            file_deepsleep_warn.flush()
                        elif not (response.status_code == 200):
                            print(response.text)
                            file_deepsleep_warn.write(str(response.text) + "\n")
                            file_deepsleep_warn.flush()

                        response = req.stopMachine(machineid)

                        if alert_deepsleep_warn:
                            toast.show_toast(title, message, icon_path="python_icon.ico", duration=3)

                        if write_deepsleep_warn:
                            file_deepsleep_warn.write(message_withdate + "\n")
                            file_deepsleep_warn.flush()

    key = cv2.waitKey(1000)
    if key == 27:  # exit on ESC
        break


cv2.destroyAllWindows()
file_motion.close()
file_globalmotion_change.close()
file_deepsleep_warn.close()
