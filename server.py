#!/usr/bin/env python
import socket, time
import random
from sys import exit
from random import *
from common.map import *
from common.player import *
from common.rules import *
from mapparse import parse_map
import sys

if sys.platform == 'win32':
	from errno import WSAEWOULDBLOCK as EWOULDBLOCK
else:
	from errno import EWOULDBLOCK

HOST = ''
PORT = 12345

UPDATE_INTERVALL = 1.0/30.0
SEND_INTERVALL = 0.1

# Game state
mapname = "data/test.stl"
if len(sys.argv) > 1:
	mapname = sys.argv[1]
mapdata = None
state = "warmup"
startTime = None
n_votebegin = 0

class Client:
	def __init__(self, conn, addr):
		self.inactive = False
		self.name = "Unnamed"
		self.conn = conn
		self.addr = addr
		self.partialdata = ""

	def __str__(self):
		return "%s(%s)" % (self.name, self.addr)

def my_sendall(s, data):
	# Python on BSD, OS/X or in nonblocking mode may raise EAGAIN even
	# for the sendall call, retry in this case
	sent = 0
	while sent < len(data):
		try:
			lsent = s.send(data[sent:])
		except socket.error as e:
			if e.errno == EWOULDBLOCK:
				continue
			raise e
		
		if lsent == 0:
			raise RuntimeError("client dropped")
		sent += lsent

class Server:
	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((HOST, PORT))
		self.s.listen(1)
		self.s.setblocking(0)

		self.clients = []
		self.reloadMap()
	
	def reloadMap(self):
		global mapdata
		oldmapdata = mapdata
		mapdata = parse_map(open(mapname))
		if oldmapdata:
			mapdata.players = oldmapdata.players
		for player in mapdata.players.values():
			player.reset()
			mapdata.placePlayer(player)

		data = mapdata.serialize()
		print "Sending map (%d bytes)" % len(data)
		self.sendall("mapdata " + data)

	def sendall(self, text):
		for client in self.clients:
			self.send(client, text)

	def send(self, client, text):
		if client.inactive:
			return
		try:
			fine = my_sendall(client.conn, text + "\n")
		except Exception as e:
			print "Send to client %s failed (%s), dropping" % (client, e)
			self._drop_client(client)

	def _drop_client(self, client):
		client.inactive = True
		if hasattr(self, "left"):
			method = getattr(self, "left")
			method(client)

	def process_network(self):
		# Accept new clients
		try:
			newclient = self.s.accept()
			if newclient != None:
				(conn, addr) = newclient
				conn.setblocking(0)
				print "Connect by ", addr
				client = Client(conn, addr)
				client.id = str(len(self.clients))
				self.clients.append(client)
				if hasattr(self, "joined"):
					method = getattr(self, "joined")
					method(client)
		except socket.error as e:
			pass

		# Handle existing clients
		for client in self.clients:
			if client.inactive:
				continue

			try:
				data = client.conn.recv(4096)
				if not data:
					print "Receiving from client %s failed, dropping" % client
					self._drop_client(client)
					continue
				data = client.partialdata + data
			except socket.error as e:
				if e.errno == 10054:
					print "Receiving from client %s failed with 10054" % client
					self._drop_client(client)
				continue

			commandlines = data.split("\n")
			if not data[-1] == "\n":
				client.partialdata = commandlines.pop()
			else:
				client.partialdata = ""

			for line in commandlines:
				if line == "":
					continue
				(command,_,args) = line.partition(" ")
				print "%s: %s" % (client, command)
				if hasattr(self, command):
					method = getattr(self, command)
					method(client, args)
				else:
					print "%s: Unknown server command '%s'" % (client, command)

