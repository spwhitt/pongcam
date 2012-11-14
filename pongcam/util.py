import cv2
import numpy as np

def contour(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Stupid hack to fix some numpy / opencv bug
    contours = [c.astype(np.int32) for c in contours]
    loc = bestloc(contours, 10)
    return (loc, contours)

def bestloc(contours, minsize):
    bestsize = 0
    best = None
    contours = [c for c in contours if np.size(c) > 100]
    if len(contours) > 0:
        best = max(contours, key=np.size)
        x,y,w,h = cv2.boundingRect(best)
        #print best.shape
        #best = (np.sum(best[:,0,0])/best.shape[0], np.sum(best[:,0,1])/best.shape[0])
        #print np.sum(best[:,1,2])
        best = (x+w/2, y+h/2)

    #for c in contours:
        #x,y,w,h = cv2.boundingRect(c)
        #if w<minsize or h<minsize:
            #continue
        #size = w*h
        #if size > bestsize:
            #bestsize = size
            #best = (x+w/2, y+h/2)
    return best

class Tracker(object):
    def train(self, region):
        """
        Frame: RGB image from webcam
        Region: Area of screen selected by user
        Used to learn necessary image features for tracking
        """
        raise NotImplementedError

    def track(self, frame):
        """
        Frame: RGB image from webcam
        Return: Point representing center of object in image
        """
        raise NotImplementedError

    def view(self):
        """
        View debug image
        """
        raise NotImplementedError

# Class to keep track of trackers, swap between them, etc.
# Train all of them at once?
# But what if one depends on location data? Then it would need to track from
# beginning too...
# CONCLUSION: Hotswapping is OUT.
#class Trackers(object):
    #def __init__(self):
