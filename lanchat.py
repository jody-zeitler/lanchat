#!/usr/bin/env python3

from select import select
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST
import sys

import netifaces

LAN_SUBNET = '192.168.'
SERVICE_PORT = 6983
BUFFER_SIZE = 4096

def get_lan_address(subnet):
	for intf in netifaces.interfaces():
		for binding in netifaces.ifaddresses(intf).get(netifaces.AF_INET, []):
			addr = binding['addr']
			if addr.startswith(subnet):
				return addr

def setup_socket(address, port):
	s = socket(AF_INET, SOCK_DGRAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	s.bind((address, port))
	return s

class DatagramClient(object):
	def __init__(self, subnet, port):
		self.address = get_lan_address(subnet)
		self.port = port
		self.recv_socket = setup_socket('', self.port)
		self.send_socket = setup_socket(self.address, self.port)

	def send_message(self, text):
		data = bytes(text, 'utf8')
		self.send_socket.sendto(data, ('<broadcast>', self.port))

	def receive_message(self):
		message = self.Message(self.recv_socket.recvfrom(BUFFER_SIZE))
		if message.address not in (None, self.address):
			return message
		else:
			return None

	class Message(object):
		def __init__(self, tupl):
			if tupl:
				self.address = tupl[1][0]
				self.port = tupl[1][1]
				self.text = str(tupl[0], 'utf8')
			else:
				self.address = None
				self.port = None
				self.text = None

def loop(client):
	ready,w,x = select([client.recv_socket, sys.stdin], [], [])
	if len(ready) > 0:
		if client.recv_socket in ready:
			incoming = client.receive_message()
			if incoming:
				print('{}: {}'.format(incoming.address, incoming.text.rstrip()))
		if sys.stdin in ready:
			outgoing = sys.stdin.readline()
			if outgoing:
				client.send_message(outgoing)

def main(args):
	client = DatagramClient(LAN_SUBNET, SERVICE_PORT)
	print('bound to {}:{}'.format(client.address, client.port))
	while True:
		loop(client)

if __name__=="__main__": sys.exit(main(sys.argv[1:]))
