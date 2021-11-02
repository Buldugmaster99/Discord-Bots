import datetime
from time import time

import discord
from discord import Member
from discord.channel import VoiceChannel
from discord.ext import commands

import VoiceChannelBot_commands as Botcommands
import VoiceChannelBot_globals as Globals

# must be imported else commands will not be applied

_ = Botcommands


@Globals.bot.event
async def on_ready():
	print('Ready')
	await Globals.bot.change_presence(status=discord.Status.idle,
	                                  activity=discord.Activity(type=discord.ActivityType.listening, name="?help"))


@commands.Cog.listener()
async def on_voice_state_update(member: Member, _, after: VoiceChannel):
	if after.channel is None or not Globals.started:
		return
	if after.channel == member.guild.get_channel(Globals.guilds[str(member.guild.id)]["monitorchannel"]):
		if Globals.guilds[str(member.guild.id)]["countup"]:
			repeat = True
			count = 1
			while repeat:
				for channel in Globals.channels:
					if channel.guild.id == member.guild.id and str(count) == str(channel.count).strip():
						count += 1
				repeat = False
		else:
			count = ""
		
		ch = await member.guild.get_channel(Globals.guilds[str(member.guild.id)]["category"]).create_voice_channel(
			name=Globals.guilds[str(member.guild.id)]["name"] + " " + str(count),
			user_limit=Globals.guilds[str(member.guild.id)]["defaultmaxmembers"])
		await member.move_to(ch)
		
		Globals.channels.append(Globals.Channel(ch, int(time() + Globals.guilds[str(member.guild.id)]["timeout"]), member.guild, count))
		print(
			f'\n{member.guild.name}:  new channel created: {ch} in {member.guild.get_channel(Globals.guilds[str(member.guild.id)]["category"])}')


Globals.bot.add_listener(on_voice_state_update)

if __name__ == "__main__":
	Globals.loadjsonvalues(Globals.datafile)
	Globals.starttime = datetime.datetime.now()
	
	Globals.bot.run(Globals.Token)
