import picamera
from time import sleep
from cv2 import imread
camera = picamera.PiCamera()

camera.contrast = 40

def take_picture(save_to_path='maze_images/current_maze.jpg'):
	camera.start_preview()
	
	x = input()
	camera.capture(save_to_path)
	camera.stop_preview()
	
	return imread(save_to_path)

def change(x):
	camera.contrast = x
