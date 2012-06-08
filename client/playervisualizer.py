from libs import pygl2d
from visualizer import *
from common.player import *

direction2RoationMap = {
	Direction.NoDir: 0,
	Direction.Left: 90,
	Direction.Right: 270,
	Direction.Up: 0,
	Direction.Down: 180
}

class PlayerVisualizer(Visualizer):

	def __init__(self, graphicfiles):
		Visualizer.__init__(self, graphicfiles)

	def getPosition(self, obj):
		return obj.position

	def getGraphicsKey(self, obj):
		return 0

	def getDirectionRotation(self, obj):
		direction = obj.currentDirection
		if direction == Direction.NoDir:
			direction = obj.lastDirection
		return direction2RoationMap[direction]
	
	def draw(self, offset, obj):
		if obj.visible:
			Visualizer.draw(self, offset, obj, rotation=self.getDirectionRotation(obj))

			direction = obj.currentDirection
			if direction == Direction.NoDir:
				direction = obj.lastDirection
			dirvector = direction_vectors[direction]
			targetpos = obj.position + Vector(16,16) + dirvector * 16 + offset

			pygl2d.draw.circle(targetpos.toIntArr(), 8, (255,0,0), 100)
	
	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)
		
		obj.clientUpdate(dt)