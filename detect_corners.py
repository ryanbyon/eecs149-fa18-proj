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
green = [9, 174, 144]
lower =	[140, 140, 0]
upper = [230, 230, 60]

# create NumPy arrays from the boundaries
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")

# find the colors within the specified boundaries and apply
# the mask
mask = cv2.inRange(image, lower, upper)
output = cv2.bitwise_and(image, image, mask = mask)
cv2.imwrite("greencorners.png", output)

green_corners = np.asarray(np.where(np.any(output != [0, 0, 0], axis=-1))).T

kmeans = KMeans(n_clusters=4, random_state=0).fit(green_corners)

# Sort in order upper_left, upper_right, lower_left, lower_right
sum_centers = np.sum(kmeans.cluster_centers_, axis=1)
sorted_indices = sum_centers.argsort()
sorted_centers = np.take(kmeans.cluster_centers_, sorted_indices, axis=0)
if sorted_centers[1][0] < sorted_centers[2][0]:
	sorted_centers[1], sorted_centers[2] = sorted_centers[2], sorted_centers[1]
	sorted_centers[2], sorted_centers[3] = sorted_centers[3], sorted_centers[2]

for i in sorted_centers:
	i[0], i[1] = i[1], i[0]

projected = projection(args["image"], 91 * 6, 124 * 6, sorted_centers.astype(np.float32))
