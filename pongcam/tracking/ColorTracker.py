import numpy as np
import cv2, cv
import pongcam.util as util

class ColorTracker(util.Tracker):
    def __init__(self):
        self.minbound = np.array([20,20,20])
        self.maxbound = np.array([40,40,40])

    def train(self, region):
        x,y,w,h = [x/2 for x in region]
        # Get region
        train = self.frame[y:y+h,x:x+w]
        cv2.imwrite('debug.jpg', train)
        # Compute bounds
        (l,a,b), (stdl,stda,stdb) = cv2.meanStdDev(train)
        ldelta = stdl*2.5
        adelta = stda*2.5
        bdelta = stdb*2.5
        self.minbound = np.array([l-ldelta, a-adelta, b-bdelta])
        self.maxbound = np.array([l+ldelta, a+adelta, b+bdelta])

    def track(self, frame):
        # Resize for efficiency
        frame = cv2.pyrDown(frame)
        frame = cv2.cvtColor(frame, cv.CV_BGR2Lab)
        self.frame = frame

        capture = cv2.inRange(frame, self.minbound, self.maxbound)

        #contours, _ = cv2.findContours(capture, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # Stupid hack to fix some numpy / opencv bug
        #contours = [c.astype(np.int32) for c in contours]

        loc, contours = util.contour(capture)

        #loc = bestcontour(contours, 10)

        if loc != None:
            loc = [x*2 for x in loc if loc != None]

        self.shape = frame.shape
        self.contours = contours

        return loc

    def view(self):
        out = np.zeros(self.shape, dtype=np.uint8)
        cv2.drawContours(out, self.contours, -1, (255,255,255))
        out = cv2.pyrUp(out)
        return out

