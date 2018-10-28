# import the necessary packages
import numpy as np
import argparse
import cv2
from sklearn.cluster import KMeans
from projection import projection

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())

# load the image
image = cv2.imread(args["image"])

# Threshold values for color filtration
lower =	[200, 200, 200]
upper = [255, 255, 255]

# create NumPy arrays from the boundaries
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")

# find the colors within the specified boundaries and apply
# the mask
mask = cv2.inRange(image, lower, upper)
output = cv2.bitwise_and(image, image, mask = mask)

blurred_output = cv2.blur(output, (4,4))

#
# FINDING CORNERS 
#

img = blurred_output
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,3,0.04)

#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)

# Threshold for an optimal value, it may vary depending on the image.
candidate_corners = np.asarray(np.where(dst>0.07*dst.max())).T

#
# CLUSTERING CANDIDATE CORNERS
#

kmeans = KMeans(n_clusters=4, random_state=0).fit(candidate_corners)

# Sort in order upper_left, upper_right, lower_left, lower_right
sum_centers = np.sum(kmeans.cluster_centers_, axis=1)
sorted_indices = sum_centers.argsort()
sorted_centers = np.take(kmeans.cluster_centers_, sorted_indices, axis=0)
if sorted_centers[1][0] < sorted_centers[2][0]:
	sorted_centers[1], sorted_centers[2] = sorted_centers[2], sorted_centers[1]

# centers = np.asarray([[87, 130], [82, 276], [234, 107], [221, 318]])

projection(args["image"], 500, sorted_centers.astype(int))