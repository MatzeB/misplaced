import time
from libs import pygl2d
from visualizer import *
from blockvisualizer import *
from common.player import *

direction2RoationMap = {
	Direction.NoDir: 0,
	Direction.Left: 90,
	Direction.Right: 270,
	Direction.Up: 0,
	Direction.Down: 180
}

class CarriedBlock(BlockVisualizer):
    def __init__(self, tileset):
        BlockVisualizer.__init__(self, tileset)
    
    def getPosition(self, obj):
        return obj.getTargetPosition()

    def getGraphicsKey(self, obj):
        return obj.carrying

    def getGraphic(self, obj):
        return Visualizer.getGraphic(self, obj)


class PlayerVisualizer(Visualizer):

	def __init__(self, spriteset, tileset):
		Visualizer.__init__(self)
		self.spriteset = spriteset
		self.graphics = self.spriteset.getWalkAnimationSprites(Direction.Up)

		self.carriedblockvisualizer = CarriedBlock(tileset)

	def getPosition(self, obj):
		return obj.position

	def getGraphicsKey(self, obj):
		#print len(self.graphics)
		if obj.velocity.getLength() > 0:
			return int(time.clock()*10%8+1)
		else:
			return 0

	def getDirectionRotation(self, obj):
		direction = obj.currentDirection
		if direction == Direction.NoDir:
			direction = obj.lastDirection
		return direction2RoationMap[direction]

	def draw(self, offset, obj):
		if obj.visible:
			direction = obj.currentDirection
			if direction == Direction.NoDir:
				direction = obj.lastDirection
			dirvector = direction_vectors[direction]

			self.graphics = self.spriteset.getWalkAnimationSprites(direction)

			# move player image...
			Visualizer.draw(self, offset + Vector(16,0), obj, rotation=0)#self.getDirectionRotation(obj))

			targetpos = obj.position + Vector(16,16) + dirvector * 16 + offset

			pygl2d.draw.circle(
				(obj.getTargetPosition() + offset).toIntArr(),
				8, (255,0,0), 100)
			if obj.carrying:
				self.carriedblockvisualizer.draw(offset, obj, rotation=self.getDirectionRotation(obj))
	
	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)
		
		obj.clientUpdate(dt)

