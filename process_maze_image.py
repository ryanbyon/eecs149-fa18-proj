# import the necessary packages
import numpy as np
import argparse
import cv2
from sklearn.cluster import KMeans
from projection import projection
from image_utils import detect_corners, gridify, overlay_visualize

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())
image = cv2.imread(args["image"])

# Threshold values for maze corner detection (green)
lower =	np.array([140, 140, 0], dtype="uint8")
upper = np.array([230, 230, 60], dtype = "uint8")

# Desired resolution of projected image
width, height = 130 * 6, 91 * 6

# Desired resolution of maze grid
grid_width, grid_height = width // 13, height // 13

# Threshold when processing raw projected maze image
wall_threshold = 210

sorted_centers = detect_corners(image, lower, upper)

projected = projection(args["image"], height, width, sorted_centers.astype(np.float32))

maze_grid = gridify(projected, grid_width, grid_height, wall_threshold)
visualized_maze_grid = overlay_visualize(projected, maze_grid)

cv2.imwrite("projected_walls_grid_final.png", visualized_maze_grid)