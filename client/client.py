#!/usr/bin/env python
import socket
import sys

PORT=12345

class Client:
	def __init__(self, server):
		self._connect(server)
		self.connected = True
		self.partialdata = ""

	def _connect(self, server):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((server, PORT))
		self.s.setblocking(0)

	def say(self, text):
		print text

	def abort(self, text):
		print "Game aborted"
		self.connected = False
	
	def welcome(self, id):
		pass # to be overwritten
	
	def mapdata(self, mapdata):
		pass # to be overwritten
	
	def mapdataupdate(self, mapupdate):
		pass # to be overwritten
	
	def pong(self, number):
		pass # to be overwritten

	def process_updates(self):
		if not self.connected: return
	
		while True:	
			try:
				data = self.s.recv(4096)
				if not data:
					print "Server quit"
					self.connected = False
					return
				data = self.partialdata + data
				if data == "":
					continue

				commandlines = data.split("\n")
				if not data[-1] == "\n":
					self.partialdata = commandlines.pop()
				else:
					self.partialdata = ""

				for line in commandlines:
					if line == "":
						continue
					(command,_,args) = line.partition(" ")
					print "Received command %s from server" % (command,)
					if hasattr(self, command):
						method = getattr(self, command)
						method(args)
					else:
						print "Unknown command %s" % (command, )
			except socket.error as e:
				break

	def send(self, command, argument=""):
		print "Send command '%s'" % command
		try:
			self.s.sendall("%s %s\n" % (command, argument))
		except:
			print "Server failed?"
			self.connected = False

if __name__ == "__main__":
	# Example commandline test client
	client = Client("localhost")

	while client.connected:
		client.process_updates()

		# Read 1 command from user
		command = sys.stdin.readline()
		command = command.strip()
		if command == "":
			continue
		client.send(command)
