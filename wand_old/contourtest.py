import numpy as np
import cv2

drawn_path = cv2.imread("spells/Alohomora.png", cv2.IMREAD_GRAYSCALE)
existing_path = cv2.imread("spells/Lumos.png", cv2.IMREAD_GRAYSCALE)

#compare spell
drawn_contour, _ = cv2.findContours(drawn_path, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
existing_contour, _ = cv2.findContours(existing_path, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

drawn_hu_moments = cv2.HuMoments(cv2.moments(drawn_contour[0])).flatten()
existing_hu_moments = cv2.HuMoments(cv2.moments(existing_contour[0])).flatten()
    
similarity_score = cv2.matchShapes(drawn_contour[0], existing_contour[0], cv2.CONTOURS_MATCH_I1, 0)

# Calculate confidence percentage
confidence_percentage = 100 - (similarity_score * 100)
print(f"Confidence Percentage: {confidence_percentage:.2f}%")
    