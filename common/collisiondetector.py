
class CollisionDetector:
	def __init__(self, mapdata):
		self.map = mapdata

	# Return list of objects something collides with
	# Assumes all invoved objects have a boundingBox() function
	def get_collisions(self, bbox):
		collisions = []
		# TODO: limit search to blocks around the player only
		allblocks = self.map.allBlocks()
		for block in allblocks:
			if not self.map.tileset[block.type].solid:
				continue
			if self.intersects(bbox, block.boundingBox()):
				collisions.append(block)

		#for other in self.map.players.values():
		#	if self.intersects(bbox, other.boundingBox()):
		#		collisions.append(other)

		return collisions

	def intersects(self, bbox0, bbox1):
		if bbox0[2] < bbox1[0] or bbox0[0] > bbox1[2]:
			return False
		if bbox0[3] < bbox1[1] or bbox0[1] > bbox1[3]:
			return False
		return True

class Collision:
	def __init__(self, block):
		self.block = block
