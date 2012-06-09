import re
import sys
from common.map import Map
from common.tileset import TileSet

def ident(scanner, token): return token
def number(scanner, token):
	if "." in token:
		return float(token)
	else:
		return int(token)
def lbrace(scanner, token): return "("
def rbrace(scanner, token): return ")"
def string(scanner, token): return token[1:-1]
def ttrue(scanner, token): return True
def tfalse(scanner, token): return False

scanner = re.Scanner([
	(r"[+-]?[0-9]+(\.[0-9]*)?", number),
	(r"[a-zA-Z_-]+", ident),
	(r'"[^"]*"', string),
	(r"\(", lbrace),
	(r"\)", rbrace),
	(r"\#t", ttrue),
	(r"\#f", tfalse),
	("\s+", None),
	])

def parse_map(input):
	def next_token():
		global i
		global token
		global tokens
		if i >= len(tokens):
			token = None
			return
		token = tokens[i]
		i += 1

	def parse_tilemap():
		width = None
		height = None
		tiles = None

		while True:
			if token == "(":
				next_token()
				if token == "width":
					next_token()
					width = token
					next_token()
					next_token()
				elif token == "height":
					next_token()
					height = token
					next_token()
					next_token()
				elif token == "tiles":
					next_token()
					tiles = []
					while token != ")":
						tiles.append(token)
						next_token()
				else:
					next_token()
					count = 1
					while count > 0:
						if token == "(":
							count += 1
						elif token == ")":
							count -= 1
						next_token()
			elif token == ")":
				next_token()
				break
			else:
				next_token()

		assert len(tiles) == width * height
		return (width,height,tiles)

	global i
	global tokens
	global remainder
	text = input.read()

	tokens, remainder = scanner.scan(text)
	i = 0
	
	next_token()
	map = None
	while True:
		if token == "(":
			next_token()
			if token == "tilemap":
				next_token()
				(width,height,tiles) = parse_tilemap()

				if map == None:
					tileset = TileSet(None, 16, 16)
					map = Map(width, height, tileset)
					map.generate()
					dest = map.background
				else:
					dest = map.blocks

				for y in range(height):
					for x in range(width):
						dest[x][y].type = tiles[y*width+x]

			else:
				next_token()
		elif token == None:
			break
		else:
			next_token()

	return map
