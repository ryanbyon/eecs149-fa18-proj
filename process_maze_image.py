# import the necessary packages
from math import ceil
import numpy as np
np.set_printoptions(threshold=np.nan)
import argparse
import cv2
# import bluetooth
import time
from projection import projection
from image_utils import detect_corners, gridify, gridify2, overlay_visualize, pad_walls
from maze_utils import breadth_first_search, find_path, compute_wall_distances, create_direction_matrix, Direction, print_path
from matcher_utils import find_robot_angle

start = time.clock()
maze_image_filepath = "maze_images/current_maze.jpg"

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
ap.add_argument("-r", "--robot", help = "path to the robot")
args = vars(ap.parse_args())
image = cv2.imread(args["image"])
robot = cv2.imread(args["robot"]) # It's facing left

# Threshold values for maze corner detection (green)
lower =	np.array([130, 50, 50], dtype="uint8")
upper = np.array([200, 90, 120], dtype = "uint8")

# Desired resolution of projected image
# 91.3, 123.6 is REAL LIFE CM measurement
real_width, real_height = 687, 461 # Sixteenths of inches!!
SIXTEENTH_INCH_TO_CM = 2.54 / 16
DESIRED_PIXELS_PER_CM = 8
width, height = 130 * 6, 91 * 6
width, height = 1236, 913
width, height = round(SIXTEENTH_INCH_TO_CM * DESIRED_PIXELS_PER_CM * real_width), round(SIXTEENTH_INCH_TO_CM * DESIRED_PIXELS_PER_CM * real_height)

# Desired resolution of maze grid
grid_width, grid_height = width // 13, height // 13

# Desired downscale factor from projected image to maze grid
# Units of MILLIMETERS SQUARED PER GRID SQUARE or 
# MILLIMETERS PER GRID SQUARE LENGTH
desired_downscale_factor = 8

# Threshold when processing grayscaled projected maze image
wall_threshold = 210

def find_path_for_robot_from_image_and_directions(maze_image, robot_image, directions):
	start_findpath_time = time.clock()
	projected = projection(maze_image, height, width, detect_corners(maze_image, lower, upper))
	padded = pad_walls(projected, desired_downscale_factor)

	top_left, bottom_right, angle = find_robot_angle(robot_image, padded)
	robot_center = ((top_left[0] + bottom_right[0])//2, (top_left[1] + bottom_right[1])//2)
	robot_center_gridsquare = (robot_center[1] // desired_downscale_factor, robot_center[0] // desired_downscale_factor)

	path = find_path(robot_center_gridsquare, directions, angle)
	end_findpath_time = time.clock()
	print("Time to look at image and recompute path: " + str(end_findpath_time - start_findpath_time) + " seconds")
	return path

def send_path_on_bluetooth(path):
	return


def generate_navigation_directions_from_image(maze_image, robot_image):
	start_project_time = time.clock()
	sorted_centers = detect_corners(maze_image, lower, upper)

	projected = projection(maze_image, height, width, sorted_centers)
	padded = pad_walls(projected, desired_downscale_factor)
	end_project_time = time.clock()
	cv2.imwrite("raw_projected.png", padded)


	# Find robot within padded
	start_findrobot_time = time.clock()
	top_left, bottom_right, angle = find_robot_angle(robot_image, padded)
	print(top_left, bottom_right, angle, flush=True)

	end_findrobot_time = time.clock()
	robot_center = ((top_left[0] + bottom_right[0])//2, (top_left[1] + bottom_right[1])//2)
	robot_center_gridsquare = (robot_center[1] // desired_downscale_factor, robot_center[0] // desired_downscale_factor)
	radius = ceil((bottom_right[0] - top_left[0]) / 2 / desired_downscale_factor)

	# start_gridify_time = time.clock()
	maze_grid = gridify2(padded, desired_downscale_factor, wall_threshold, top_left, bottom_right)
	# end_gridify_time = time.clock()
	# cv2.imwrite("temp.png", maze_grid)

	bools = maze_grid.astype(bool)
	distances_from_walls = np.empty(shape=maze_grid.shape, dtype="uint8")
	directions_simple = np.zeros(shape=maze_grid.shape, dtype="uint8")
	distances = np.full(maze_grid.shape, np.inf)
	
	start_bfs_time = time.clock()
	compute_wall_distances(bools, distances_from_walls)

	bools_buffered = distances_from_walls <= radius
	breadth_first_search(bools_buffered, (50, 7), directions_simple, distances)
	directions_smart = create_direction_matrix(bools_buffered, distances, distances_from_walls)
	end_bfs_time = time.clock()

	print("Projecion and corner detection: " + str(end_project_time - start_project_time))
	print("Robot finding: " + str(end_findrobot_time - start_findrobot_time))
	print("BFS to find distances from walls, distances from every square, directions from every square: " + str(end_bfs_time - start_bfs_time))
	
	visualized_maze_grid = overlay_visualize(padded, bools_buffered.astype("uint8"))
	cv2.imwrite("projected_walls_grid_final.png", visualized_maze_grid)
	return directions_smart

	# cv2.imwrite("wall_distances_2.png", distances_from_walls * 28)
	
	# cv2.imwrite("distances2.png", distances)
	# cv2.imwrite("magic2.png", directions_smart)

	# path_modified = [str(el) if type(el) == int else str(el.value) for el in path]
	 
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

	
