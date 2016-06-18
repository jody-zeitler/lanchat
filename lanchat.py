#!/usr/bin/env python3

from select import select
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_BROADCAST
import sys
from time import sleep

import netifaces

LAN_SUBNET = "192.168."
SERVICE_PORT = 6983
BUFFER_SIZE = 4096

def get_lan_address():
	for intf in netifaces.interfaces():
		for binding in netifaces.ifaddresses(intf).get(netifaces.AF_INET, []):
			addr = binding['addr']
			if addr.startswith(LAN_SUBNET):
				return addr

def setup_socket(address, port):
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind((address, port))
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	return s

class DatagramClient(object):
	def __init__(self):
		self.address = get_lan_address()
		self.port = SERVICE_PORT
		self.socket = setup_socket(self.address, self.port)

	def send_message(self, text):
		data = bytes(text, "utf8")
		self.socket.sendto(data, ('<broadcast>', self.port))

	def receive_message(self):
		message = self.socket.recvfrom(BUFFER_SIZE)
		if message:
			return (str(message[0], "utf8"), message[1])
		else:
			return None

def loop(client):
	ready,w,x = select([client.socket, sys.stdin], [], [])
	if len(ready) > 0:
		if client.socket in ready:
			print('incoming')
			incoming = client.receive_message()
			if incoming:
				print('{}: {}'.format(incoming[1], incoming[0]))
		if sys.stdin in ready:
			outgoing = sys.stdin.readline()
			if outgoing:
				client.send_message(outgoing)

def main(args):
	client = DatagramClient()
	print('bound to {}:{}'.format(client.address, client.port))
	while True:
		loop(client)

if __name__=="__main__": sys.exit(main(sys.argv[1:]))
