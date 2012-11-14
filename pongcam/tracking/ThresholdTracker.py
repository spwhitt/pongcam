import numpy as np
import cv2, cv
import util

class ThresholdTracker(util.Tracker):
    def __init__(self, threshold = 200, minsize = 5):
        self.threshold = threshold
        # Blobs must be larger than this to count as an object
        self.minsize = minsize

    def train(self, region):
        # IDEA: If I could speed this up, it could be selected on the fly at
        # threshold time

        # ANOTHER IDEA: Average values of frame within region
        # Subtract some value, and let that be your threshold

        values = np.sort(self.frame, axis=None)
        # Keep about 300 pixels in the threshold
        self.threshold = values[-300]
        print self.threshold

    def track(self, frame):
        # IDEA: Hugh transform to look for circle shape
        #frame = cv2.pyrDown(frame)
        thresh = cv2.cvtColor(frame, cv.CV_RGB2GRAY)
        self.frame = thresh
        _, thresh = cv2.threshold(thresh, self.threshold, 255, cv.CV_THRESH_BINARY)

        #contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #loc = bestcontour(contours, 10)
        loc, contours = util.contour(thresh)

        self.shape = frame.shape
        self.contours = contours

        return loc

    def view(self):
        out = np.zeros(self.shape, dtype=np.uint8)
        cv2.drawContours(out, self.contours, -1, (255,255,255))
        #out = cv2.pyrUp(out)
        return out
