#!/usr/bin/python

import pygame, os, sys

from libs import pygl2d

from random import *
from common.map import *
from common.vector import *
from client.mapvisualizer import *
from client.client import *
from client.networkconstants import *
from mapparse import parse_map

class Main:
	def __init__(self, hostname):
		self.screen = None
		self.screenDim = Vector(800,576)
		self.background = (255,255,255)
		self.running = False
		self.showFPS = True

		self.playername = "Player_" + str(int(100 * random()))
		
		pygl2d.window.init(self.screenDim.toIntArr(), caption="Misplaced")

		self.font = pygame.font.SysFont("Courier New", 32, bold=True)
		self.fontColor = (0, 0, 0)

		self.networkClient = Client(hostname)

		self.networkClient.send(NetworkCommand.Name, self.playername)

		self.networkClient.mapdata = self.mapUpdate
		self.networkClient.mapdataupdate = self.mapDataUpdate

		self.map = None

	# ====================================================================================================
	# =======================           Network                      =====================================
	# ====================================================================================================

	def mapUpdate(self, strmapdata):
		# Assume the server just sent us a filename
		#mapdata = parse_map(open(strmapdata))
		mapdata = Map.deserialize(strmapdata)
		if not self.map:
			self.map = MapVisualizer(mapdata, self.playername, self.screenDim)
		else:
			self.map.setData(mapdata)
	
	def mapDataUpdate(self, strmapupdate):
		mapupdate = MapUpdate.deserialize(strmapupdate)
		if self.map:
			self.map.setUpdateData(mapupdate)
	

	# ====================================================================================================
	# =======================           Inputs                       =====================================
	# ====================================================================================================

	def poll(self):
		events = pygame.event.get()
		for e in events:
			if e.type == pygame.QUIT:
				self.running = False
			elif e.type == pygame.KEYDOWN:

				if e.key == pygame.K_LEFT or e.key == pygame.K_a:
					self.networkClient.send(NetworkCommand.Player_Command_Left, True)
				elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
					self.networkClient.send(NetworkCommand.Player_Command_Right, True)
				elif e.key == pygame.K_UP or e.key == pygame.K_w:
					self.networkClient.send(NetworkCommand.Player_Command_Up, True)
				elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
					self.networkClient.send(NetworkCommand.Player_Command_Down, True)
				elif e.key == pygame.K_SPACE:
					self.networkClient.send(NetworkCommand.Player_Command_Attack, True)
			
			elif e.type == pygame.KEYUP:
				if e.key == pygame.K_ESCAPE:
					self.running = False

				elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
					self.networkClient.send(NetworkCommand.Player_Command_Left, False)
				elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
					self.networkClient.send(NetworkCommand.Player_Command_Right, False)
				elif e.key == pygame.K_UP or e.key == pygame.K_w:
					self.networkClient.send(NetworkCommand.Player_Command_Up, False)
				elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
					self.networkClient.send(NetworkCommand.Player_Command_Down, False)
				elif e.key == pygame.K_SPACE:
					self.networkClient.send(NetworkCommand.Player_Command_Attack, False)

	

	# ====================================================================================================
	# =======================           Game Loop                    =====================================
	# ====================================================================================================
	
	def update(self, dt):
		if self.map:
			self.map.clientUpdate(dt)
	
	def draw(self):
		pygl2d.window.begin_draw()

		if self.map:
			self.map.draw()
		elif not self.networkClient.connected:
			pass # todo draw waiting for server message

		pygl2d.window.end_draw()
	
	def run(self):
		
		self.running = True
		clock = pygame.time.Clock()
		while self.running:
			dt = clock.tick(40) / 1000.0

			if self.showFPS and self.map:
				fps = clock.get_fps()
				print "FPS:",fps
				#fps_display = pygl2d.font.RenderText(str(int(fps)), [0, 0, 0], self.font)
				#fps_display.draw([10, 10])

			self.poll()

			self.networkClient.process_updates()
			
			self.update(dt)
			self.draw()

if __name__ == '__main__':
	hostname = "localhost"
	if len(sys.argv) > 1:
		hostname = sys.argv[1]

	main = Main(hostname)
	print "starting..."
	main.run()
	print "shuting down..."
