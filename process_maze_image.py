# import the necessary packages
from math import ceil
import numpy as np
np.set_printoptions(threshold=np.nan)
import argparse
import cv2
# import bluetooth
import time
from sklearn.cluster import KMeans
from projection import projection
from image_utils import detect_corners, gridify, gridify2, overlay_visualize, pad_walls
from maze_utils import breadth_first_search, find_path, compute_wall_distances, create_direction_matrix, Direction

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
ap.add_argument("-r", "--robot", help = "path to the robot")
args = vars(ap.parse_args())
image = cv2.imread(args["image"])
robot = cv2.imread(args["robot"])

# Threshold values for maze corner detection (green)
lower =	np.array([140, 140, 0], dtype="uint8")
upper = np.array([230, 230, 60], dtype = "uint8")

# Desired resolution of projected image
# 91.3, 123.6 is REAL LIFE CM measurement
width, height = 130 * 6, 91 * 6
width, height = 1236, 913

# Desired resolution of maze grid
grid_width, grid_height = width // 13, height // 13

# Desired downscale factor from projected image to maze grid
# Units of MILLIMETERS SQUARED PER GRID SQUARE or 
# MILLIMETERS PER GRID SQUARE LENGTH
desired_downscale_factor = 20

# Threshold when processing raw projected maze image
wall_threshold = 210

sorted_centers = detect_corners(image, lower, upper)

projected = projection(args["image"], height, width, sorted_centers.astype(np.float32))
padded = pad_walls(projected, desired_downscale_factor)

# Find robot within padded
res = cv2.matchTemplate(robot, padded, cv2.TM_SQDIFF)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
top_left = min_loc
bottom_right = (min_loc[0] + robot.shape[1], min_loc[1] + robot.shape[0])
robot_center = ((top_left[0] + bottom_right[0])//2, (top_left[1] + bottom_right[1])//2)
robot_center_gridsquare = (robot_center[1] // desired_downscale_factor, robot_center[0] // desired_downscale_factor)
radius = ceil((bottom_right[0] - top_left[0]) / 2 / desired_downscale_factor)

cv2.imwrite("raw_projected.png", padded)

maze_grid = gridify2(padded, desired_downscale_factor, wall_threshold, top_left, bottom_right)
visualized_maze_grid = overlay_visualize(padded, maze_grid)

cv2.imwrite("projected_walls_grid_final.png", visualized_maze_grid)

bools = maze_grid.astype(bool)
distances_from_walls = np.empty(shape=maze_grid.shape, dtype="uint8")
directions_simple = np.zeros(shape=maze_grid.shape, dtype="uint8")
distances = np.full(maze_grid.shape, np.inf)

compute_wall_distances(bools, distances_from_walls)
cv2.imwrite("wall_distances_2.png", distances_from_walls * 28)
bools_buffered = distances_from_walls <= radius
breadth_first_search(bools_buffered, (6, 6), directions_simple, distances)
directions_smart = create_direction_matrix(bools_buffered, distances, distances_from_walls)

cv2.imwrite("distances2.png", distances)
cv2.imwrite("magic2.png", directions_smart)

path = find_path(robot_center_gridsquare, directions_smart)

path_modified = [str(el) if type(el) == int else str(el.value) for el in path]
 
# bd_addr = "00:14:03:06:75:C2" 
# port = 1
# sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
# sock.connect((bd_addr,port))

# index = 0
# while index < len(path_modified):
# 	sock.send(str(path_modified[index]))
# 	sock.send(str(path_modified[index+1]))
# 	time.sleep(1) # Wait for the car to finish the previous two steps
# 	index += 2

# sock.close()

print(path_modified)
