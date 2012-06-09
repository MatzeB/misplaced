import pickle, base64
from block import *
from player import *
from common.vector import *

class Map:
	def __init__(self, blocks_horizontal, blocks_vertical, tileset):
		self.blocks = {}
		self.background = {}
		self.players = {}
		self.tileset = tileset

		self.width = blocks_horizontal * 32
		self.blocks_horizontal = blocks_horizontal
		self.height = blocks_vertical * 32
		self.blocks_vertical = blocks_vertical

		self.blocks = {}
		for x in range(self.blocks_horizontal):
			self.blocks[x] = {}
			self.background[x] = {}

	def getMapUpdate(self):
		mapupdate = MapUpdate()

		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				if self.background[x][y].isDirty:
					mapupdate.background.append(self.background[x][y])
					self.background[x][y].isDirty = False

				if self.blocks[x][y].isDirty:
					mapupdate.blocks.append(self.blocks[x][y])
					self.blocks[x][y].isDirty = False

		for id,player in self.players.iteritems():
			if player.isDirty:
				mapupdate.players.append(player)
				player.isDirty = False

		return mapupdate

	def findNearestBlockAt(self, list, position):
		result = None
		
		if position.x < 0 or position.x >= self.blocks_horizontal * TILE_WIDTH: return result
		if position.y < 0 or position.y >= self.blocks_vertical * TILE_HEIGHT: return result

		minDist = -1
		ix = int(position.x/TILE_WIDTH)
		iy = int(position.y/TILE_HEIGHT)
		for x in range(ix, ix+1):
			for y in range(iy, iy+1):
				block = list[x][y]
				dist = Vector.distance(block.getCenterPosition(), position)
				if minDist == -1 or dist < minDist:
					result = block
					minDist = dist

		return result

	def getTargetBlock(self, list, position, direction):
		dirvector = direction_vectors[direction]
		targetpos = position + Vector(32,32) + dirvector * 16

		return self.findNearestBlockAt(list, targetpos)

	def update(self, dt):
		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				self.blocks[x][y].update(dt)

		for id,player in self.players.iteritems():
			player.update(dt)

			if player.currentInteraction == Interaction.Destroy:
				block = self.getTargetBlock(self.blocks, player.position, player.currentDirection)
				
				if block and block.type != 0:
					player.updateInteraction(dt, block)
					if not block.isInteracting:
						block.isInteracting = True
						block.isDirty = True
				else:
					block = self.getTargetBlock(self.background, player.position, player.currentDirection)
					
					if block:
						player.updateInteraction(dt, block)
						if not block.isInteracting:
							block.isInteracting = True
							block.isDirty = True

			if player.currentInteraction == Interaction.PickUp:
				block = self.getTargetBlock(self.blocks, player.position, player.currentDirection)
                                player.updateInteraction(dt, block)

	def generate(self):
		for x in range(self.blocks_horizontal):
			self.blocks[x] = {}
			self.background[x] = {}
			for y in range(self.blocks_vertical):
				self.blocks[x][y] = Block(x,y)
				self.background[x][y] = Block(x,y)
				self.background[x][y].isBackground = True

	def addPlayer(self, player):
		self.players[player.id] = player

	def incrementalUpdate(self, data, packetTime):
		for block in data.blocks:
			self.blocks[block.x][block.y].setUpdateData(block, packetTime)
		
		for block in data.background:
			self.background[block.x][block.y].setUpdateData(block, packetTime)
		
		for player in data.players:
			if self.players.has_key(player.id):
				self.players[player.id].setUpdateData(player, packetTime)
			else:
				self.players[player.id] = player

	def serialize(self):
		result = "["
		result += str(self.blocks_horizontal)
		result += "|"
		result += str(self.blocks_vertical)
		result += "|"

		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				result += self.background[x][y].serialize() + "/"
		result += "|"

		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				result += self.blocks[x][y].serialize() + "/"
		result += "|"

		for id,player in self.players.iteritems():
			result += player.serialize() + "/"
		
		result += "]"

		return result

	@staticmethod
	def deserialize(strdata):
		parts = strdata[1:-1].split("|")
		strblocks_background = parts[2].split("/")
		strblocks_blocks = parts[3].split("/")
		strplayers = parts[4].split("/")
	
		result = Map(int(parts[0]), int(parts[1]), None)

		for b in strblocks_background:
			if len(b.strip()) > 0:
				block = Block.deserialize(b)
				result.background[block.x][block.y] = block

		for b in strblocks_blocks:
			if len(b.strip()) > 0:
				block = Block.deserialize(b)
				result.blocks[block.x][block.y] = block
			
		for p in strplayers:
			if len(p.strip()) > 0:
				player = Player.deserialize(p)
				result.players[player.id] = player

		return result

	def check_winning_condition(self):
		# Check if there is an "SOS" made out of wood on the map
		pattern = [
			1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1,
			1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0,
			1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1,
			0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1,
			1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1,
		]
		pattern_width = 11
		pattern_height = len(pattern)/pattern_width

		for y in range(self.blocks_vertical - pattern_height-1):
			for x in range(self.blocks_horizontal - pattern_width-1):
				found = True
				for py in range(pattern_height):
					if not found:
						break
					for px in range(pattern_width):
						is_wood   = self.blocks[x+px][y+py].type == self.tileset.wood
						need_wood = pattern[py*pattern_width + px] != 0
						if is_wood != need_wood:
							found = False
							break
				if found:
					return True

class MapUpdate:
	def __init__(self, blocks=None, background=None, players=None):
		self.blocks = blocks or []
		self.background = background or []
		self.players = players or []

	def hasData(self):
		return len(self.players) > 0 or len(self.blocks) > 0 or len(self.background) > 0

	def serialize(self):
		result = "["
		
		for b in self.blocks:
			result += b.serialize() + "/"

		result += "|"
		
		for b in self.background:
			result += b.serialize() + "/"

		result += "|"

		for p in self.players:
			result += p.serialize() + "/"

		result += "]"

		return result

	@staticmethod
	def deserialize(strdata):
		result = MapUpdate()

		parts = strdata[1:-1].split("|")
		strblocks = parts[0].split("/")
		strbackground = parts[1].split("/")
		strplayers = parts[2].split("/")

		for b in strblocks:
			if len(b.strip()) > 0:
				result.blocks.append(Block.deserialize(b))

		for b in strbackground:
			if len(b.strip()) > 0:
				result.background.append(Block.deserialize(b))
		
		for p in strplayers:
			if len(p.strip()) > 0:
				result.players.append(Player.deserialize(p))

		return result


