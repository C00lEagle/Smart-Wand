# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# a call back function for the trackbars... it does nothing...
def nothing(jnk):
    pass

#some color values we'll be using
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)

# the resoultion of the camera... common values: (1296,972), (640,480), (320,240), (240, 180)
# smaller resolutions work best when viewed remotely, however they all work great natively
resolution = (320,240)

# create the named window and the trackbars...
winName = 'Target Detect'
cv2.namedWindow(winName)
cv2.createTrackbar('showThreshold', winName, 0, 1, nothing)  # shows the threshold binary image if 1, shows the original otherwise
cv2.createTrackbar('threshold', winName, 100, 255, nothing)  # the threshold value
cv2.createTrackbar('minPerim', winName, 100, 1000, nothing)  # the minimum perimiter of the convex hull to be kept
cv2.createTrackbar('epsilon', winName, 10, 1000, nothing)    # the epsilon used for approximating the perimiter
cv2.createTrackbar('autoShutter', winName, 50, 255, nothing) # used to automatically set the shutter speed, this is the target average pixel value.

# initialize the camera and grab a reference to the raw camera capture
# there are a lot of options we can do here... check out the examples
# at http://picamera.readthedocs.org/en/release-1.9/recipes1.html
camera = PiCamera()
camera.resolution = resolution
camera.shutter_speed = 10000
camera.exposure_mode = 'off'

rawCapture = PiRGBArray(camera, size=resolution)
 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    # get the trackbar values...
    drawThresh = cv2.getTrackbarPos('showThreshold', winName)
    thresh = cv2.getTrackbarPos('threshold',winName)
    minPerim = cv2.getTrackbarPos('minPerim', winName)
    eps = cv2.getTrackbarPos('epsilon',winName)
    autoShutter = cv2.getTrackbarPos('autoShutter', winName)
    ss = camera.shutter_speed # also get the shutter speed.

    #start timer
    t = cv2.getTickCount()

    # grab the raw NumPy array representing the image
    drawnImage = image = frame.array

    # convert to a grayscale image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # calculate the avarage pixel value
    avg = cv2.mean(gray_image)

    # threshold the grayscale image
    ret, threshImg = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)

    # if the trackbar is set to 1, use the threshold image to draw on instead
    if drawThresh == 1:
        # convert the threshold image back to color so we can draw on it with colorful lines
        drawnImage = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2RGB)

    # find the contours in the thresholded image...
    im2, contours, high = cv2.findContours(threshImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # the arrays of detected targets, they're empty now, but we'll fill them next.
    hulls = []      # this will be the convex hulls
    aproxHulls = [] # this will be the aproximated convex hulls
    rects = []      # this will be the rotated rectangles around the convex hulls

    # for each contour we found...
    for cnt in contours:
        # get the convexHull
        hull = cv2.convexHull(cnt)

        # get the perimiter of the hull
        perim = cv2.arcLength(hull, True)

        # is the the perimiter of the hull is > than the minimum allowed?
        if perim > minPerim: 
            # add it to the array of detected hulls.
            hulls.append(hull)
            # calculate the final epsilon and use it to approximate the hull... we might skip this step depending on how well formed the hulls will be
            epsilon = eps/1000.0 * perim
            aprox = cv2.approxPolyDP(hull, epsilon, True)
            aproxHulls.append(aprox)
            # find the rotated bounding rectangle... again, we might skip this step depending on how well formed the hulls are.
            rect = cv2.minAreaRect(hull)
            rects.append(rect)
            
    # end the timer
    t = cv2.getTickCount() - t
    time = t / cv2.getTickFrequency() * 1000

    # time to draw on top of the original image....

    # draw all the detected hulls back on the original image (green with a width of 3)
    cv2.drawContours(drawnImage, hulls, -1, green, 3)

    # draw all the aproximated hulls (blue with a width of 1)
    cv2.drawContours(drawnImage, aproxHulls, -1, blue, 1) 

    # draw each rectangle (red with a width of 2)
    for rect in rects:
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(drawnImage, [box], 0, red, 2)

    # draw some text with status...
    text = 'Detect Time: %.0f ms' % (time)
    cv2.putText(drawnImage, text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
    text = 'Avg Pixel: %.0f' % (avg[0])
    cv2.putText(drawnImage, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
    text = '# Detections: %d' % (len(hulls))
    cv2.putText(drawnImage, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
    text = 'shutter speed: %d' % (ss)
    cv2.putText(drawnImage, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)

    # show the frame
    cv2.imshow(winName, drawnImage)

    # Important!  Clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
    # calculate the increment for the shutter speed by 1% of it's current value
    inc = 0
    if avg[0] > (autoShutter + 2):
        inc = -max(int(ss * 0.10), 2)  # if it's less than 2 use 2 
    if avg[0] < (autoShutter - 2):
        inc = max(int(ss * 0.10), 2)  # if it's less than 2 use 2 

    # print 'avg: %.0f, target value: %d, ss: %d, inc: %d' % (avg[0], autoShutter, ss, inc)

    # set the shutter speed
    camera.shutter_speed = ss + inc

    # get the key from the keyboard
    key = cv2.waitKey(1) & 0xFF
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
