import datetime
import sys
from configparser import ConfigParser
import cv2
import ctypes
import tkinter as tk
from tkinter import simpledialog
from pathlib import Path
import os

# Initializers

config = ConfigParser()
config.read('config.ini')


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


# Constants to stream
ip_address = config.get('stream', 'ip_address')
username = config.get('stream', 'username')
password = config.get('stream', 'password')


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
file_object = open('logs_motion\log_motion_'+targetcam+'.txt', 'a')


# Starting the Logic
#vc = cv2.VideoCapture(streamUrl)
vc = cv2.VideoCapture(0)

width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
print("starting camera frame: ", width, height)

if not vc.isOpened():  # try to get the first frame
    print("coulnt access this VC")
else:
    while 1:
        rval1, frame1 = vc.read()
        rval2, frame2 = vc.read()
        if (not rval1) or (not rval2):
            print("can't capture, restarting the stream....")
            vc.release()
            vc = cv2.VideoCapture(streamUrl)
            cv2.waitKey(1000)
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
        print(str(number))
        file_object.flush()

        key = cv2.waitKey(1000)
        if key == 27:  # exit on ESC
            break

cv2.destroyAllWindows()
file_object.close()
