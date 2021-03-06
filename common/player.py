import time
from rules import *
from vector import *
from direction import *
from block import BlockType
from client.soundconstants import Sounds
from libs.pygl2d.font import RenderText
import pygame.font
from pygame import Color

TILE_WIDTH = 32
TILE_HEIGHT = 32

class Interaction:
	NoInteraction = 0
	Destroy = 1
	Create = 2
	PickUp = 3

class Player:

	def __init__(self, onClient, id="", x=0, y=0):
		self.isOnClient = onClient
		self.id = id
		self.name = "unnamed"
		self.visible = False
		self.isDirty = False
		self.targetposition = None
		self.position = Vector(96,96)
		self.velocity = Vector(0,0)
		self.oldAccel = Vector(0,0)
		self.acceleration = Vector(0,0)
		self.movementAcceleration = 100
		self.currentInteraction = Interaction.NoInteraction
		self.currentInteractionBlockType = None
		self.carrying = None
		self.carryingDirection = Direction.Up
		self.voted_begin = False
		self.stunned = False
		self.stunTimer = None
		self.evil = None
		self.chattext = ""
	
	def stun(self):
		if not self.stunned:
			self.stunned = True
			self.isDirty = True
			self.currentInteraction = Interaction.NoInteraction
			self.stunTimer = time.time()

	def unStun(self):
		if self.stunned:
			self.stunned = False
			self.isDirty = True

	def reset(self):
		self.stunned = False
		self.carrying = None
		self.isDirty = True
        
	def getTargetPosition(self):
		targetpos = self.position + self.oldAccel.getNormalized() * 16.
		return targetpos

	# Just an approximation
	def getDirection(self):
		alpha = self.oldAccel.getAngle()
		if -3*pi/4 <= alpha <= -pi/4:
			return Direction.Left
		if pi/4 <= alpha <= 3*pi/4:
			return Direction.Right
		if -pi/4 <= alpha <= pi/4:
			return Direction.Down
		return Direction.Up

	def mostlyUp(self):
		alpha = self.oldAccel.getAngle()
		return not (-pi/2 <= alpha <= pi/2)

	def interact(self, interaction, setInteracting):
		if not self.stunned and setInteracting:
			if interaction == Interaction.Destroy:
				self.currentInteraction = interaction
			elif interaction == Interaction.Create:
				self.currentInteraction = interaction
			elif interaction == Interaction.PickUp:
				self.currentInteraction = interaction
		else:
			self.currentInteraction = Interaction.NoInteraction


	def move(self, direction, doMove):
		if self.stunned:
			if self.acceleration.getLength() > 0:
				self.oldAccel = self.acceleration
				self.acceleration = Vector(0,0)
			return

		if doMove:
			accel = self.movementAcceleration
		else:
			accel = 0

		if direction == Direction.Left or direction == Direction.Right:
			self.acceleration.x = 0
		else:
			assert direction == Direction.Up or direction == Direction.Down
			self.acceleration.y = 0

		self.acceleration += direction_vectors[direction] * accel
		if self.acceleration.getLength() > 0:
			self.oldAccel = Vector(self.acceleration)

		self.isDirty = True

	def interaction_destroy_dirt(self, dt, block):
		if self.isOnClient:
			#print block.type
			pass

	def interaction_pickup_block(self, dt, block):
		if self.carrying:
			if block.type == 0:
				block.type = self.carrying
				block.direction = addDirection(self.carryingDirection, self.getDirection())
				self.carrying = None
				block.isDirty = True
				self.isDirty = True
		else:
			self.carrying = block.type
			self.carryingDirection = subDirection(block.direction, self.getDirection())
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
		elif self.currentInteraction == Interaction.PickUp:
			self.currentInteractionBlockType = block.type
			self.interaction_pickup_block(dt, block)
		else:
			self.currentInteractionBlockType = None

	def update(self, dt, collision_detector):

		if self.stunned and self.stunTimer and time.time() > self.stunTimer + STUN_TIME:
			self.unStun()

		if self.velocity.getLength() < 0.01 and self.acceleration.getLength() < 0.01:
			return

		destvel = self.velocity + self.acceleration
		destpos = self.position + (destvel * dt)
		destbbox = (destpos.x-16., destpos.y-16.,
					destpos.x+16., destpos.y+16.)
		collisions = collision_detector.get_collisions(destbbox)
		if self in collisions:
			collisions.remove(self)
		if len(collisions) > 0:
			# calculate a push-out vector (assume we only collided with 1 thing)
			if False:
				collider = collisions[0]
				cbbox = collider.boundingBox()
				mybbox = self.boundingBox()
				pen_top = cbbox[2] - mybbox[0]
				pen_bottom = mybbox[2] - cbbox[0]
				pen_left = cbbox[3] - mybbox[1]
				pen_right = mybbox[3] - cbbox[1]
				pens = [
					(pen_top, Vector(0., 1.)),
					(pen_bottom, Vector(0., -1.)),
					(pen_left, Vector(1., 0)),
					(pen_right, Vector(-1., 0)),
				]
				pens.sort()
				print "Collision with %s" % str(collisions[0])
				self.velocity = pens[0][1] * (float(pens[0][0])*5.)
				print "Out velocity: %s" % self.velocity
			else:
				self.velocity *= -0.5
				self.velocity.clamp(5)
			self.acceleration = Vector(0, 0)
		else:
			self.velocity = destvel
			self.position = destpos
			assert self.boundingBox() == destbbox
			assert(len(collision_detector.get_collisions(self.boundingBox())) <= 1)
			self.velocity *= 0.1

		if self.velocity.getLength() < 0.001:
			self.velocity = Vector(0,0)
		self.velocity.clamp(200)

		self.isDirty = True

	def playSounds(self):
		if self.currentInteraction == Interaction.Destroy:
			if not Sounds.attackChannel or not Sounds.attackChannel.get_busy():
				Sounds.attackChannel = Sounds.attack.play()

	def clientUpdate(self, dt, collision_detector):
		self.update(dt, collision_detector)

		if self.targetposition:
			destpos = self.position + (self.targetposition - self.position) * dt
			if len(collision_detector.get_collisions(self.boundingBox())) <= 1:
				self.position = destpos
			else:
				self.position = self.targetposition

		self.playSounds()
	
	# Get (left,top,right,bottom) bounding box
	def boundingBox(self):
		return (self.position.x-16., self.position.y-16.,
		        self.position.x+16., self.position.y+16.)

	def setUpdateData(self, data, packetTime):
		self.name = data.name
		self.visible = data.visible
		self.targetposition = data.position + data.velocity * packetTime
		self.velocity = data.velocity
		self.acceleration = data.acceleration
		self.oldAccel = data.oldAccel
		self.movementAcceleration = data.movementAcceleration
		self.currentInteraction = data.currentInteraction
		self.currentInteractionBlockType = data.currentInteractionBlockType
		self.carrying = data.carrying
		self.carryingDirection = data.carryingDirection
		self.voted_begin = data.voted_begin
		self.stunned = data.stunned
		self.evil = data.evil

	def textupdate(self):
		text = self.name
		if self.chattext != "":
			text += ": %s" % self.chattext
		self.nametext.change_text(text)

	def serialize(self):
		result = "[%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s]" % (
			self.id,
			self.name,
			self.visible,
			self.position.serialize(),
			self.velocity.serialize(),
			self.acceleration.serialize(),
			self.oldAccel.serialize(),
			self.movementAcceleration,
			self.currentInteraction,
			self.currentInteractionBlockType,
			self.carrying,
			self.carryingDirection,
			self.voted_begin,
			self.stunned,
			self.evil
		)

		return result

	@staticmethod
	def deserialize(strdata):
		result = Player(True)
		
		parts = strdata[1:-1].split(",")

		result.id = parts.pop(0)
		result.name = parts.pop(0)
		result.visible = parts.pop(0) == "True"
		result.position = Vector.deserialize(parts.pop(0))
		result.velocity = Vector.deserialize(parts.pop(0))
		result.acceleration = Vector.deserialize(parts.pop(0))
		result.oldAccel = Vector.deserialize(parts.pop(0))
		result.movementAcceleration = float(parts.pop(0))
		result.currentInteraction = int(parts.pop(0))
		part = parts.pop(0)
		if part == "None": result.currentInteractionBlockType = None
		else: result.currentInteractionBlockType = int(part)
		part = parts.pop(0)
		if part == "None": result.carrying = None
		else: result.carrying = int(part)
		result.carryingDirection = int(parts.pop(0))
		result.voted_begin = parts.pop(0) == "True"
		result.stunned = parts.pop(0) == "True"
		part = parts.pop(0)
		if part == "None": result.evil = None
		else: result.evil = part == "True"

		return result
