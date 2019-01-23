#!/usr/bin/env python3

import socket

def check_server_status(address, port):
	check_socket = socket.socket()
	try:
		check_socket.connect(address, port)
		return True
	except socket.error:
		return False