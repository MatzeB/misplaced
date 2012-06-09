from libs.pygl2d.image import Image

class Tile:
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

class TileSet:
	def __init__(self, filename, n_horizontal, n_vertical):
		if filename != None:
			image = Image(filename)
			image.ox = 0
			image.oy = 0
		else:
			image = None
		tiles = []
		TILE_W = 32
		TILE_H = 32
		self.raft = 4
		self.wood = 69
		solid_tiles = [ 64, 66, 68, 69, 72, 73, 76, 77,
			24, 25, 26,
			28, 29, 30,
			32, 33, 34,
			36, 37, 38,
			40, 41, 42,
			44, 45, 46,
			# TODO add more tiles as solid...
		]

		for s in range(4):
			for y in range(n_vertical):
					for x in range(n_horizontal/4):
						xp = s*4+x
						tile = Tile(image, (xp*TILE_W, y*TILE_H, (xp+1)*TILE_W, (y+1)*TILE_H))
						tiles.append(tile)
		for s in solid_tiles:
			tiles[s].solid = True
		self.tiles = tiles

	def __len__(self):
		return len(self.tiles)

	def __getitem__(self, key):
		return self.tiles[key]
