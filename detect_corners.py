# import the necessary packages
import numpy as np
import argparse
import cv2

def dist(a, b):
	return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())

# load the image
image = cv2.imread(args["image"])



lower =	[200, 200, 200]
upper = [255, 255, 255]



# create NumPy arrays from the boundaries
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")

# find the colors within the specified boundaries and apply
# the mask
mask = cv2.inRange(image, lower, upper)
output = cv2.bitwise_and(image, image, mask = mask)

cv2.imwrite("white.png", output)
output = cv2.blur(output, (4,4))
cv2.imwrite("whiteblur.png", output)

# FINDING CORNERS 
filename = 'whiteblur.png'
img = cv2.imread(filename)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,3,0.04)

#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)

# Threshold for an optimal value, it may vary depending on the image.

img[dst>0.07*dst.max()]=[0,0,255]

B = np.where(dst>0.07*dst.max())
pts = [(B[0][i], B[1][i]) for i in range(len(B[0]))]
print(pts)

cv2.imshow('dst', img)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()