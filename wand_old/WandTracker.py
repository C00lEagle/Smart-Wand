'''{ CAMERA PROPERTIES
'Model': 'ov5647', 'UnitCellSize': (1400, 1400),'ColorFilterArrangement': 2,
'Location': 2,'Rotation': 0,'PixelArraySize': (2592, 1944),
'PixelArrayActiveAreas': [(16, 6, 2592, 1944)],'ScalerCropMaximum': (0, 0, 0, 0),
'SystemDevices': (20748, 20738, 20739, 20740)
}'''
from picamera2 import Picamera2, Preview
import libcamera
import time
import cv2
import numpy as np


camera = Picamera2()
#print(camera.camera_properties)
#print(camera.sensor_modes)
config = camera.create_preview_configuration(main={"size": (640,480)}, display="main")
config["transform"] = libcamera.Transform(hflip=1)
camera.configure(config)
camera.set_controls({"AwbEnable":False, "Contrast":1, "Brightness":0, "ExposureValue":0, "AnalogueGain":1})
camera.start_preview(Preview.QTGL)


camera.start()
cv2.namedWindow("Main", cv2.WINDOW_NORMAL)
#cv2.setWindowProperty("Main", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    rgb_array = camera.capture_array("main") #capture rgb photo
    gray_array = cv2.cvtColor(rgb_array, cv2.COLOR_BGR2GRAY) #convert that photo into gray scale
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray_array) #find brightest point in the gray scale
    print("Brightest Point: " , maxLoc, maxVal) #print data
    cv2.circle(rgb_array, maxLoc, 5, (0, 0, 255), 2) #draw a circle around the brightest point
    cv2.imshow("Main", rgb_array) #Show image
time.sleep(5)
camera.stop()
camera.stop_preview()
destroyAllWindows()