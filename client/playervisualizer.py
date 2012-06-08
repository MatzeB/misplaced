from visualizer import *

class PlayerVisualizer(Visualizer):

	def __init__(self, graphicfiles):
		Visualizer.__init__(self, graphicfiles)

	def getPosition(self, obj):
		return obj.position

	def getGraphicsKey(self, obj):
		return 0
	
	def draw(self, offset, obj):
		if obj.visible:
			Visualizer.draw(self, offset, obj)
	
	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)
		
		obj.clientUpdate(dt)