import json
import sys
from dataclasses import dataclass
from time import time
from typing import List, Dict

import interactions
from dataclasses_json import dataclass_json
from interactions import Guild
from interactions.ext.voice import setup, VoiceState


class CommandException(Exception):
    pass


@dataclass
class CChannel:
    voiceChannel: interactions.Channel = None
    deleteTime: int = None
    guild: interactions.Guild = None
    count: int = None

    def update(self, timeout: int):
        if self.deleteTime < time() + timeout:
            self.deleteTime = int(time() + timeout)


@dataclass_json
@dataclass
class CustomGuild:
    category_id: int | None
    timeout: int | None
    new_channel_name: str
    default_max_members: int
    monitor_voice_channel_id: int


guilds: Dict[int, CustomGuild] = {}

channels: List[CChannel] = []

ids = 821030130703925248

bot = interactions.Client(token="", default_scope=ids)
# setup(bot)


datafile: str = "VoiceChannelBot_data.json"


def log(mess: str, guild: Guild):
    print(f"guild:{guild.name if guild is not None else '--missing--'}[{guild.id if guild is not None else '--missing--'}] {mess}")


def err(mess: str, guild: Guild | None = None):
    print(f"guild:{guild.name if guild is not None else '--missing--'}[{guild.id if guild is not None else '--missing--'}] {mess}",
          file=sys.stderr)


def loadjsonvalues(path: str):
    with open(path, 'r') as file:
        json_data = json.load(file)
        for guild in json_data["guilds"]:
            guilds[int(guild)] = CustomGuild.from_dict(json_data["guilds"][guild])

    print(guilds)


#
# def savejsonvalues(path: str):
#     with open(path, 'w') as file:
#         data = {"guilds": guilds}
#         json.dump(data, file, indent=2)


# @tasks.loop(seconds=5)
# async def testing():
#     removeChannels = []
#     for ch in channels:
#         try:
#             if len(ch.voiceChannel.members) > 0:
#                 ch.update(int(guilds[str(ch.guild.id)]["timeout"]))
#             elif ch.deleteTime < time():
#                 await ch.voiceChannel.delete()
#                 print(f'\n{ch.guild.name}:  {ch.voiceChannel} deleted')
#                 removeChannels.append(ch)
#         except Exception:
#             traceback.print_exc()
#             removeChannels.append(ch)
#     for ch2 in removeChannels:
#         channels.remove(ch2)
#     removeChannels.clear()
