from libs.pygl2d.image import Image

class Tile:
	def __init__(self, image, (left, top, right, bottom)):
		self.image = image
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom
		self.color = (255.0,255.0,255.0)
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

# Initialize tileset
def make_tileset(filename, n_horizontal, n_vertical):
	image = Image(filename)
	image.ox = 0
	image.oy = 0
	tileset = []
	TILE_W = 32
	TILE_H = 32
	for s in range(4):
		for y in range(n_vertical):
				for x in range(n_horizontal/4):
					xp = s*4+x
					tile = Tile(image, (xp*TILE_W, y*TILE_H, (xp+1)*TILE_W, (y+1)*TILE_H))
					tileset.append(tile)

	return tileset
