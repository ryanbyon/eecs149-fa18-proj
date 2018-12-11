# import the necessary packages
import numpy as np
import argparse
import cv2
from sklearn.cluster import KMeans
from projection import projection
from math import ceil

# MAGIC NUMBERS
WALL_THRESHOLD_DOWNSIZING = 80 # When downsizing the maze image to generate maze grid
WALL_THRESHOLD_UPSIZING = 0 # When upsizing, maze walls should already be 255 or 0

# Wall color thresholds
wall_lower_bgr = np.asarray([0, 0, 90])
wall_upper_bgr = np.asarray([55, 55, 180])

wall_color = [12, 12, 90]
RED = [0, 0, 255]

# Takes a raw image of the maze and outputs the pixel coordinates (row,col) of its four corners
#
# image: image of the maze
# corner_lower_bgr: numpy array of lower bounds for corner color
# corner_upper_bgr: numpy array of upper bounds for corner color
def detect_corners(image, corner_lower_bgr, corner_upper_bgr):
	green_mask = cv2.inRange(image, corner_lower_bgr, corner_upper_bgr)
	cv2.imwrite("YellowMask.png", green_mask)
	output = cv2.bitwise_and(image, image, mask = green_mask)
	green_corners = np.asarray(np.where(np.any(output != [0, 0, 0], axis=-1))).T

	# Use K-Means clustering to produce four coordinates for the corners
	kmeans = KMeans(n_clusters=4, random_state=0).fit(green_corners)

	# Sort in order upper_left, upper_right, lower_right, lower_left
	sum_centers = np.sum(kmeans.cluster_centers_, axis=1)
	sorted_indices = sum_centers.argsort()
	sorted_centers = np.take(kmeans.cluster_centers_, sorted_indices, axis=0)
	
	if sorted_centers[1][0] < sorted_centers[2][0]:
		sorted_centers[1], sorted_centers[2] = sorted_centers[2], sorted_centers[1]
		sorted_indices[1], sorted_indices[2] = sorted_indices[2], sorted_indices[1]

	for i in sorted_centers:
		i[0], i[1] = i[1], i[0]

	# Want min_x, min_y
	group0 = green_corners[np.where(kmeans.labels_ == sorted_indices[0])].T
	# Want min_x, max_y
	group1 = green_corners[np.where(kmeans.labels_ == sorted_indices[1])].T
	# Want max_x, min_y
	group2 = green_corners[np.where(kmeans.labels_ == sorted_indices[2])].T
	# Want max_x, max_y	
	group3 = green_corners[np.where(kmeans.labels_ == sorted_indices[3])].T

	result = np.zeros(shape=(4, 2))
	result[0] = np.asarray([np.min(group0[1]), np.min(group0[0])])
	result[1] = np.asarray([np.min(group1[1]), np.max(group1[0])])
	result[2] = np.asarray([np.max(group2[1]), np.min(group2[0])])
	result[3] = np.asarray([np.max(group3[1]), np.max(group3[0])])
	return result.astype(np.float32)

# Takes a projected image of the maze and outputs a downscaled image whose pixel values are 
# either [255, 255, 255] (white=wall is present) or [0, 0 0] (black=wall not present).
#
# Also pad the borders with some white.
#
# projected: projected image
# grid_width: desired width in grid squares
# grid_height: desired height in grid squares
# wall_threshold: threshold for detecting walls in the projected image
def gridify(projected, grid_width, grid_height, wall_threshold):
	projected = cv2.cvtColor(projected, cv2.COLOR_BGR2GRAY)
	threshed = cv2.threshold(projected, wall_threshold, 255, cv2.THRESH_BINARY)[1]

	downsized = cv2.resize(threshed, dsize = (grid_width, grid_height), interpolation=cv2.INTER_AREA)

	threshed_downsized = cv2.threshold(downsized, WALL_THRESHOLD_DOWNSIZING, 255, cv2.THRESH_BINARY)[1]
	return threshed_downsized

