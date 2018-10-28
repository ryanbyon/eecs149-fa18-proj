import numpy as np
import skimage as sk
import skimage.io as skio
import cv2
from skimage.transform import ProjectiveTransform
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

# reference: 
# https://stackoverflow.com/questions/33283088/transform-irregular-quadrilateral-to-rectangle-in-python-matplotlib

# Intput: img_name, maze_size, corners
# Output: square image of maze with maze_size
# example: 
# corners = np.asarray([[122.71763273258648, 187.22917681441788], [121.03424257184611,353.32367267413537], [289.37325864588405, 160.85606429615194], [280.95630784218213, 397.65294690696538]])
corners = np.asarray([[87, 130], [82, 276], [234, 107], [221, 318]])

def projection(img_name, maze_size, corners):
	# Read in image:
	img = sk.img_as_float(skio.imread(img_name))
	skio.imshow(img)


	# Calculating Projective Transformation Matrix:
	t = ProjectiveTransform()
	source = np.asarray([[0,0], [0,maze_size], [maze_size, 0], [maze_size, maze_size]])
	if not t.estimate(source, corners): 
	    raise Exception("estimate failed")


	# Computing Transformed Maze:
	maze = np.zeros((maze_size, maze_size,3))

	for i in range(maze_size):
	    for j in range(maze_size):
	        new_t = np.matrix.round(t([i,j]))[0]
	        maze[i][j] = img[int(new_t[0])][int(new_t[1])]

	plt.imshow(maze)
	plt.show()

	return maze

# If you want to manually pick the four corners
def pick_corners(img):
	print('Pick 4 corners on the source img.')
	plt.imshow(img)
	pts = plt.ginput(4, timeout=0)   
	plt.close()

	print(pts)