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

def get_channel(channel_name):
	for channel in client.get_all_channels():
		if channel.name == channel_name:
			return channel
	print("No channel with name {} was found on the server.".format(channel_name))

def is_server_admin(user):
	for role in user.roles:
		if role.name == server_admin_role:
			return True
	return False

config = read_config()
bot_token = get_config_item(config, 'bot_token')
status_channel = None # Needs to be discovered after the bot connects to the server
status_channel_name = get_config_item(config, 'status_channel', 'server-status')
server_admin_role = get_config_item(config, 'server_admin_role', 'ServerAdmin')
server_ip = get_config_item(config, 'server_ip', '127.0.0.1')
server_port = get_config_item(config, 'server_port', 9999)
server_check_frequency = get_config_item(config, 'server_check_frequency', 60)
server_status = ServerStatus.NOT_DISCOVERED

# HELPER FUNCTIONS
async def send_message(channel, message, user=None):
	if user:
		message = '{} {}'.format(user.mention, message)
	await client.send_message(channel, message)

async def update_server_status(status):
	print('Got status: {}'.format(status.name))
	changed = False
	global server_status
	if server_status == ServerStatus.NOT_DISCOVERED:
		if status == ServerStatus.ONLINE:
			changed = True
	elif server_status == ServerStatus.ONLINE:
		if status == ServerStatus.OFFLINE:
			changed = True
	elif server_status == ServerStatus.OFFLINE:
		if status == ServerStatus.ONLINE:
			changed = True
	if changed:
		server_status = status
		await send_message(status_channel, "Server status has changed. Server is now {}".format(server_status.name))

# COMMAND HANDLERS
def config_ip(new_ip):
	global server_ip
	server_ip = new_ip.strip()

def config_port(new_port):
	global server_port
	server_port = int(new_port.strip())

def config_frequency(new_frequency):
	global server_check_frequency
	server_check_frequency = int(new_frequency.strip())

config_items = {
	'ip' : config_ip,
	'port' : config_port,
	'frequency' : config_frequency
}

async def on_config(command_body, channel, requester):
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
	await send_message(channel, 'Cannot configure {}. Configurable items are: {}'.format(command_body.split()[0], config_items.keys().join(', ')))

# COMMANDS
valid_commands = {'/statusBotConfig' : on_config}

# DISCORD TASKS
async def check_server_task():
	global status_channel
	await client.wait_until_ready()
	while not client.is_closed:
		if(status_channel):
			await update_server_status(status.check_server_status(server_ip, server_port))
		else:
			print('Attempting to find channel {}'.format(status_channel_name))
			status_channel = get_channel(status_channel_name)
		await asyncio.sleep(server_check_frequency)

# DISCORD EVENT HANDLING
@client.event
async def on_ready():
	print('StatusBot\'s status is A-OK!')

@client.event
async def on_message(message):
	if message.author == client.user:
		return # We do not want to process our own messages

	for command, handler in valid_commands.items():
		if message.content.startswith(command):
			command_body = message.content[len(command):]
			await handler(command_body, message.channel, message.author)
			break

client.loop.create_task(check_server_task())
client.run(bot_token)
