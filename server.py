#!/usr/bin/env python
import socket, time
from sys import exit
from random import *
from common.map import *
from common.player import *
from mapparse import parse_map

HOST = ''
PORT = 12345

UPDATE_INTERVALL = 1.0/30.0
SEND_INTERVALL = 0.1

mapname = "data/test.stl"
mapdata = parse_map(open(mapname))

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
			if e.errno == 10054:
				raise RuntimeError("client dropped")
			elif e.errno == 35 or e.errno == 10035:
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

	def sendall(self, text):
		for client in self.clients:
			self.send(client, text)

	def send(self, client, text):
		if client.inactive:
			return
		try:
			fine = my_sendall(client.conn, text + "\n")
		except:
			self._drop_client(client)

	def _drop_client(self, client):
		print "Client %s left." % (client.addr, )
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
				print "Connect by ", addr
				client = Client(conn, addr)
				client.id = len(self.clients)
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
					self._drop_client(client)
					continue
				data = client.partialdata + data
			except socket.error as e:
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

	def gameupdate(server, dt):
		mapdata.update(dt)

	def sendgameupdate(server):
		mapupdate = mapdata.getMapUpdate()

		if mapupdate.hasData():
			sendMapUpdate(mapupdate)

	# ====================================================================================================
	# =======================           Network Functions                      ===========================
	# ====================================================================================================

	def say(client, text):
		global server
		server.sendall("say %s: %s" % (client.name, text))

	def sendmap(client, text):
		global server
		server.send(client, "mapdata " + mapdata.serialize())

	def changename(client, newname):
		global server

		print "%s changed name to %s" % (client, newname)
		client.name = newname
		client.player.name = newname
		client.player.visible = True

		server.send(client, "welcome " + client.player.id)
		server.send(client, "mapdata " + mapdata.serialize())

	def abort(client, args):
		global server
		print "%s send abort game" % str(client)
		server.sendall("abort")

	def joined(client):
		player = Player(str(client.id), randint(0,mapdata.width), randint(0,mapdata.height))
		mapdata.addPlayer(player)
		client.player = player

	def left(client):
		player = client.player
		if player in mapdata.players:
			del mapdata.players[player]

	def player_command_right(client, doit):
		client.player.move(Direction.Right, doit == "True")

	def player_command_left(client, doit):
		client.player.move(Direction.Left, doit == "True")

	def player_command_up(client, doit):
		client.player.move(Direction.Up, doit == "True")

	def player_command_down(client, doit):
		client.player.move(Direction.Down, doit == "True")

	def player_command_attack(client, doit):
		pass # todo

	def ping(client, number):
		global server
		server.send(client, "pong " + str(number))

	server.say = say
	server.sendmap = sendmap
	server.changename = changename
	server.abort = abort
	server.joined = joined
	server.left = left
	server.player_command_right = player_command_right
	server.player_command_left = player_command_left
	server.player_command_up = player_command_up
	server.player_command_down = player_command_down
	server.player_command_attack = player_command_attack
	server.ping = ping

	t = time.clock()
	lastUpdateTime = t
	lastSendTime = t
	while True:
		server.process_network()

		t = time.clock()
		dt = t - lastUpdateTime
		if dt > UPDATE_INTERVALL:
			gameupdate(server, dt)
			lastUpdateTime = t

		dt = t - lastSendTime
		if dt > SEND_INTERVALL:
			sendgameupdate(server)
			lastSendTime = t
