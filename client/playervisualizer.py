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
		return 0

	def getDirectionRotation(self, obj):
		direction = obj.currentDirection
		if direction == Direction.NoDir:
			direction = obj.lastDirection
		return direction2RoationMap[direction]

        def getTargetOffset(self, obj):
                direction = obj.currentDirection
                if direction == Direction.NoDir:
                        direction = obj.lastDirection
                dirvector = direction_vectors[direction]
                targetpos = Vector(16,16) + dirvector * 16
                return targetpos
	
	def draw(self, offset, obj):
		if obj.visible:
			self.graphics = self.spriteset.getWalkAnimationSprites(obj.currentDirection)

			Visualizer.draw(self, offset, obj, rotation=self.getDirectionRotation(obj))

			direction = obj.currentDirection
			if direction == Direction.NoDir:
				direction = obj.lastDirection
			dirvector = direction_vectors[direction]
			targetpos = obj.position + Vector(16,16) + dirvector * 16 + offset

			pygl2d.draw.circle(
                            (obj.getTargetPosition() + offset).toIntArr(),
                            8, (255,0,0), 100)
                        if obj.carrying:
                            self.carriedblockvisualizer.draw(offset, obj, rotation=self.getDirectionRotation(obj))
	
	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)
		
		obj.clientUpdate(dt)

