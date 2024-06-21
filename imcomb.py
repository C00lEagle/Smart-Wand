import cv2

img1 = cv2.imread('Lumos/L.jpg', cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread('Nox/N.jpg', cv2.IMREAD_GRAYSCALE)
img3 = cv2.imread('Incendio/I.jpg', cv2.IMREAD_GRAYSCALE)
img4 = cv2.imread('Alohomora/A.jpg', cv2.IMREAD_GRAYSCALE)
img5 = cv2.imread('Wingardium/W.jpg', cv2.IMREAD_GRAYSCALE)

im_v = cv2.vconcat([img1,img2,img3,img4,img5])
cv2.imwrite("train_spells2.jpg",im_v)