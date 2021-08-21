import cv2
import numpy as np

drawing = True
ix, iy, iw, ih = 0, 0, 100, 100


font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2


# mouse callback function
def handleMouse(event, x, y, flags, param):
    global ix, iy, iw, ih
    #print("click ", ix, iy)
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        print("draw started ", x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        iw = x-ix
        ih = y-iy
        print("draw ended ", x, y)
        rval1, selectionFrame = vc.read()
        cv2.rectangle(selectionFrame, (ix, iy),
                      (ix + iw, iy + ih), (0, 255, 0), 2)
        cv2.putText(selectionFrame, str(ix)+" x "+str(iy), (ix, iy), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        cv2.circle(selectionFrame, (ix, iy), 5, color, -1)
        cv2.putText(selectionFrame, str(x)+" x "+str(y), (x, y), font,
                    fontScale, color, thickness, cv2.LINE_AA)
        cv2.circle(selectionFrame, (x, y), 5, color, -1)
        cv2.imshow("selectionFrame", selectionFrame)


ip_address = "192.168.1.20"
username = "admin"
password = "ayman1351359"
streamUrl = 'rtsp://' + username + ':' + password + \
    '@' + ip_address + ':554/Streaming/channels/902'


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
    rval1, selectionFrame = vc.read()
    cv2.imshow("selectionFrame", selectionFrame)
    cv2.setMouseCallback('selectionFrame', handleMouse)
else:
    rval1 = False


while rval1:

    rval1, frame1 = vc.read()
    rval2, frame2 = vc.read()
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    #gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    #gray2 = cv2.GaussianBlur(gray1, (21, 21), 0)
    gray1_cropped = gray1[iy:iy+ih, ix:ix+iw]
    gray2_cropped = gray2[iy:iy+ih, ix:ix+iw]
    diff = cv2.absdiff(gray1_cropped, gray2_cropped)

    number = cv2.countNonZero(diff)
    print(number)
    cv2.imshow("motion", diff)

    cv2.rectangle(frame1, (ix, iy), (ix + iw, iy + ih), (0, 255, 0), 2)
    cv2.circle(frame1, (ix, iy), 5, color, -1)
    cv2.circle(frame1, (ix+iw, iy+ih), 5, color, -1)
    cv2.putText(frame1, str(number), (ix, iy), font,
                fontScale, color, thickness, cv2.LINE_AA)
    cv2.imshow("frame1", frame1)

    # print("waiting...")
    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
    # print("resuming.")

cv2.destroyWindow("selection")
