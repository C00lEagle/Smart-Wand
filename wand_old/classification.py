import cv2
import numpy as np

SZ = 50
CLASS_N = 10

def deskew(img):
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
# no deskewing needed.
        return img.copy()
# Calculate skew based on central momemts.
    skew = m['mu11']/m['mu02']
# Calculate affine transform to correct skewness.
    M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
# Apply affine transform
    img = cv2.warpAffine(img, M, (SZ, SZ), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
    return img

cv2.namedWindow("Main", cv2.WINDOW_NORMAL)

img = cv2.imread('wand_spell3.jpg', cv2.IMREAD_GRAYSCALE)
img = img[:,80:560]
img = cv2.resize(img, (SZ, SZ), interpolation = cv2.INTER_AREA)
cv2.imwrite('wand_spell3.jpg',img)
im2 = deskew(img)
cv2.imwrite('deskewed3.jpg',im2)
img = cv2.imread('deskewed3.jpg', cv2.IMREAD_GRAYSCALE)
cv2.imshow("Main", img)
cv2.waitKey(0)
cv2.destroyAllWindows()