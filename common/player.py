from vector import *

TILE_WIDTH = 32
TILE_HEIGHT = 32

class Interaction:
	NoInteraction = 0
	Destroy = 1
	Create = 2

class Direction:
	NoDir = 0
	Left = 1
	Right = 2
	Up = 3
	Down = 4

direction_vectors = [
	Vector( 0, 0),
	Vector(-1, 0),
	Vector( 1, 0),
	Vector( 0, -1),
	Vector( 0,  1),
]

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
		self.movementAcceleration = 200
		self.currentDirection = Direction.Up
		self.currentInteraction = Interaction.NoInteraction

	def interact(self, interaction, setInteracting):
		if setInteracting:
			if interaction == Interaction.Destroy:
				self.currentInteraction = interaction
			elif interaction == Interaction.Create:
				self.currentInteraction = interaction
		else:
			self.currentInteraction = Interaction.NoInteraction


	def move(self, direction, doMove):
		accel = self.movementAcceleration
		if not doMove:
			accel *= -1

		self.acceleration += direction_vectors[direction] * accel
		self.currentDirection = direction

		self.isDirty = True

	def update(self, dt):
		if self.velocity.getLength() > 0 or self.acceleration.getLength() > 0:
			self.velocity += self.acceleration
			self.position += self.velocity * dt
			self.velocity *= 0.1

			self.velocity.clamp(200)

			self.isDirty = True

	def clientUpdate(self, dt):
		self.update(dt)

		if self.targetposition:
			self.position += (self.targetposition - self.position) * dt

	def setUpdateData(self, data, packetTime):
		self.name = data.name
		self.visible = data.visible
		self.targetposition = data.position + data.velocity * packetTime
		self.velocity = data.velocity
		self.acceleration = data.acceleration
		self.movementAcceleration = data.movementAcceleration
		self.currentDirection = data.currentDirection
		self.currentInteraction = data.currentInteraction


	def serialize(self):
		result = "[%s,%s,%s,%s,%s,%s,%s,%s,%s]" % (
			self.id,
			self.name,
			self.visible,
			self.position.serialize(),
			self.velocity.serialize(),
			self.acceleration.serialize(),
			self.movementAcceleration,
			self.currentDirection,
			self.currentInteraction
		)

		return result

	@staticmethod
	def deserialize(strdata):
		result = Player()
		
		parts = strdata[1:-1].split(",")

		result.id = parts[0]
		result.name = parts[1]
		result.visible = parts[2] == "True"
		result.position = Vector.deserialize(parts[3])
		result.velocity = Vector.deserialize(parts[4])
		result.acceleration = Vector.deserialize(parts[5])
		result.movementAcceleration = float(parts[6])
		result.currentDirection = int(parts[7])
		result.currentInteraction = int(parts[8])

		return result