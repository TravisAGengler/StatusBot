#!/usr/bin/env python3

import socket
from enum import Enum

class ServerStatus(Enum):
	NOT_DISCOVERED = 1
	ONLINE = 2
	OFFLINE = 3

def check_server_status(address, port):
	print("Checking {}:{}".format(address, port))
	check_socket = socket.socket()
	try:
		check_socket.connect((address, port))
		return ServerStatus.ONLINE
	except socket.error:
		return ServerStatus.OFFLINE