if __name__ == "__main__":
	global server
	server = Server()
	print "Server running"

	# ====================================================================================================
	# =======================           Game Functions                         ===========================
	# ====================================================================================================
	
	def sendMapUpdate(mapupdate):
		global server
		server.sendall("mapdataupdate " + mapupdate.serialize())

	def sendPlayerUpdate(client):
		mapupdate = MapUpdate(players=[client.player])
		sendMapUpdate(mapupdate)

	def setGameState(server, newState):
		global state
		state = newState
		server.sendall("state %s" % state)
		if state == "game":
			global startTime 
			server.reloadMap()
			startTime = time.time()

	def gameupdate(server, dt):
		global state
		mapdata.update(dt)
		if state == "game":
			game_is_won = mapdata.check_winning_condition()
			if game_is_won:
				print "You created the SOS, help will be here soon"
				server.sendall("winner nice")
				setGameState(server, "warmup")
			game_is_lost = check_losing_condition()
			if game_is_lost:
				print "You ran out of time, help will be here soon"
				server.sendall("winner evil")
				setGameState(server, "warmup")

	def sendgameupdate(server, deltatime):
		mapupdate = mapdata.getMapUpdate(deltatime)

		if mapupdate.hasData():
			sendMapUpdate(mapupdate)

	# ====================================================================================================
	# =======================           Network Functions                      ===========================
	# ====================================================================================================

	def say(client, text):
		global server
		server.sendall("say %s|%s" % (client.player.id, text))

	def sendmap(client, text):
		global server
		data = mapdata.serialize()
		print "Sending map (%d bytes)" % len(data)
		server.send(client, "mapdata " + data)

	def name(client, newname):
		global server

		client.name = newname
		client.player.name = newname
		client.player.visible = True
		client.player.isDirty = True

	def abort(client, args):
		global server
		print "%s send abort game" % str(client)
		server.sendall("abort")

	def joined(client):
		player = Player(str(client.id), randint(0,mapdata.width), randint(0,mapdata.height))
		player.client = client
		mapdata.addPlayer(player)
		mapdata.placePlayer(player)
		if state == "game":
			player.evil = randint(0,2) == 0
		client.player = player

		server.send(client, "welcome " + str(client.player.id))
		data = mapdata.serialize()
		print "Sending map (%d bytes)" % len(data)
		server.send(client, "mapdata " + data)
		print "publising gamestate"
		server.send(client, "state %s" % state)


	def left(client):
		global server
		player = client.player
		if mapdata.players.has_key(player.id):
			del mapdata.players[player.id]
		server.sendall("left %s" % player.id)

	def player_command_right(client, doit):
		client.player.move(Direction.Right, doit == "True")

	def player_command_left(client, doit):
		global server
		client.player.move(Direction.Left, doit == "True")

	def player_command_up(client, doit):
		client.player.move(Direction.Up, doit == "True")

	def player_command_down(client, doit):
		client.player.move(Direction.Down, doit == "True")

	def player_command_destroy(client, doit):
		client.player.interact(Interaction.Destroy, doit == "True")

	def player_command_pickup(client, doit):
		client.player.interact(Interaction.PickUp, doit == "True")

	def player_command_create(client, doit):
		client.player.interact(Interaction.Create, doit == "True")

	def startround():
		global server
		global n_votebegin

		# Decide which players are 'evil'
		nice_players = list(mapdata.players.values())
		n_evil = len(nice_players)/3
		for i in range(n_evil):
			s = randint(0, len(nice_players)-1)
			evil = nice_players[s]
			nice_players.remove(evil)
			evil.evil = True

		for nice in nice_players:
			nice.evil = False

		for player in mapdata.players.values():
			player.voted_begin = False
			player.isDirty = True
		n_votebegin = 0

		setGameState(server, "game")
		print "Round begins"
	
	def check_losing_condition():
		global server
		if startTime:
			return time.time() > startTime + ROUND_TIME

	def votebegin(client, text):
		global n_votebegin
		if state != "warmup":
			return
		if client.player.voted_begin:
			return
		client.player.voted_begin = True
		client.player.isDirty = True
		n_votebegin += 1

		if n_votebegin == len(mapdata.players):
			startround()
		else:
			server.sendall("voteresult %s/%s" % (n_votebegin, len(mapdata.players)))

	def ping(client, number):
		global server
		server.send(client, "pong " + str(number))

	server.say = say
	server.sendmap = sendmap
	server.name = name
	server.abort = abort
	server.joined = joined
	server.left = left
	server.player_command_right = player_command_right
	server.player_command_left = player_command_left
	server.player_command_up = player_command_up
	server.player_command_down = player_command_down
	server.player_command_destroy = player_command_destroy
	server.player_command_pickup = player_command_pickup
	server.player_command_create = player_command_create
	server.ping = ping
	server.votebegin = votebegin

	t = time.time()
	lastUpdateTime = t
	lastSendTime = t
	while True:
		server.process_network()

		t = time.time()
		dt = t - lastUpdateTime
		if dt > UPDATE_INTERVALL:
			gameupdate(server, dt)
			lastUpdateTime = t

		dt = t - lastSendTime
		if dt > SEND_INTERVALL:
			sendgameupdate(server, t - lastUpdateTime)
			lastSendTime = t

		wait = min(UPDATE_INTERVALL - (t - lastUpdateTime),
				SEND_INTERVALL - (t - lastSendTime))
		if wait > 0:
			time.sleep(wait)
