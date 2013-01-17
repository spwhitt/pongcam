import cv2, cv, sys

class Camera(object):
    def __init__(self):
        # Start the webcam
        cam = cv2.VideoCapture(0)
        self.cam = cam
        if not cam.isOpened():
            sys.exit("Unable to open webcam")

        # Output camera info
        self.width = int(cam.get(cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(cam.get(cv.CV_CAP_PROP_FRAME_HEIGHT))

        print "Webcam connected."
        print "Capture size: %s x %s" % (self.width, self.height)

    def click(self):
        """ Take a picture """
        success, capture = self.cam.read()
        if not success:
            sys.exit("Failed to capture frame")
        # Flip image on both axis: the y axis to compensate for pyglet, and the x
        # axis to cause the webcam to act like a mirror
        #capture = cv2.pyrDown(capture)
        capture = cv2.flip(capture, -1)
        #self.pic = capture
        return capture

    def done(self):
        self.cam.release()
