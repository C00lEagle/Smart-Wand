#hog
import cv2
img = cv2.imread('deskewed.jpg', cv2.IMREAD_GRAYSCALE)

winSize = (50,50)
blockSize = (20,20)
blockStride = (10,10)
cellSize = (20,20)
nbins = 9
derivAperture = 1
winSigma = -1.
histogramNormType = 0
L2HysThreshold = 0.2
gammaCorrection = 1
nlevels = 64
signedGradients = True
 
hog = cv2.HOGDescriptor(winSize,blockSize,blockStride,cellSize,nbins,derivAperture,winSigma,histogramNormType,L2HysThreshold,gammaCorrection,nlevels,signedGradients)

descriptor = hog.compute(img)
print(descriptor)