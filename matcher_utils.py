import numpy as np
import cv2
import math
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 10

# Return angle in degrees that the robot has rotated from facing LEFT in the maze
# as well as the top left and bottom right of the bounding box containing it
def find_robot_angle(robot_img=cv2.imread("maze_images/raw_robot2.png"), maze_img=cv2.imread("raw_projected.png")):
	img1 = cv2.cvtColor(robot_img, cv2.COLOR_BGR2GRAY)	# queryImage
	img2 = cv2.cvtColor(maze_img, cv2.COLOR_BGR2GRAY)		# trainImage
	# Initiate SIFT detector
	sift = cv2.xfeatures2d.SIFT_create()

	# find the keypoints and descriptors with SIFT
	kp1, des1 = sift.detectAndCompute(img1,None)
	kp2, des2 = sift.detectAndCompute(img2,None)

	FLANN_INDEX_KDTREE = 0
	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
	search_params = dict(checks = 50)

	flann = cv2.FlannBasedMatcher(index_params, search_params)

	matches = flann.knnMatch(des1,des2,k=2)

	# store all the good matches as per Lowe's ratio test.
	good = []
	for m,n in matches:
	    if m.distance < 0.7*n.distance:
	        good.append(m)
	
	src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
	dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

	M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
	
	matchesMask = mask.ravel().tolist()

	h,w = img1.shape
	pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	dst = cv2.perspectiveTransform(pts,M)

	img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
	draw_params = dict(matchColor = (0,255,0), # draw matches in green color
					   singlePointColor = None,
					   matchesMask = matchesMask, # draw only inliers
					   flags = 2)
	img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
	cv2.imwrite("lol.png", img3)
	plt.imshow(img3, 'gray'),plt.show()

	# Transformed upper left, transformed upper right.
	p2, q2 = dst[0][0], dst[3][0]
	dy = q2[1] - p2[1]
	dx = q2[0] - p2[0]

	dst = dst.reshape(4,2).T
	if dx > 0:
		angle = -1 * 180 / math.pi * math.atan(dy/dx)
	else:
		angle = 180 - 180 / math.pi * math.atan(dy/dx)

	min_x = np.min(dst[0]).astype(int)
	min_y = np.min(dst[1]).astype(int)
	max_x = np.max(dst[0]).astype(int)
	max_y = np.max(dst[1]).astype(int)
	top_left = (min_x, min_y)
	bottom_right = (max_x, max_y)
	return top_left, bottom_right, clip_to_range(angle)

# Clip the angle to [-180, 180]
def clip_to_range(angle):
	if -180 <= angle <= 180:
		return angle
	elif angle < -180:
		return 360 + angle
	else:
		return -360 + angle

# Angle to rotate first pair of points (a1, b1) to second pair (a2, b2) 
def get_angle(a1, a2, b1, b2):
	dy1, dx1 = b1[1] - a1[1], b1[0] - a1[0]
	dy2, dx2 = b2[1] - a2[1], b2[0] - a2[0]

	if dx1 > 0:
		angle1 = -1 * 180 / math.pi * math.atan(dy1/dx1)
	else:
		angle1 = 180 - 180 / math.pi * math.atan(dy1/dx1)
	angle1 = clip_to_range(angle1)
	if dx2 > 0:
		angle2 = -1 * 180 / math.pi * math.atan(dy2/dx2)
	else:
		angle2 = 180 - 180 / math.pi * math.atan(dy2/dx2)
	angle2 = clip_to_range(angle2)
	return clip_to_range(angle2 - angle1)
