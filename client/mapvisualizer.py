from blockvisualizer import *
from playervisualizer import *
from common.vector import *
from common.block import *
from common.tileset import TileSet
from common.sprite import PlayerSpriteSet
from libs import pygl2d
from debug import DEBUG

class MapVisualizer:
	def __init__(self, mapdata, playerid, screenDim):
		self.map = mapdata
		self.playerid = playerid
		self.screenDim = screenDim

		self.tileset = TileSet("data/tiles.png", 16, 16)
		self.spriteset = PlayerSpriteSet("data/player.png", 9, 5)
		self.map.tileset = self.tileset
		self.blockvisualizer = BlockVisualizer(self.tileset)
		self.playervisualizer = PlayerVisualizer(self.spriteset, self.tileset)

		self.targetOffset = Vector(0,0)
		self.currentOffset = Vector(0,0)

	def setCurrentState(self, state):
		self.current_state = state
		self.blockvisualizer.current_state = state
		self.playervisualizer.current_state = state

	def setData(self, mapdata):
		self.map = mapdata # todo: interpolate
		self.map.tileset = self.tileset

	def setUpdateData(self, mapupdate, pakettime):
		self.map.incrementalUpdate(mapupdate, pakettime)

	def draw(self):
		for x in range(self.map.blocks_horizontal):
			if (x * self.blockvisualizer.blockWidth) < -self.currentOffset.x - TILE_WIDTH/2: continue
			if (x * self.blockvisualizer.blockWidth) > -self.currentOffset.x + self.screenDim.x + TILE_WIDTH/2: continue

			for y in range(self.map.blocks_vertical):
				if (y * self.blockvisualizer.blockHeight) < -self.currentOffset.y - TILE_HEIGHT/2: continue
				if (y * self.blockvisualizer.blockHeight) > -self.currentOffset.y + self.screenDim.y + TILE_HEIGHT/2: continue	
			
				background_block = self.map.background[x][y]
				if background_block.type != 0:
					self.blockvisualizer.draw(self.currentOffset, background_block)
					if DEBUG and self.tileset[background_block.type].solid:
						bbox = background_block.boundingBox()
						bbox = (bbox[0] + self.currentOffset.x,
							bbox[1] + self.currentOffset.y,
							bbox[2] + self.currentOffset.x,
							bbox[3] + self.currentOffset.y)
						pygl2d.draw.rect(bbox, (255, 0, 0), alpha=100)
				solid_block = self.map.blocks[x][y]
				if solid_block.type != 0:
					self.blockvisualizer.draw(self.currentOffset, solid_block)

		for id,player in self.map.players.iteritems():
			# Debug highlighting
			block = self.map.findNearestBlockAt(
			                                    self.map.background,
			                                    player.getTargetPosition())
			if block != None:# and DEBUG:
				px = block.x * self.blockvisualizer.blockWidth + self.currentOffset.x - TILE_WIDTH/2
				py = block.y * self.blockvisualizer.blockHeight + self.currentOffset.y - TILE_HEIGHT/2
				bbox = (px, py, px+TILE_WIDTH, py+TILE_HEIGHT)
				pygl2d.draw.rect(bbox, (255,255,255), alpha=100)

			# Debug highlighting for collision bounding box
			if DEBUG:
				bbox = player.boundingBox()
				bbox = (
					bbox[0] + self.currentOffset.x,
					bbox[1] + self.currentOffset.y,
					bbox[2] + self.currentOffset.x,
					bbox[3] + self.currentOffset.y)
				pygl2d.draw.rect(bbox, (0, 0, 255), alpha=100)
				
			self.playervisualizer.draw(self.currentOffset, player)

	def clientUpdate(self, dt):
		for x in range(self.map.blocks_horizontal):
			for y in range(self.map.blocks_vertical):
				self.blockvisualizer.clientUpdate(dt, self.map.blocks[x][y])

		for id,player in self.map.players.iteritems():
			self.playervisualizer.clientUpdate(dt, player, self.map.collision_detector)

		self.updateOffset(dt)

	def findPlayer(self):
		if self.map.players.has_key(self.playerid):
			return self.map.players[self.playerid]
		else:
			return None

	def updateOffset(self, dt):
		player = self.findPlayer()

		if player:
			self.targetOffset = -(player.position - self.screenDim/2)
			#if self.targetOffset.x > 0: self.targetOffset.x = 0
			#if self.targetOffset.y > 0: self.targetOffset.y = 0
			#if self.targetOffset.x < -self.map.width: self.targetOffset.x = 0
			#if self.targetOffset.y > -self.map.height: self.targetOffset.y = 0

			#self.currentOffset = self.targetOffset
			self.currentOffset += (self.targetOffset - self.currentOffset) * dt
