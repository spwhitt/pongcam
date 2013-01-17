import numpy as np
import cv2, cv
import pongcam.util as util

class BackProjectTracker(util.Tracker):
    def __init__(self):
        self.frame = np.zeros((100,100,3), dtype=np.uint8)
        self.train([100,100,100,100])

    def train(self, region):
        # Resize region
        x,y,w,h = [x/2 for x in region]
        # Get region
        train = self.frame[y:y+h,x:x+w]

        # Calculate histogram
        lhist = cv2.calcHist([train], [0], None, [10], [0,255])
        ahist = cv2.calcHist([train], [1], None, [10], [0,255])
        bhist = cv2.calcHist([train], [2], None, [10], [0,255])

        # Convert histogram to probability distribution
        lhist = lhist / np.sum(lhist)
        ahist = ahist / np.sum(ahist)
        bhist = bhist / np.sum(bhist)

        self.hist = [lhist, ahist, bhist]
        #self.hist = [ahist, bhist]

    def track(self, frame):
        # Resize for efficiency
        frame = cv2.pyrDown(frame)
        frame = cv2.cvtColor(frame, cv.CV_BGR2Lab)
        self.frame = frame

        l,a,b = self.hist
        # Convert to float32 so we can represent probability values
        frame = frame.astype(np.float32)
        lback = cv2.calcBackProject([frame], [0], l, [0,255], 1)
        aback = cv2.calcBackProject([frame], [1], a, [0,255], 1)
        bback = cv2.calcBackProject([frame], [2], b, [0,255], 1)

        # Combine channels and convert to image
        self.back = (aback * bback * lback ) * 255
        self.back = self.back.astype(np.uint8)

        tmp = np.array(self.back)
        loc, contours = util.contour(tmp)

        self.contours = contours

        # Scale loc back up due to pyrDown
        if loc != None:
            loc = [x*2 for x in loc if loc != None]

        return loc

    def view(self):
        out = cv2.cvtColor(self.back, cv.CV_GRAY2RGB)
        cv2.drawContours(out, self.contours, -1, (0,0,255))
        out = cv2.pyrUp(out)
        return out

