#!/usr/bin/env python

import pygame, os, sys, time
import pygame.font
from pygame.color import Color

from libs import pygl2d

from random import *
from common.rules import *
from common.map import *
from common.vector import *
from client.mapvisualizer import *
from client.client import *
from client.networkconstants import *
from mapparse import parse_map
from libs.pygl2d.font import RenderText

PING_INTERVALL = 3.0

class Main:
	def __init__(self, playername, hostname):
		self.screen = None
		self.screenDim = Vector(800,576)
		self.background = (255,255,255)
		self.running = False
		self.showFPS = True

		self.current_state = "warmup"
		self.startTime = None

		self.packetTime = 1/30.0
		self.lastPingTime = time.clock()
		self.lastPongTime = time.clock()

		self.playername = playername or "Player_" + str(int(100 * random()))
		self.playerid = None
		
		pygl2d.window.init(self.screenDim.toIntArr(), caption="Misplaced")

		pygame.font.init()
		fontname = pygame.font.get_default_font()
		self.font = pygame.font.Font(fontname, 32)
		self.statetext = RenderText("", Color("red"), self.font)

		self.networkClient = Client(hostname)

		self.networkClient.send(NetworkCommand.Name, self.playername)

		self.networkClient.mapdata = self.mapUpdate
		self.networkClient.mapdataupdate = self.mapDataUpdate
		self.networkClient.welcome = self.welcomeMessage
		self.networkClient.pong = self.pong
		self.networkClient.left = self.playerLeft
		self.networkClient.state = self.state

		self.map = None

	# ====================================================================================================
	# =======================           Network                      =====================================
	# ====================================================================================================

	def sendPing(self):
		self.lastPingTime = time.clock()
		self.networkClient.send(NetworkCommand.Ping, self.lastPingTime)

	def pong(self, number):
		t = time.clock()
		self.packetTime = (t - self.lastPingTime)/2.0
		self.lastPongTime = t

	def welcomeMessage(self, id):
		self.playerid = id

	def state(self, newstate):
		self.current_state = newstate
		if self.map:
			self.map.current_state = self.current_state
		if self.current_state == "game":
			self.startTime = time.clock()
	
	def updateStateText(self):
		text = ""
		player = None
		if self.map and self.map.map.players.has_key(self.playerid):
			player = self.map.map.players[self.playerid]
		if self.current_state == "warmup":
			if not player.voted_begin:
				text += "Warmup, press F3 when ready!"
		else:
			if player.evil is not None:
				if player.evil:
					text += "You are evil. "
				else:
					text += "You are nice. "
			text += "%.0fs left." % (ROUND_TIME + self.startTime - time.clock())
		self.statetext.change_text(text)

	def mapUpdate(self, strmapdata):
		# Assume the server just sent us a filename
		#mapdata = parse_map(open(strmapdata))
		mapdata = Map.deserialize(strmapdata)
		if not self.map:
			self.map = MapVisualizer(mapdata, self.playerid, self.screenDim)
			self.map.current_state = self.current_state
		else:
			self.map.setData(mapdata)
	
	def mapDataUpdate(self, strmapupdate):
		mapupdate = MapUpdate.deserialize(strmapupdate)
		if self.map:
			self.map.setUpdateData(mapupdate, self.packetTime)

	def playerLeft(self, playerid):
		if self.map.map.players.has_key(playerid):
			del self.map.map.players[playerid]

	# ====================================================================================================
	# =======================           Inputs                       =====================================
	# ====================================================================================================

	def player_interact(self, interaction, doit):
		if self.map and self.map.map.players.has_key(self.playerid):
			self.map.map.players[self.playerid].interact(interaction, doit)

	def movePlayer(self, direction, doit):
		if self.map and self.map.map.players.has_key(self.playerid):
			self.map.map.players[self.playerid].move(direction, doit)

	def poll(self):
		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				self.running = False
			elif e.type == pygame.KEYDOWN:

				if e.key == pygame.K_LEFT or e.key == pygame.K_a:
					self.networkClient.send(NetworkCommand.Player_Command_Left, True)
					self.movePlayer(Direction.Left, True)
				elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
					self.networkClient.send(NetworkCommand.Player_Command_Right, True)
					self.movePlayer(Direction.Right, True)
				elif e.key == pygame.K_UP or e.key == pygame.K_w:
					self.networkClient.send(NetworkCommand.Player_Command_Up, True)
					self.movePlayer(Direction.Up, True)
				elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
					self.networkClient.send(NetworkCommand.Player_Command_Down, True)
					self.movePlayer(Direction.Down, True)
				elif e.key == pygame.K_SPACE:
					self.networkClient.send(NetworkCommand.Player_Command_Destroy, True)
					self.player_interact(Interaction.Destroy, True)
                                elif e.key == pygame.K_RETURN:
                                        self.networkClient.send(NetworkCommand.Player_Command_PickUp, True)
                                        self.player_interact(Interaction.PickUp, True)
				elif e.key == pygame.K_F3:
					self.networkClient.send("votebegin")
 
			
			elif e.type == pygame.KEYUP:
				if e.key == pygame.K_ESCAPE:
					self.running = False

				elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
					self.networkClient.send(NetworkCommand.Player_Command_Left, False)
					self.movePlayer(Direction.Left, False)
				elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
					self.networkClient.send(NetworkCommand.Player_Command_Right, False)
					self.movePlayer(Direction.Right, False)
				elif e.key == pygame.K_UP or e.key == pygame.K_w:
					self.networkClient.send(NetworkCommand.Player_Command_Up, False)
					self.movePlayer(Direction.Up, False)
				elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
					self.networkClient.send(NetworkCommand.Player_Command_Down, False)
					self.movePlayer(Direction.Down, False)
				elif e.key == pygame.K_SPACE:
					self.networkClient.send(NetworkCommand.Player_Command_Destroy, False)
					self.player_interact(Interaction.Destroy, True)
                                elif e.key == pygame.K_RETURN:
                                        self.networkClient.send(NetworkCommand.Player_Command_PickUp, False)
                                        self.player_interact(Interaction.PickUp, False)

	

	# ====================================================================================================
	# =======================           Game Loop                    =====================================
	# ====================================================================================================
	
	def update(self, dt):
		if self.map:
			self.map.clientUpdate(dt)
		self.updateStateText()
	
	def draw(self):
		pygl2d.window.begin_draw()

		if self.map:
			self.map.draw()
		elif not self.networkClient.connected:
			pass # todo draw waiting for server message

		self.statetext.draw(self.screenDim
				- Vector(self.statetext.get_width() + 13,
		                 self.statetext.get_height() + 13))

		pygl2d.window.end_draw()
	
	def run(self):
		
		self.running = True
		clock = pygame.time.Clock()
		while self.running:
			dt = clock.tick(30) / 1000.0

			if self.showFPS and self.map:
				fps = clock.get_fps()
				#print "FPS:",fps
				#fps_display = pygl2d.font.RenderText(str(int(fps)), [0, 0, 0], self.font)
				#fps_display.draw([10, 10])

			self.poll()

			self.networkClient.process_updates()
			
			self.update(dt)
			self.draw()

			if (time.clock() - self.lastPongTime) > PING_INTERVALL:
				self.sendPing()

if __name__ == '__main__':
	playername = None
	if len(sys.argv) > 1:
		playername = sys.argv[1]

	hostname = "localhost"
	if len(sys.argv) > 2:
		hostname = sys.argv[2]

	main = Main(playername, hostname)
	print "starting..."
	main.run()
	print "shuting down..."
