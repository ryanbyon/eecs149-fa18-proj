# Search
import collections
import numpy as np
from enum import Enum
from matcher_utils import clip_to_range

class Direction(Enum):
	NOWHERE = 0
	LEFT = 63
	UP = 126
	RIGHT = 189
	DOWN = 252

	def opposite(self):
		if self == Direction.LEFT:
			return Direction.RIGHT
		elif self == Direction.RIGHT:
			return Direction.LEFT
		elif self == Direction.UP:
			return Direction.DOWN
		elif self == Direction.DOWN:
			return Direction.UP
		else:
			return Direction.NOWHERE

	# What angle (in degrees) to turn to face self from initial
	# Initial should be in [-180, 180]
	def turn_calculation(self, initial_angle_from_LEFT):
		angle_to_face_LEFT = -initial_angle_from_LEFT
		if self == Direction.LEFT:
			return angle_to_face_LEFT
		elif self == Direction.UP:
			return clip_to_range(-90 + angle_to_face_LEFT)
		elif self == Direction.RIGHT:
			return clip_to_range(180 + angle_to_face_LEFT)
		elif self == Direction.DOWN:
			return clip_to_range(90 + angle_to_face_LEFT)

	# What angle from LEFT is this direction?
	def angle_from_LEFT(self):
		if self == Direction.LEFT:
			return 0
		elif self == Direction.UP:
			return -90
		elif self == Direction.RIGHT:
			return 180
		elif self == Direction.DOWN:
			return 90

# Returns the valid neighboring grid squares
# paired with the DIRECTION to RETURN to the first square
def neighbors(point, grid):
	result = []
	y, x, height, width = point[0], point[1], grid.shape[0], grid.shape[1]
	if y > 0:
		result.append(((y-1, x), Direction.DOWN))
	if y < height-1:
		result.append(((y+1, x), Direction.UP))
	if x > 0:
		result.append(((y, x-1), Direction.RIGHT))
	if x < width-1:
		result.append(((y, x+1), Direction.LEFT))
	return result

def compute_wall_distances(grid, wall_distances):
	visited, queue = set(), collections.deque([])
	walls = grid.nonzero()
	for i in range(len(walls[0])):
		wall = (walls[0][i], walls[1][i])
		visited.add(wall)
		wall_distances[wall[0]][wall[1]] = 0
		queue.append(wall)
	while queue:
		vertex = queue.popleft()
		for adjacent, _ in neighbors(vertex, grid):
			if adjacent not in visited:
				visited.add(adjacent)
				queue.append(adjacent)
				wall_distances[adjacent[0]][adjacent[1]] = wall_distances[vertex[0]][vertex[1]] + 1

# Performs bfs on grid
# At the end, directions will be populated with elements in [0, 4]
# where 0 = this square is the destination
# 1 = go left to reach destination
# 2 = go up
# 3 = go right
# 4 = go down
def breadth_first_search(grid, dest, directions, distances): 
    visited, queue = set(), collections.deque([dest])
    directions[dest[0]][dest[1]] = Direction.NOWHERE.value
    distances[dest[0]][dest[1]] = 0
    visited.add(dest)
    while queue: 
        vertex = queue.popleft()
        for adjacent, direction_code in neighbors(vertex, grid):
            if adjacent not in visited and not grid[adjacent[0]][adjacent[1]]:
                visited.add(adjacent)
                queue.append(adjacent)
                directions[adjacent[0]][adjacent[1]] = direction_code.value
                distances[adjacent[0]][adjacent[1]] = distances[vertex[0]][vertex[1]] + 1

def create_direction_matrix(grid, distances, wall_distances):
	# Initialize as Direction.NOWHERE.value
	result = np.zeros(shape=grid.shape, dtype="uint8")
	for i in range(len(result)):
		for j in range(len(result[0])):
			if not grid[i][j] and distances[i][j] != 0:
				candidates = neighbors((i, j), grid)
				best_direction = min(candidates, key=lambda c: (distances[c[0][0]][c[0][1]], -wall_distances[c[0][0]][c[0][1]]))
				result[i][j] = best_direction[1].opposite().value
	return result

def find_path(source, directions, initial_angle):
	path = []
	curr = source
	# while we're not inside a wall or at the destination pointed to by directions
	while directions[curr[0]][curr[1]] != Direction.NOWHERE.value:
		direction = directions[curr[0]][curr[1]]
		path.append((direction, curr))
		if direction == Direction.LEFT.value:
			curr = (curr[0], curr[1]-1)
		elif direction == Direction.UP.value:
			curr = (curr[0]-1, curr[1])
		elif direction == Direction.RIGHT.value:
			curr = (curr[0], curr[1]+1)
		elif direction == Direction.DOWN.value:
			curr = (curr[0]+1, curr[1])

	return process_path(path, initial_angle)

# Input: [255, 255, 191]
# Output: [DONT_TURN, 2, TURN_LEFT, 1]
def process_path(path, initial_angle):
	result = []
	index, prev_dir = 0, Direction(path[0][0])
	result.append(prev_dir.turn_calculation(initial_angle))
	curr_runlength = 0
	while index < len(path):
		curr_dir = Direction(path[index][0])
		if curr_dir == prev_dir:
			curr_runlength += 1
		else:
			result.append(curr_runlength)
			curr_runlength = 1
			result.append(curr_dir.turn_calculation(prev_dir.angle_from_LEFT()))
			prev_dir = curr_dir
		index += 1
	result.append(curr_runlength)
	return result

def print_path(path):
	index = 0
	while (index < len(path)):
		print("Turn " + str(path[index]) + " degrees.")
		print("Go forward " + str(path[index + 1]) + " squares.")
		index += 2
