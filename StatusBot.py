#!/usr/bin/env python3

import asyncio
import discord
import json
import sys

from statusCheck import ServerStatus
import statusCheck as status

# DISCORD CLIENT
client = discord.Client()

# CONFIG
def read_config():
	path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
	with open(path) as f:
	    data = json.load(f)
	return data

def get_config_item(config, config_key, default = None):
	return config[config_key] if config_key in config else default

config = read_config()
bot_token = get_config_item(config, 'bot_token')
bot_command = '/statusBot'
status_channel_name = get_config_item(config, 'status_channel', 'server-status')
server_admin_role = get_config_item(config, 'server_admin_role', 'ServerAdmin')
server_address = get_config_item(config, 'server_address', '127.0.0.1')
server_port = get_config_item(config, 'server_port', 9999)
server_frequency_bounds = [5,30]
server_frequency = get_config_item(config, 'server_check_frequency', server_frequency_bounds[1])
server_status = {'status' : ServerStatus.NOT_DISCOVERED, 'err' : None}

# HELPER FUNCTIONS
async def send_message(channel, message, user=None):
	global client
	if user:
		message = '{} {}'.format(user.mention, message)
	await client.send_message(channel, message)

async def report_server_status(status_channels):
	global server_status
	for channel in status_channels:
		await send_message(channel, "Server status has changed. Server is now {}".format(server_status['status'].name))

def has_status_changed(old_status, new_status):
	changed = False
	if old_status['status'] == ServerStatus.NOT_DISCOVERED:
			changed = True
	elif old_status['status'] == ServerStatus.ONLINE:
		if new_status['status'] == ServerStatus.OFFLINE:
			changed = True
	elif old_status['status'] == ServerStatus.OFFLINE:
		if new_status['status'] == ServerStatus.ONLINE:
			changed = True
	return changed

def get_status_channels():
	channels = []
	global status_channel_name
	global client
	for server in client.servers:
		for channel in server.channels:
			if channel.name == status_channel_name:
				channels.append(channel)
	return channels

def is_server_admin(user):
	global server_admin_role
	for role in user.roles:
		if role.name == server_admin_role:
			return True
	return False

def get_task_params():
	global server_address
	global server_port
	global server_frequency
	return {
		'address' : server_address,
		'port' : server_port,
		'frequency' : server_frequency
	}

# COMMAND HANDLERS
def config_address(new_address):
	global server_address
	server_address = new_address.strip()

def config_port(new_port):
	global server_port
	server_port = int(new_port.strip())

def config_frequency(new_frequency):
	global server_frequency
	global server_frequency_bounds
	freq_int = int(new_frequency.strip())
	if freq_int > server_frequency_bounds[1]:
		freq_int = server_frequency_bounds[1]
	elif freq_int < server_frequency_bounds[0]:
		freq_int = server_frequency_bounds[0]
	server_frequency = freq_int

config_items = {
	'address' : config_address,
	'port' : config_port,
	'frequency' : config_frequency
}

async def on_config(command_body, channel, requester):
	global server_admin_role
	if not is_server_admin(requester):
		await send_message(channel, 'Sorry, you do not have permission to configure StatusBot. Find a {} to configure StatusBot'.format(server_admin_role), requester)
		return

	command_body=command_body.strip()

	for config_item, handler in config_items.items():
		if command_body.startswith(config_item):
			config_body = command_body[len(config_item):]
			handler(config_body)
			await send_message(channel, 'Configured {} to be {}'.format(config_item, config_body), requester)
			return
	await send_message(channel, 'Cannot configure {}. Configurable items are: {}'.format(command_body.split()[0], ', '.join(list(config_items.keys()))))

async def on_tell_status(command_body, channel, requester):
	await send_message(channel, "The server is currently {}".format(server_status.name), requester)

# COMMANDS
valid_commands = {
	'config' : on_config,
	'status' : on_tell_status
}

# DISCORD TASKS
async def check_server_task():
	global client
	global server_status
	await client.wait_until_ready()
	status_channels = get_status_channels()
	while not client.is_closed:
		params = get_task_params()
		new_status = status.check_server_status(params['address'], params['port'])
		if has_status_changed(server_status, new_status):
			server_status = new_status
			await report_server_status(status_channels)
		await asyncio.sleep(params['frequency'])

# DISCORD EVENT HANDLING
@client.event
async def on_ready():
	print('StatusBot\'s status is A-OK!')

@client.event
async def on_message(message):
	global client
	if message.author == client.user:
		return # We do not want to process our own messages

	global bot_command
	for command, handler in valid_commands.items():
		complete_command = bot_command + ' ' + command
		if message.content.startswith(complete_command):
			command_body = message.content[len(complete_command):]
			await handler(command_body, message.channel, message.author)
			break

status_task = client.loop.create_task(check_server_task())
client.run(bot_token)
status_task.cancel()
