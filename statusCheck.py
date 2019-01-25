#!/usr/bin/env python3

import socket
import sys

from enum import Enum

# PUBLIC API
class ServerStatus(Enum):
	NOT_DISCOVERED = 1
	ONLINE = 2
	OFFLINE = 3

def check_server_status(address, port):
	check_socket = socket.socket()
	check_socket.settimeout(5) # 5 second timeout should suffice
	try:
		check_socket.connect((address, port))
		check_socket.shutdown(socket.SHUT_RDWR)
		check_socket.close()
		return {'status' : ServerStatus.ONLINE, 'err' : None}
	except socket.error as err:
		return {'status' : ServerStatus.OFFLINE, 'err' : err}

# MAIN
def _main():
	address = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
	port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
	status = check_server_status(address, port)
	print('Server {}:{} is {} {}'.format(address, port, status['status'].name, status['err'] if status['err'] else ''))

# MAIN HOOK
if __name__ == "__main__":
	_main()
