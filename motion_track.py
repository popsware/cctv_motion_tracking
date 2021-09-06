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


# Initializers
streamUrl = 'rtsp://' + username + ':' + password + \
    '@' + ip_address + ':554/Streaming/channels/' + channel
file_object = open('logs_motion\log_motion_'+targetcam+'.txt', 'a')
ctypes.windll.kernel32.SetConsoleTitleW("tracking "+targetcam)
print("tracking "+targetcam)


# Starting the Logic
vc = cv2.VideoCapture(streamUrl)

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
