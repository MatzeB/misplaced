
class CollisionDetector:
	def __init__(self, mapdata):
		self.map = mapdata

	def update(self, dt):
		for player in self.map.players:
			collision = self.getCollision(player)
			if collision:
				player.collide(collision)

	def getCollision(self, player):
		collision = None

		for block in self.map.blocks:
			if self.intersects(player, block):
				collision = Collision(block)
				break

		return collision

	def intersects(self, player, block):
		return False # todo


class Collision:
	def __init__(self, block):
		self.block = block