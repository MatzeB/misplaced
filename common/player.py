from vector import *

class Direction:
	Left = 0
	Right = 1
	Up = 2
	Down = 3

class Player:

	def __init__(self, id="", x=0, y=0):
		self.id = id
		self.name = "unnamed"
		self.visible = False
		self.isDirty = False
		self.targetposition = None
		self.position = Vector(0,0)
		self.velocity = Vector(0,0)
		self.acceleration = Vector(0,0)
		self.movementAcceleration = 2

	def move(self, direction, doMove):
		accel = self.movementAcceleration
		if not doMove:
			accel = 0

		if direction == Direction.Left:
			self.acceleration = Vector(-accel,0)
		elif direction == Direction.Right:
			self.acceleration = Vector(accel,0)
		elif direction == Direction.Up:
			self.acceleration = Vector(0,-accel)
		elif direction == Direction.Down:
			self.acceleration = Vector(0,accel)
		self.isDirty = True

	def update(self, dt):
		if self.velocity.getLength() > 0 or self.acceleration.getLength() > 0:
			self.position += self.velocity * dt
			self.velocity += self.acceleration
			self.velocity *= 0.8

			self.isDirty = True

	def clientUpdate(self, dt):
		if self.targetposition:
			self.position += (self.targetposition - self.position) * dt

	def setUpdateData(self, data):
		self.name = data.name
		self.visible = data.visible
		self.velocity = data.velocity
		self.acceleration = data.acceleration
		self.movementAcceleration = data.movementAcceleration
		self.targetposition = data.position


	def serialize(self):
		result = "[%s,%s,%s]" % (
			self.id,
			self.name,
			self.visible,
			self.position,
			self.velocity,
			self.acceleration,
			self.movementAcceleration
		)

		return result

	@staticmethod
	def deserialize(strdata):
		result = Player()
		
		parts = strdata[1:-1].split(",")

		self.id = parts[0]
		self.name = parts[1]
		self.visible = parts[2] == True
		self.position = Vector.deserialize(parts[3])
		self.velocity = Vector.deserialize(parts[4])
		self.acceleration = Vector.deserialize(parts[5])
		self.movementAcceleration = float(parts)

		return result