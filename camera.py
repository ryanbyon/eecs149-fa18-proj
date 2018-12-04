import picamera
from time import sleep
camera = picamera.PiCamera()

camera.start_preview()
sleep(5)
camera.capture('maze_images/current_maze.jpg')
camera.stop_preview()
print('Done')
