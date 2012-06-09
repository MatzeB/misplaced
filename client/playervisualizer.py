import time
from libs import pygl2d
from libs.pygl2d.font import RenderText
from visualizer import *
from blockvisualizer import *
from common.player import *
from pygame.color import Color
from math import *

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

		self.nameCache = {}
		fontname = pygame.font.get_default_font()
		self.font = pygame.font.Font(fontname, 14)
		attitudeFont = pygame.font.Font(fontname, 12)
		self.evilAttitudeImage = RenderText("EVIL", Color("black"), attitudeFont)
		self.goodAttitudeImage = RenderText("GOOD", Color("white"), attitudeFont)

		self.current_state = "warmup"
		

	def getPosition(self, obj):
		return obj.position

	def getGraphicsKey(self, obj):
		#print len(self.graphics)
		if obj.velocity.getLength() > 0:
			return int(time.clock()*10%8+1)
		else:
			return 0

	def getDirection(self, obj):
		direction = obj.currentDirection
		if direction == Direction.NoDir:
			direction = obj.lastDirection
		return direction
	
	def getDirectionRotation(self, obj):
		return direction2RoationMap[self.getDirection(obj)]

	def draw(self, offset, obj):
		if obj.visible:
			direction = obj.currentDirection
			if direction == Direction.NoDir:
				direction = obj.lastDirection
			dirvector = direction_vectors[direction]

			self.graphics = self.spriteset.getWalkAnimationSprites(direction)

            # If the player moves up, draw carried things first
			if self.getDirection(obj) == Direction.Up and obj.carrying:
				self.carriedblockvisualizer.draw(offset, obj, rotation=self.getDirectionRotation(obj))

			# move player image...
			rot = 0
			if obj.stunned:
				rot = 180
			Visualizer.draw(self, offset + Vector(16,5), obj, rotation=rot)#self.getDirectionRotation(obj))

			targetpos = obj.position + Vector(16,16) + dirvector * 16 + offset

			pygl2d.draw.circle(
				(obj.getTargetPosition() + offset).toIntArr(),
				8, (255,0,0), 100)
			if self.getDirection(obj) != Direction.Up and obj.carrying:
				self.carriedblockvisualizer.draw(offset, obj, rotation=self.getDirectionRotation(obj))

			self.drawName(offset, obj)

	def drawName(self, offset, obj):
		if not self.nameCache.has_key(obj.name):
			self.nameCache[obj.name] = RenderText(obj.name, Color("green"), self.font)

		textImg = self.nameCache[obj.name]
		textImg.draw(obj.position + offset + Vector(-textImg.get_width()/2+16, -32))

		if self.current_state == "warmup" and obj.evil is not None:
			img = self.goodAttitudeImage
			if obj.evil:
				img = self.evilAttitudeImage
			#img.rotate(15)# + sin(time.clock()*100%(2*pi))*10)
			img.draw(obj.position + offset + Vector(-textImg.get_width()/2+16, -20))

	
	def clientUpdate(self, dt, obj):
		Visualizer.clientUpdate(self, dt, obj)
		
		obj.clientUpdate(dt)

