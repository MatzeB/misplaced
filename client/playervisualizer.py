import time
from libs import pygl2d
from libs.pygl2d.font import RenderText
from visualizer import *
from blockvisualizer import *
from common.player import *
from pygame.color import Color
from math import *
from debug import DEBUG

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
		if obj.stunned:
			return 5
		elif obj.velocity.getLength() > 1:
			return int(time.time()*10%8+1)
		else:
			return 0

	def getDirectionRotation(self, obj):
		return direction2RoationMap[obj.getDirection()]

	def draw(self, offset, obj):
		if obj.visible:
			if not obj.stunned:
				self.graphics = self.spriteset.getWalkAnimationSprites(obj.getDirection())
			else:
				self.graphics = self.spriteset.getStunnedSprites()

            # If the player moves up, draw carried things first
			if obj.mostlyUp() and obj.carrying:
				self.carriedblockvisualizer.draw(offset, obj, rotation=self.getDirectionRotation(obj))

			Visualizer.draw(self, offset + Vector(0,-11.), obj, rotation=0)#self.getDirectionRotation(obj))

			if DEBUG:
				pygl2d.draw.circle(
					(obj.getTargetPosition() + offset).toIntArr(),
					8, (255,0,0), 100)
			if not obj.mostlyUp() and obj.carrying:
				self.carriedblockvisualizer.draw(offset, obj, rotation=self.getDirectionRotation(obj))

			self.drawName(offset, obj)

	def drawName(self, offset, obj):
		if not self.nameCache.has_key(obj.name):
			self.nameCache[obj.name] = RenderText(obj.name, Color("green"), self.font)

		textImg = self.nameCache[obj.name]
		textImg.draw(obj.position + offset + Vector(-textImg.get_width()/2, -32))

		if self.current_state == "warmup" and obj.evil is not None:
			img = self.goodAttitudeImage
			if obj.evil:
				img = self.evilAttitudeImage
			img.draw(obj.position + offset + Vector(-textImg.get_width()/2, -20))

	
	def clientUpdate(self, dt, obj, colldet):
		Visualizer.clientUpdate(self, dt, obj)
		
		obj.clientUpdate(dt, colldet)

