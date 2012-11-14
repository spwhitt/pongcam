import numpy as np
import cv2, cv
from util import *

def normalize_bgr(bgr):
    frame = cv2.cvtColor(bgr, cv.CV_BGR2RGB).astype(np.float32)
    norm = 255/np.sum(frame, axis=2)
    frame = (frame / norm[:,:,np.newaxis]).astype(np.uint8)
    return frame

class NormalizeRGB(Tracker):
    def __init__(self):
        self.minbound = np.array([100,100,100])
        self.maxbound = np.array([200,200,200])

    def train(self, region):
        x,y,w,h = region
        # Get region
        train = self.frame[y:y+h,x:x+w]
        cv2.imwrite('debug.jpg', train)
        # Compute bounds
        (l,a,b), (stdl,stda,stdb) = cv2.meanStdDev(train)
        ldelta = stdl*1
        adelta = stda*1
        bdelta = stdb*1
        self.minbound = np.array([l-ldelta, a-adelta, b-bdelta])
        self.maxbound = np.array([l+ldelta, a+adelta, b+bdelta])

    def track(self, frame):
        self.frame = normalize_bgr(frame)
        thresh = cv2.inRange(self.frame, self.minbound, self.maxbound)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        loc = bestcontour(contours, 10)

        self.shape = frame.shape
        self.contours = contours

        return loc

    def view(self):
        out = np.zeros(self.shape, dtype=np.uint8)
        cv2.drawContours(out, self.contours, -1, (255,255,255))
        return out
