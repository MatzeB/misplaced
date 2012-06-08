import pickle, base64
from block import *

class Map:
	def __init__(self, blocks_horizontal, blocks_vertical):
		self.blocks = {}
		self.players = {}

		self.width = blocks_horizontal * 32
		self.blocks_horizontal = blocks_horizontal
		self.height = blocks_vertical * 32
		self.blocks_vertical = blocks_vertical

	def getMapUpdate(self):
		mapupdate = MapUpdate()

		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				if self.blocks[x][y].isDirty:
					mapupdate.blocks.append(self.blocks[x][y])
					self.blocks[x][y].isDirty = False

		for id,player in self.players.iteritems():
			if player.isDirty:
				mapupdate.players.append(player)
				player.isDirty = False

		return mapupdate


	def update(self, dt):
		for x in range(self.blocks_horizontal):
			for y in range(self.blocks_vertical):
				self.blocks[x][y].update(dt)

		for id,player in self.players.iteritems():
			player.update(dt)

	def generate(self):
		for x in range(self.blocks_horizontal):
			self.blocks[x] = {}
			for y in range(self.blocks_vertical):
				self.blocks[x][y] = Block(x,y)

		self.blocks[2][5].type = BlockType.Gras

	def addPlayer(self, player):
		self.players[player.id] = player

	def incrementalUpdate(self, data):
		# todo: interpolate
		for block in data.blocks:
			self.blocks[block.x][block.y].setUpdateData(block)
		
		for player in data.players:
			if self.players.has_key(player.id):
				self.players[player.id].setUpdateData(player)
			else:
				self.players[player.id] = player

	def serialize(self):
		data = pickle.dumps(self)
		result = base64.b64encode(data)
		return result

	@staticmethod
	def deserialize(strdata):
		data = base64.b64decode(strdata)
		return pickle.loads(data)

class MapUpdate:
	def __init__(self, blocks=[], players=[]):
		self.blocks = blocks
		self.players = players

	def hasData(self):
		return len(self.players) > 0 or len(self.blocks) > 0

	def serialize(self):
		result = "["
		
		for b in self.blocks:
			result += b.serialize() + "/"

		result += "|"

		for p in self.players:
			result += p.serialize() + "/"

		result += "]"
		#data = pickle.dumps(self)
		#result = base64.b64encode(data)
		return result

	@staticmethod
	def deserialize(strdata):
		#data = base64.b64decode(strdata)
		#return pickle.loads(data)

		result = MapUpdate()

		parts = strdata[1:-1].split("|")
		strblocks = parts[0].split("/")
		strplayers = parts[1].split("/")

		for b in strblocks:
			if len(b.strip()) > 0:
				result.blocks.append(Block.deserialize(b))
		
		for p in strplayers:
			if len(p.strip()) > 0:
				result.players.append(Player.deserialize(p))

		return result

