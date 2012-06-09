from vector import *
from block import BlockType

TILE_WIDTH = 32
TILE_HEIGHT = 32

class Interaction:
	NoInteraction = 0
	Destroy = 1
	Create = 2
        PickUp = 3

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

	def __init__(self, onClient, id="", x=0, y=0):
		self.isOnClient = onClient
		self.id = id
		self.name = "unnamed"
		self.visible = False
		self.isDirty = False
		self.targetposition = None
		self.position = Vector(0,0)
		self.velocity = Vector(0,0)
		self.acceleration = Vector(0,0)
		self.movementAcceleration = 100
		self.lastDirection = Direction.Up
		self.currentDirection = Direction.Up
		self.currentInteraction = Interaction.NoInteraction
		self.currentInteractionBlockType = None
                self.carrying = None

	def interact(self, interaction, setInteracting):
		if setInteracting:
			if interaction == Interaction.Destroy:
				self.currentInteraction = interaction
			elif interaction == Interaction.Create:
				self.currentInteraction = interaction
			elif interaction == Interaction.PickUp:
				self.currentInteraction = interaction
		else:
			self.currentInteraction = Interaction.NoInteraction


	def move(self, direction, doMove):
		accel = self.movementAcceleration
		if not doMove:
			accel *= -1

		self.acceleration += direction_vectors[direction] * accel

		if self.currentDirection == Direction.NoDir:
			self.lastDirection = self.currentDirection
			self.currentDirection = direction

		if self.acceleration.getLength() == 0:
			self.lastDirection = self.currentDirection
			self.currentDirection = Direction.NoDir

		self.isDirty = True

	def interaction_destroy_dirt(self, dt, block):
		if self.isOnClient:
			#print block.type
			pass

        def interaction_pickup_block(self, dt, block):
                if self.carrying:
                    print block.type
                    if block.type == 0:
                        block.type = self.carrying
                        self.carrying = None
                        block.isDirty = True
                        self.isDirty = True
                else:
                    self.carrying = block.type
                    block.type = 0
                    block.isDirty = True
                    self.isDirty = True
                self.currentInteraction = Interaction.NoInteraction


	def updateInteraction(self, dt, block):
		if not block:
			self.currentInteractionBlockType = None
			return

		if self.currentInteraction == Interaction.Destroy:
			self.currentInteractionBlockType = block.type
			
			#if block.type == BlockType.Dirt:
			self.interaction_destroy_dirt(dt, block)
                if self.currentInteraction == Interaction.PickUp:
                        self.currentInteractionBlockType = block.type
                        self.interaction_pickup_block(dt, block)
		else:
			self.currentInteractionBlockType = None

	def update(self, dt):
		if self.velocity.getLength() > 0 or self.acceleration.getLength() > 0:
			self.velocity += self.acceleration
			self.position += self.velocity * dt
			self.velocity *= 0.1

			if self.velocity.getLength() < 0.001:
				self.velocity = Vector(0,0)

			self.velocity.clamp(200)

			if self.position.x < 0:
				self.position.x = 0
				self.velocity.x *= -1
			if self.position.y < 0:
				self.position.y = 0
				self.velocity.y *= -1

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
		self.lastDirection = data.lastDirection
		self.currentDirection = data.currentDirection
		self.currentInteraction = data.currentInteraction
		self.currentInteractionBlockType = data.currentInteractionBlockType
                self.carrying = data.carrying


	def serialize(self):
		result = "[%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s]" % (
			self.id,
			self.name,
			self.visible,
			self.position.serialize(),
			self.velocity.serialize(),
			self.acceleration.serialize(),
			self.movementAcceleration,
			self.lastDirection,
			self.currentDirection,
			self.currentInteraction,
			self.currentInteractionBlockType,
                        self.carrying
		)

		return result

	@staticmethod
	def deserialize(strdata):
		result = Player(True)
		
		parts = strdata[1:-1].split(",")

		result.id = parts[0]
		result.name = parts[1]
		result.visible = parts[2] == "True"
		result.position = Vector.deserialize(parts[3])
		result.velocity = Vector.deserialize(parts[4])
		result.acceleration = Vector.deserialize(parts[5])
		result.movementAcceleration = float(parts[6])
		result.lastDirection = int(parts[7])
		result.currentDirection = int(parts[8])
		result.currentInteraction = int(parts[9])
		if parts[10] == "None": result.currentInteractionBlockType = None
		else: result.currentInteractionBlockType = int(parts[10])
		if parts[11] == "None": result.carrying = None
		else: result.carrying = int(parts[11])


		return result
