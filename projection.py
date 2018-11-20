import numpy as np
import cv2

import warnings
warnings.filterwarnings('ignore')

# reference: 
# https://stackoverflow.com/questions/33283088/transform-irregular-quadrilateral-to-rectangle-in-python-matplotlib

# Intput: img_name, maze_size, corners
# Output: square image of maze with maze_size
# example: 
	# corners = np.asarray([[122.71763273258648, 187.22917681441788], [121.03424257184611,353.32367267413537], [289.37325864588405, 160.85606429615194], [280.95630784218213, 397.65294690696538]])
	# projection("corners.jpg", 100, corners)

def projection(img_name, width, height, corners):
	# Read in image:
	img = cv2.imread(img_name)

	# Calculating Projective Transformation Matrix:
	print(corners)
	source = np.array([[0,0], [0,width], [height, 0], [height, width]], dtype = "float32")
	M = cv2.getPerspectiveTransform(corners, source)
	final = cv2.warpPerspective(img, M, (height, width))

	cv2.imshow("final", final)
	cv2.waitKey(0)

	return final

