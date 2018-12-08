import cv2
# import bluetooth
from process_maze_image import generate_navigation_directions_from_image, send_path_on_bluetooth, find_path_for_robot_from_image_and_directions
# from camera import take_picture

robot_image = cv2.imread("maze_images/raw_robot2.png")

# first_pic = take_picture()
first_pic = cv2.imread("maze_images/maze5small.jpg")
directions_matrix = generate_navigation_directions_from_image(first_pic, robot_image) # Also detect the destination!!
first_path = find_path_for_robot_from_image_and_directions(first_pic, robot_image, directions_matrix)

print(first_path)
# send_path_on_bluetooth(first_path)
# bluetooth_receive()
# while True:
# 	image = take_picture()
# 	path = find_path_for_robot_from_image_and_directions(image, directions_matrix) # Project the image, locate the robot, get the path
# 	send_path_on_bluetooth(path)
# 	bluetooth_receive()
