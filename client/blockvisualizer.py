from visualizer import *
from math import *
from common.direction import *

class BlockVisualizer(Visualizer):

	def __init__(self, tileset):
		Visualizer.__init__(self)
		self.graphics = tileset
		self.blockWidth = 32
		self.blockHeight = 32

	def getPosition(self, obj):
		x = obj.x * self.blockWidth
		y = obj.y * self.blockHeight
		result = Vector(x,y)
		return result

	def getGraphicsKey(self, obj):
		return obj.type

	def getRotation(self,obj):
		return directonToRotation(obj.direction)

	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)

		obj.clientUpdate(dt)
		
		obj.interactionIndex += 180.0 * dt
		if obj.interactionIndex > 360:
			obj.interactionIndex = 0

	def draw(self, offset, obj, rotation=0):
		rot = rotation + self.getRotation(obj)
		Visualizer.draw(self, offset, obj, rot)

	def getGraphic(self, obj):
		result = Visualizer.getGraphic(self, obj)
		if obj.isInteracting:
			result.colorize(255,0,0)
			if not obj.isBackground:
				result.scale = 1.0 + round(sin(obj.interactionIndex/360.0 * (2*pi))/10.0 - 0.2, 2)
		else:
			result.colorize(255,255,255)
			result.scale = 1.0
		return result
