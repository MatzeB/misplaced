from blockvisualizer import *
from playervisualizer import *
from common.vector import *
from common.block import *
from tileset import make_tileset

class MapVisualizer:
	def __init__(self, mapdata, playerid, screenDim):
		self.map = mapdata
		self.playerid = playerid
		self.screenDim = screenDim

		self.tileset = make_tileset("data/tiles.png", 16, 16)
		self.blockvisualizer = BlockVisualizer(self.tileset)
		self.playervisualizer = PlayerVisualizer([
			"client/graphics/player_0.png",
			"client/graphics/player_1.png"
		])

		self.targetOffset = Vector(0,0)
		self.currentOffset = Vector(0,0)

	def setData(self, mapdata):
		self.map = mapdata # todo: interpolate

	def setUpdateData(self, mapupdate, pakettime):
		self.map.incrementalUpdate(mapupdate, pakettime)

	def draw(self):
		#print self.currentOffset
		for x in range(self.map.blocks_horizontal):
			if (x * self.blockvisualizer.blockWidth) < self.currentOffset.x: continue
			if (x * self.blockvisualizer.blockWidth) > self.currentOffset.x + self.screenDim.x: continue

			for y in range(self.map.blocks_vertical):
				if (y * self.blockvisualizer.blockHeight) < self.currentOffset.y: continue
				if (y * self.blockvisualizer.blockHeight) > self.currentOffset.y + self.screenDim.y: continue	
			
				background_block = self.map.background[x][y]
				if background_block.type != 0:
					self.blockvisualizer.draw(self.currentOffset, background_block)
				solid_block = self.map.blocks[x][y]
				if solid_block.type != 0:
					self.blockvisualizer.draw(self.currentOffset, solid_block)

		for id,player in self.map.players.iteritems():
			self.playervisualizer.draw(self.currentOffset, player)

	def clientUpdate(self, dt):
		for x in range(self.map.blocks_horizontal):
			for y in range(self.map.blocks_vertical):
				self.blockvisualizer.clientUpdate(dt, self.map.blocks[x][y])

		for id,player in self.map.players.iteritems():
			self.playervisualizer.clientUpdate(dt, player)

		#self.updateOffset(dt)

	def findPlayer(self):
		if self.map.players.has_key(self.playerid):
			return self.map.players[self.playerid]
		else:
			return None

	def updateOffset(self, dt):
		player = self.findPlayer()

		if player:
			self.targetOffset = -(player.position - self.screenDim/2)
			#print self.targetOffset
			if self.targetOffset.x > 0: self.targetOffset.x = 0
			if self.targetOffset.y > 0: self.targetOffset.y = 0
			#if self.targetOffset.x < -self.map.width: self.targetOffset.x = 0
			#if self.targetOffset.y > -self.map.height: self.targetOffset.y = 0

			self.currentOffset = (self.targetOffset - self.currentOffset) * dt
