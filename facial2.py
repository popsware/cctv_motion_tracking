from Th_ReadCamera import ThreadedCamera
import cv2
from win10toast import ToastNotifier
from configparser import ConfigParser


def vconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
    return cv2.vconcat(im_list_resize)


if __name__ == '__main__':

    config_stream = ConfigParser()
    config_stream.read('config_stream.ini')
    ip_address = config_stream.get('stream', 'ip_address')
    username = config_stream.get('stream', 'username')
    password = config_stream.get('stream', 'password')
    config_cam = ConfigParser()
    config_cam.read('config_cam.ini')
    targetcam = "outside2"
    channel = config_cam.get(targetcam, 'channel')
    streamUrl = 'rtsp://' + username + ':' + password + '@' + ip_address + ':554/Streaming/channels/'+channel
    streamer = ThreadedCamera(streamUrl)

    while True:
        frame = streamer.grab_frame()

        if frame is not None:
            # Detecting Faces

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) > 0:
                print("Found {0} faces!".format(len(faces)))

                pdList = []
                # Draw a rectangle around the faces
                for (x, y, w, h) in faces:
                    pdList.append(frame[y:y+h, x:x+w])
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                frame_faces = vconcat_resize_min(pdList)
                cv2.imshow("Faces", frame_faces)
            else:
                # cv2.destroyWindow("Faces")
                print("No Faces Detected")

            cv2.imshow("Context", frame)

        key = cv2.waitKey(1)
        if key == 27:  # exit on ESC
            break
