import cv2
import bluetooth
from process_maze_image import generate_navigation_directions_from_image, send_path_on_bluetooth, find_path_for_robot_from_image_and_directions
from time import sleep

DONT_GO_LONGER_THAN = 10 # squares
sleeping = 0;
counter = 0;

def send_path_on_bluetooth(sock, path):
	for i, path_element in enumerate(path):		
		if i % 2 == 1:
			distanceToMove = round(path_element*0.6, 2)
			# sleeping = 2
		else:
			distanceToMove = round(path_element*1.1, 2)
			sleeping = 1.5
		tosend = str(distanceToMove)
		print(path_element, tosend, flush=True)
		sock.send(tosend)
		sleep(3.5)

def truncate_path(path):
	print("truncating this path: " + str(path))
	result = []
	for i, path_element in enumerate(path):
		if i % 2 == 0:
			result.append(path_element)
		else:
			if path_element > DONT_GO_LONGER_THAN:
				result.append(DONT_GO_LONGER_THAN)
				break
			else:
				result.append(path_element)
	return result

robot_image = cv2.imread("maze_images/magic_marker.jpg")

first_pic = cv2.imread("maze_images/current_maze.jpg")
# first_pic = cv2.imread("maze_images/current_maze.jpg")
directions_matrix, wall_booleans = generate_navigation_directions_from_image(first_pic, robot_image) # Also detect the destination!!
first_path = find_path_for_robot_from_image_and_directions(first_pic, robot_image, directions_matrix, wall_booleans)

# truncated_path = truncate_path(first_path)
print(first_path)

# connect bluetooth!
print("I'm sending the path...")
bd_addr = "00:14:03:06:75:C2" 
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr,port))


send_path_on_bluetooth(sock, first_path[:2])

count = 1
done = False
while not done:
	current_maze_picture = take_picture()
	current_path = find_path_for_robot_from_image_and_directions(current_maze_picture.copy(), robot_image.copy(), directions_matrix.copy(), wall_booleans)
	if len(current_path) == 0:
		break
	#if count > 4 or len(current_path) <= 2: # Only one degree-turn and forward-move
	#	done = True
	#current_path = truncate_path(current_path)
	send_path_on_bluetooth(sock, current_path[:2])
	count += 1
	print(counter)
	counter += 1
sock.close()
		


# bluetooth_receive()
# while True:
# 	image = take_picture()
# 	path = find_path_for_robot_from_image_and_directions(image, directions_matrix) # Project the image, locate the robot, get the path
# 	send_path_on_bluetooth(path)
# 	bluetooth_receive()
