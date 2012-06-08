from libs.pygl2d.image import Image

class Tile:
	def __init__(self, image, (left, top, right, bottom)):
		self.image = image
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom

	def rotate(self, rotation):
		self.rotation = rotation

	def draw(self, pos, rotation=0):
		if not self.image:
			return
		self.image.rotate(rotation)
		self.image.draw_part(pos, (self.left, self.top, self.right, self.bottom))

# Initialize tileset
def make_tileset(filename, n_horizontal, n_vertical):
	image = Image(filename)
	tileset = []
	tileset.append(Tile(None, (0,0,0,0)))
	TILE_W = 32
	TILE_H = 32
	for y in range(n_vertical):
		for x in range(n_horizontal):
			tile = Tile(image, (x*TILE_W, y*TILE_H, (x+1)*TILE_W, (y+1)*TILE_H))
			tileset.append(tile)

	return tileset
