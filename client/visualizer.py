import pygame
from libs import pygl2d
from common.vector import *

class Visualizer:

	def __init__(self, graphicfiles=None):
		self.graphicfiles = graphicfiles or []
		self.graphics = []

		for strfile in self.graphicfiles:
			self.graphics.append(pygl2d.image.Image(strfile))

	def getPosition(self, obj):
		return Vector(0,0)

	def getGraphicsKey(self, obj):
		return 0

	def getGraphic(self, obj):
		key = self.getGraphicsKey(obj)
		if key < 0 or key >= len(self.graphics):
			return None
		else:
			return self.graphics[key]

	def draw(self, offset, obj, rotation=0):
		p = self.getPosition(obj)
		graphic = self.getGraphic(obj)
		if graphic:
			graphic.draw((p + offset).toIntArr(), rotation)
	
	def clientUpdate(self, dt, obj):
		pass
