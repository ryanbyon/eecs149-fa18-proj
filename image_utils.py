# import the necessary packages
import numpy as np
import argparse
import cv2
from sklearn.cluster import KMeans
from projection import projection

# MAGIC NUMBERS
WALL_THRESHOLD_DOWNSIZING = 77 # When downsizing the maze image to generate maze grid
WALL_THRESHOLD_UPSIZING = 0 # When upsizing, maze walls should already be 255 or 0

RED = [0, 0, 255]

# Takes a raw image of the maze and outputs the pixel coordinates (row,col) of its four corners
#
# image: image of the maze
# corner_lower_bgr: numpy array of lower bounds for corner color
# corner_upper_bgr: numpy array of upper bounds for corner color
def detect_corners(image, corner_lower_bgr, corner_upper_bgr):
	green_mask = cv2.inRange(image, corner_lower_bgr, corner_upper_bgr)
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
		sorted_centers[2], sorted_centers[3] = sorted_centers[3], sorted_centers[2]

	for i in sorted_centers:
		i[0], i[1] = i[1], i[0]
	return sorted_centers

# Takes a projected image of the maze and outputs a downscaled image whose pixel values are 
# either [255, 255, 255] (white=wall is present) or [0, 0 0] (black=wall not present).
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

# Overlays a downscaled grid onto a projected image of the maze.
#
# proj: projected image
# grid: downscaled grid
def overlay_visualize(proj, grid):
	upsized_grid = cv2.resize(grid, dsize = (proj.shape[1], proj.shape[0]), interpolation=cv2.INTER_NEAREST)
	threshed_upsized_grid = cv2.threshold(upsized_grid, WALL_THRESHOLD_UPSIZING, 255, cv2.THRESH_BINARY)[1]

	threshed_upsized_grid = cv2.cvtColor(threshed_upsized_grid, cv2.COLOR_GRAY2BGR)
	threshed_upsized_grid[np.where((threshed_upsized_grid == [255, 255, 255]).all(axis = 2))] = RED

	threshed_upsized_grid_png = eliminate_black_background(threshed_upsized_grid)
	projected_maze_png = add_alpha_channel(proj)

	overlay = cv2.addWeighted(projected_maze_png, 0.8, threshed_upsized_grid_png, 0.2, 0)
	overlay_grid_lines(overlay)
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
def overlay_grid_lines(image):
	dx, dy = 13,13

	# Custom (rgb) grid color
	grid_color = [0,0,0,255]

	# Modify the image to include the grid
	image[:,::dy,:] = grid_color
	image[::dx,:,:] = grid_color