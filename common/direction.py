from vector import *

class Direction:
	NoDir = 0
	Left = 1
	Right = 2
	Up = 3
	Down = 4

def randomDirection():
	return randint(Direction.Left, Direction.Down)

direction_vectors = [
	Vector( 0, 0),
	Vector(-1, 0),
	Vector( 1, 0),
	Vector( 0, -1),
	Vector( 0,  1),
]
