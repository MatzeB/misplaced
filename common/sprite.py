from libs.pygl2d.image import Image
from common.direction import *

class PlayerSprite:
	def __init__(self, image, (left, top, right, bottom)):
		self.image = image
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom
		self.color = (255.0,255.0,255.0)
		self.solid = False
		self.scale = 1.0

	def colorize(self, r, g, b):
		self.color = (r, g, b)
	def scale(self, s):
		self.scale = s

	def draw(self, pos, rotation=0):
		self.image.colorize(self.color)
		self.image.scale(self.scale)
		self.image.rotate(rotation)
		self.image.draw_part(pos, (self.left, self.top, self.right, self.bottom))

class PlayerSpriteSet:
	def __init__(self, filename, n_horizontal, n_vertical):
		if filename != None:
			image = Image(filename)
			image.ox = 0
			image.oy = 0
		else:
			image = None

		TILE_W = 64
		TILE_H = 64

		sprites = []
		for y in range(n_vertical):
			for x in range(n_horizontal):
				sprite = PlayerSprite(image, (x*TILE_W, y*TILE_H, (x+1)*TILE_W, (y+1)*TILE_H))
				sprites.append(sprite)

		self.sprites = sprites

	def getStunnedSprites(self):
		return self.sprites[36:43]

	def getWalkAnimationSprites(self, direction):
		if direction == Direction.NoDir or direction == Direction.Left:
			return self.sprites[9:18]
		elif direction == Direction.Right:
			return self.sprites[27:36]
		elif direction == Direction.Up:
			return self.sprites[0:9]
		elif direction == Direction.Down:
			return self.sprites[18:27]

	def __len__(self):
		return len(self.sprites)

	def __getitem__(self, key):
		return self.sprites[key]
