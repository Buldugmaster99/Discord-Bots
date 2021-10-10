from discord.guild import Guild
from discord.channel import VoiceChannel
from discord.ext import tasks, commands

from time import time
import datetime

import json
import traceback

class Channel:
    voiceChannel: VoiceChannel = None
    deletetime: int = None
    guild: Guild = None
    count: int = None

    def __init__(self, channel: VoiceChannel, deletetime: int, guild: Guild, count: int):
        self.voiceChannel = channel
        self.deletetime = deletetime
        self.guild = guild
        self.count = count

    def update(self, timeout: int):
        if self.deletetime < time() + timeout:
            self.deletetime = time() + timeout


guilds: dict[str, dict[str, type]] = {}

channels: list[Channel] = []

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
        data = {}
        data["Token"] = Token
        data["Admin"] = Admin
        data["guilds"] = guilds
        json.dump(data, file, indent=2)    
        

@tasks.loop(seconds=5)
async def testing():
    global channels
    remch = []
    for ch in channels:
        try:
            if len(ch.voiceChannel.members) > 0:
                ch.update(int(guilds[str(ch.guild.id)]["timeout"]))
            elif ch.deletetime < time():
                await ch.voiceChannel.delete()
                print(f'\n{ch.guild.name}:  {ch.voiceChannel} deleted')
                remch.append(ch)
        except Exception as ex:
            traceback.print_exc()
            remch.append(ch)
    for ch2 in remch:
        channels.remove(ch2)
    remch.clear()