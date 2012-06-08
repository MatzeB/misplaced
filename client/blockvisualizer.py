from visualizer import *

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

	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)

		obj.clientUpdate(dt)
