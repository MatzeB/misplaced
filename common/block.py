class BlockType:
	Dirt = 0
	Gras = 1
	Stone = 2

class Block:

	def __init__(self, x, y, t=BlockType.Dirt):
		self.x = x
		self.y = y
		self.previousType = t
		self.type = t
		self.isDirty = False

	def update(self, dt):
		pass
		#if self.type != self.previousType:
			#print self.type, self.previousType
			#self.previousType = self.type
			#self.isDirty = True

		#	print "block change"

	def clientUpdate(self, dt):
		pass

	def setUpdateData(self, data, packetTime):
		self.type = data.type

	def serialize(self):
		result = "[%s,%s,%s]" % (
			self.x,
			self.y,
			self.type
		)

		return result

	@staticmethod
	def deserialize(strdata):
		parts = strdata[1:-1].split(",")
		return Block(int(parts[0]), int(parts[1]), int(parts[2]))