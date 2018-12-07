import picamera
from time import sleep
from cv2 import imread
camera = picamera.PiCamera()

def take_picture(save_to_path='maze_images/current_maze.jpg'):
	camera.start_preview()
	sleep(10)
	camera.capture(save_to_path)
	camera.stop_preview()
	
	return imread(save_to_path)
