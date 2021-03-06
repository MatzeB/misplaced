import pickle, base64
from block import *
from player import *
from common.vector import *
from common.collisiondetector import CollisionDetector

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

		self.collision_detector = CollisionDetector(self)

		self.blocks = {}
		for x in range(self.blocks_horizontal):
			self.blocks[x] = {}
			self.background[x] = {}

	def allBlocks(self):
		result = []
		#for row in self.blocks.values():
		#	for b in row.values():
		#		if b.type == 0:
		#			continue
		#		result.append(b)
		for row in self.background.values():
			for b in row.values():
				if b.type == 0:
					continue
				result.append(b)
		return result

	def allGroundBlocks(self):
		blocks = []
		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				if (not self.tileset.tiles[self.background[x][y].type].solid) and \
				   self.blocks[x][y].type == 0:
					   blocks.append(self.background[x][y])
		return blocks

	def placePlayer(self,player):
		groundBlocks = self.allGroundBlocks()
		s = randint(0,len(groundBlocks)-1)
		block = groundBlocks[s]
		player.position = block.getCenterPosition()
		print player.position
		player.isDirty = True

	def getMapUpdate(self, deltatime):
		mapupdate = MapUpdate(deltatime=deltatime)

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
		x = int(position.x/TILE_WIDTH + 0.5)
		y = int(position.y/TILE_HEIGHT + 0.5)
		if x in list and y in list[x]:
			return list[x][y]
		else:
			return None

	def findPlayerAt(self, position, excluded=None):
		minDist = 10000
		result = None
		for id, player in self.players.iteritems():
			if player != excluded:
				dist = Vector.distance(player.position, position)
				if dist < minDist:
					result = player
					minDist = dist

		if minDist < 16: # Target needs to be that close
			return result
		else:
			return None

	def update(self, dt):
		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				self.blocks[x][y].update(dt)

		for id,player in self.players.iteritems():
			player.update(dt, self.collision_detector)

			if player.currentInteraction == Interaction.Destroy:
				block = self.findNearestBlockAt(self.blocks, player.getTargetPosition())
				if block and block.type != 0:
					player.updateInteraction(dt, block)
					if not block.isInteracting:
						block.isInteracting = True
						block.isDirty = True
				else:
					victim = self.findPlayerAt(player.getTargetPosition(), player)

					if victim:
						if victim.stunned:	
							victim.unStun()
						else:
							victim.stun()
						player.currentInteraction = Interaction.NoInteraction
						player.isDirty = True

			if player.currentInteraction == Interaction.PickUp:
				block = self.findNearestBlockAt(self.blocks, player.getTargetPosition())
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
			self.blocks[block.x][block.y].setUpdateData(block, packetTime + data.deltatime)
		
		for block in data.background:
			self.background[block.x][block.y].setUpdateData(block, packetTime + data.deltatime)
		
		for player in data.players:
			if self.players.has_key(player.id):
				self.players[player.id].setUpdateData(player, packetTime + data.deltatime)
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
	def __init__(self, blocks=None, background=None, players=None, deltatime=0):
		self.blocks = blocks or []
		self.background = background or []
		self.players = players or []
		self.deltatime = deltatime

	def hasData(self):
		return len(self.players) > 0 or len(self.blocks) > 0 or len(self.background) > 0

	def serialize(self):
		result = "["

		result += str(self.deltatime)

		result += "|"
		
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
		result.deltatime = float(parts[0])
		strblocks = parts[1].split("/")
		strbackground = parts[2].split("/")
		strplayers = parts[3].split("/")

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


