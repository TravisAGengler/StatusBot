# StatusBot
StatusBot is a Discord bot for checking the status of a game server. Written in Python

# Features
  - Periodically checks the status of a server and sends a message to a designated channel when the status of the server changes
  - Configurable on the fly. If your server address or port changes, ServerAdmins can configure StatusBot to check the new socket address
  - Supports hostname resolution 

# Usage
StatusBot is configurable through `config.json` or through discord itself. Use the following commands to configure the `address` `port` or `server_check_frequency` of the bot:
`/statusBot config address 127.0.0.1`
```markdown
Configured address to be 127.0.0.1
```
`/statusBot config port 9999`
```markdown
Configured port to be 9999
```
`/statusBot config frequency 25`
```markdown
Configured frequency to be 25
```

You can also have StatusBot tell you the status of the server by using `/statusBot status`:
`/statusBot status`
```markdown
The server is currently ONLINE
```
Frequency is measured in seconds.  Maximum frequency is 5 seconds, minimum is 30 seconds. Any values you configure outside of this range will be made to fit inside this range

# Planned Features
  - N/A

# Possible Features
  - Support for checking the status of multiple servers
  - Suggest other features by creating an [issue](https://github.com/TravisAGengler/StatusBot/issues) and giving it the label `enhancement`

# config.json
config.json is important to configuring StatusBot. Here is a sample `config.json`:
```json
{
	"bot_token" : "MY_SUPER_SECRET_TOKEN",
	"status_channel" : "The channel to post status to. Defaults to server-status",
	"server_admin_role" : "The role required to call /statusBotConfig. Defaults to ServerAdmin",
	"server_address" : "The address to check the status of. IPv4 address or domain name. Defaults to 127.0.0.1",
	"server_port" : "The port to check the status of. Defaults to 9999",
	"server_check_frequency" : "The frequency in seconds which StatusBot checks the server. Defaults to 30 seconds."
}
```
Pass the path to this file as the first argument to your invocation of `StatusBot.py`. By default, StatusBot looks for `./config.json`
