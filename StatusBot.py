#!/usr/bin/env python3

import discord
import json
import sys

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
status_channel = get_config_item(config, 'status_channel', 'server-status')
server_admin_role = get_config_item(config, 'server_admin_role', 'ServerAdmin')
server_ip = get_config_item(config, 'server_ip', '127.0.0.1')
server_port = get_config_item(config, 'server_port', '9999')
server_check_frequency = get_config_item(config, 'server_check_frequency', 60)

# HELPER FUNCTIONS
async def send_message(channel, message, user=None):
	if user:
		message = '{} {}'.format(user.mention, message)
	await client.send_message(channel, message)

# COMMAND HANDLERS
def config_ip(new_ip):
	server_ip = new_ip.strip()

def config_port(new_port):
	server_port = new_port.strip()

def config_frequency(new_frequency):
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
			config_body = message.content[len(command):]
			handler(config_body)
			await send_message(channel, 'Configured {} to be {}'.format(config_item, config_body), requester)
			return
	await send_message(channel, 'Cannot configure {}. Configurable items are: {}'.format(command_body.split()[0], config_items.keys().join(', ')))

# COMMANDS
valid_commands = {'/statusBotConfig' : on_config}

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

client.run(bot_token)
