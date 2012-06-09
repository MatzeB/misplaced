from common.vector import *

class BlockType:
	Dirt = 0
	Gras = 1
	Stone = 2

class Block:

	def __init__(self, x, y, t=BlockType.Dirt):
		self.x = x
		self.y = y
		self.type = t
		self.isInteracting = False
		self.isBackground = False

		# server properties
		self.isDirty = False
		
		# client properties
		self.previousType = t
		self.interactionIndex = 0

	def update(self, dt):
		pass
		#if self.type != self.previousType:
			#print self.type, self.previousType
			#self.previousType = self.type
			#self.isDirty = True

		#	print "block change"

	def getCenterPosition(self):
		return Vector(self.x,self.y) * 32

	def clientUpdate(self, dt):
		pass

	def setUpdateData(self, data, packetTime):
		self.type = data.type
		self.isInteracting = data.isInteracting
		self.isBackground = data.isBackground

	def serialize(self):
		result = "[%s,%s,%s,%s,%s]" % (
			self.x,
			self.y,
			self.type,
			self.isInteracting,
			self.isBackground
		)

		return result

	def boundingBox(self):
		p = self.getCenterPosition()
		return (p.x-16., p.y-16.,
		        p.x+16., p.y+16.)

	@staticmethod
	def deserialize(strdata):
		parts = strdata[1:-1].split(",")
		result = Block(int(parts[0]), int(parts[1]), int(parts[2]))
		result.isInteracting = parts[3] == "True"
		result.isBackground = parts[4] == "True"
		return result
