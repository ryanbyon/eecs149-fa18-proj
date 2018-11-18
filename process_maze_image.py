# import the necessary packages
import numpy as np
np.set_printoptions(threshold=np.nan)
import argparse
import cv2
from sklearn.cluster import KMeans
from projection import projection
from image_utils import detect_corners, gridify, overlay_visualize
from maze_utils import breadth_first_search, find_path, compute_wall_distances, create_direction_matrix, Direction

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())
image = cv2.imread(args["image"])

# Threshold values for maze corner detection (green)
lower =	np.array([140, 140, 0], dtype="uint8")
upper = np.array([230, 230, 60], dtype = "uint8")

# Desired resolution of projected image
# 91.3, 123.6 is REAL LIFE CM measurement
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

bools = maze_grid.astype(bool)
distances_from_walls = np.empty(shape=maze_grid.shape, dtype="uint8")
directions_simple = np.zeros(shape=maze_grid.shape, dtype="uint8")
distances = np.full(maze_grid.shape, np.inf)

compute_wall_distances(bools, distances_from_walls)
breadth_first_search(bools, (40, 58), directions_simple, distances)
directions_smart = create_direction_matrix(bools, distances, distances_from_walls)

path = find_path((1, 1), directions_smart)
for e in path:
	print(e)