# Takes a projected image of the maze and outputs a downscaled image whose pixel values are 
# either [255, 255, 255] (white=wall is present) or [0, 0 0] (black=wall not present).
#
# Also pad the borders with some white. And make sure none of the pixels in the robot are set as walls
#
# projected: projected image
# downscale_factor: each square(this number) patch of the image becomes 1 grid square
# wall_threshold: threshold for detecting walls in the projected image
def gridify2(projected, downscale_factor, wall_threshold, robot_top_left=None, robot_bottom_right=None):
	BLACK = 0
	#projected = cv2.cvtColor(projected, cv2.COLOR_BGR2GRAY)
	#threshed = cv2.threshold(projected, wall_threshold, 255, cv2.THRESH_BINARY)[1]

	threshed = cv2.inRange(projected, wall_lower_bgr, wall_upper_bgr)
	cv2.imwrite("temp_walls.png", threshed)
	h, w = threshed.shape
	if robot_top_left is not None:
		robot_y_min = max(0, robot_top_left[1] - 10)
		robot_y_max = min(h , robot_bottom_right[1] + 10)
		robot_x_min = max(0, robot_top_left[0] - 10)
		robot_x_max = min(w , robot_bottom_right[0] + 10)
		threshed[robot_y_min:robot_y_max, robot_x_min:robot_x_max] = BLACK

	grid_height, grid_width = projected.shape[:2]
	downsized = cv2.resize(threshed, dsize = (grid_width//downscale_factor, grid_height//downscale_factor), interpolation=cv2.INTER_AREA)

	threshed_downsized = cv2.threshold(downsized, WALL_THRESHOLD_DOWNSIZING, 255, cv2.THRESH_BINARY)[1]
	cv2.imwrite("temp_walls_2.png", threshed_downsized)

	return threshed_downsized

# Takes the projected image of the maze and outputs this image, padded
# with a few white pixels so that both the height and width are divisible
# by desired_downscale_factor.
def pad_walls(projected, desired_downscale_factor):
	WHITE = [255, 255, 255]
	height, width = projected.shape[:2]
	target_height = closest_multiple(height, desired_downscale_factor)
	target_width = closest_multiple(width, desired_downscale_factor)
	height_diff, width_diff = target_height - height, target_width - width

	top, left = height_diff // 2, width_diff // 2
	bottom, right = height_diff - top, width_diff - left

	return cv2.copyMakeBorder(projected, top, bottom, left, right, cv2.BORDER_CONSTANT, value=wall_color)

# Overlays a downscaled grid onto a projected image of the maze.
#
# proj: projected image
# grid: downscaled grid
def overlay_visualize(proj, grid):
	upsized_grid = cv2.resize(grid, dsize = (proj.shape[1], proj.shape[0]), interpolation=cv2.INTER_NEAREST)
	upscale_factor = proj.shape[1] // grid.shape[1]
	threshed_upsized_grid = cv2.threshold(upsized_grid, WALL_THRESHOLD_UPSIZING, 255, cv2.THRESH_BINARY)[1]

	threshed_upsized_grid = cv2.cvtColor(threshed_upsized_grid, cv2.COLOR_GRAY2BGR)
	threshed_upsized_grid[np.where((threshed_upsized_grid == [255, 255, 255]).all(axis = 2))] = RED

	threshed_upsized_grid_png = eliminate_black_background(threshed_upsized_grid)
	projected_maze_png = add_alpha_channel(proj)

	overlay = cv2.addWeighted(projected_maze_png, 0.8, threshed_upsized_grid_png, 0.2, 0)
	overlay_grid_lines(overlay, upscale_factor)
	return overlay

# Takes in a 3-channel image and outputs a 4-channel image where the
# opacity of all black pixels [0, 0, 0] is 0 (made complete transparent)
def eliminate_black_background(image):
	_,alpha = cv2.threshold(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),0,255,cv2.THRESH_BINARY)
	b, g, r = cv2.split(image)
	rgba = [b,g,r, alpha]
	dst = cv2.merge(rgba,4)
	return dst

# Takes in a 3-channel image and outputs a 4-channel image where the
# opacity of all pixels is set to 255 (completely opaque)
def add_alpha_channel(image):
	b_channel, g_channel, r_channel = cv2.split(image)
	alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
	return cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

# Draws grid lines on an image
def overlay_grid_lines(image, upscale_factor):
	dx, dy = upscale_factor, upscale_factor

	# Custom (rgb) grid color
	grid_color = [0,0,0,255]

	# Modify the image to include the grid
	image[:,::dy,:] = grid_color
	image[::dx,:,:] = grid_color

# Return the smallest multiple of b larger than a, assuming a >> b
#
# Helps in padding borders with white
def closest_multiple(a, b):
	return ceil(a / b) * b
