import datetime
import json
import traceback
from time import time

from discord.channel import VoiceChannel
from discord.ext import commands, tasks
from discord.guild import Guild


class Channel:
	voiceChannel: VoiceChannel = None
	deleteTime: int = None
	guild: Guild = None
	count: int = None
	
	def __init__(self, channel: VoiceChannel, deleteTime: int, guild: Guild, count: int):
		self.voiceChannel = channel
		self.deleteTime = deleteTime
		self.guild = guild
		self.count = count
	
	def update(self, timeout: int):
		if self.deleteTime < time() + timeout:
			self.deleteTime = int(time() + timeout)


# guilds: dict[str, dict[str, type]] = {}
guilds = {}

# channels: list[Channel] = []
channels = []

started: bool = False

starttime: datetime = None

Token: str = None
Admin: int = None

bot: commands.Bot = commands.Bot(command_prefix="?", help_command=None)

datafile: str = "VoiceChannelBot_data.json"


def loadjsonvalues(path: str):
	global Token, guilds, Admin
	with open(path, 'r') as file:
		json_data = json.load(file)
		Token = json_data["Token"]
		Admin = json_data["Admin"]
		guilds = json_data["guilds"]


def savejsonvalues(path: str):
	with open(path, 'w') as file:
		data = {"Token": Token, "Admin": Admin, "guilds": guilds}
		json.dump(data, file, indent=2)


@tasks.loop(seconds=5)
async def testing():
	removeChannels = []
	for ch in channels:
		try:
			if len(ch.voiceChannel.members) > 0:
				ch.update(int(guilds[str(ch.guild.id)]["timeout"]))
			elif ch.deleteTime < time():
				await ch.voiceChannel.delete()
				print(f'\n{ch.guild.name}:  {ch.voiceChannel} deleted')
				removeChannels.append(ch)
		except Exception:
			traceback.print_exc()
			removeChannels.append(ch)
	for ch2 in removeChannels:
		channels.remove(ch2)
	removeChannels.clear()
