from vector import *

class Direction:
	NoDir = 0
	Up = 1
	Left = 2
	Down = 3
	Right = 4

def randomDirection():
	return randint(Direction.Left, Direction.Down)

def directonToRotation(dir):
	if dir == Direction.Up:
		return 0
	else:
		return (dir - 1) * 90

direction_vectors = [
	Vector( 0, 0),
	Vector( 0, -1),
	Vector(-1, 0),
	Vector( 0,  1),
	Vector( 1, 0),
]
