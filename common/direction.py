from vector import *

class Direction:
	NoDir = 0
	Up = 1
	Left = 2
	Down = 3
	Right = 4

def randomDirection():
	return randint(Direction.Up, Direction.Right)

def directonToRotation(dir):
	if dir == Direction.NoDir:
		return 0
	else:
		return (dir - 1) * -90

def addDirection(dir1, dir2):
	return ((dir1 - 1) + (dir2 - 1)) % 4 +1

def subDirection(dir1, dir2):
	return ((dir1 - 1) - (dir2 - 1)) % 4 +1

direction_vectors = {
	Direction.NoDir: Vector( 0, 0),
	Direction.Up: Vector( 0, -1),
	Direction.Left: Vector(-1, 0),
	Direction.Down: Vector( 0,  1),
	Direction.Right: Vector( 1, 0),
}
