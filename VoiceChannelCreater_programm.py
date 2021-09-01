import discord
from discord.ext.commands import Bot
from discord.ext import tasks,commands
from time import time
import datetime
import json

from uuid import uuid4
from random import randint
import traceback

Token = None
Admin = None

guilds = {}  # guild = {"category" : "924781035","Timeout":"35", ... }

channels = {} # voice = [time,timeout,report channel]


bot = commands.Bot(command_prefix="_", help_command=None)

starttime = datetime.datetime.now()

@bot.event
async def on_ready():
	print('Ready')
	await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening,name = "_help"))


def loadjsonvalues(path):
	global Token,guilds,Admin
	with open(path, 'r') as file:
		json_data = json.load(file)
		Token = json_data["Token"]
		Admin = json_data["Admin"]
		guilds = json_data["guilds"]
		
def savejsonvalues(path):
	with open(path, 'w') as file:
		data = {}
		data["Token"] = Token
		data["Admin"] = Admin
		data["guilds"] = guilds
		json.dump(data,file,indent=2)

@tasks.loop(seconds=10)
async def testing():
	global channels
	remch = []
	for ch in channels:
		try:
			if len(ch.members) > 0:
				channels[ch][0] = time()
			elif channels[ch][0] + int(guilds[channels[ch][1]]["timeout"]) < time():
				await ch.delete()
				await channels[ch][2].send(f'{ch} deleted')
				print(f'\n{ch} deleted')
				remch.append(ch)
		except Exception as ex:
			traceback.print_exc()
			remch.append(ch)
	for ch2 in remch:
		del channels[ch2]
	remch.clear()
	
	
@bot.command()
async def timeout(ctx, args=None):
	if args == None:
		await ctx.channel.send(f'timeout = {guilds[str(ctx.guild.id)]["timeout"]}')
	elif ctx.author.top_role.id == int(guilds[str(ctx.guild.id)]["adminrole"]):
		try:
			int(args)
		except:
			await ctx.send(f'timeout must be int {args}')
			print(f'\ntimeout must be int {args}')
			return
		guilds[str(ctx.guild.id)]["timeout"] = str(args)
		savejsonvalues("VoiceChannelCreaterBot_data.json")
		await ctx.send(f'timeout changed to {guilds[str(ctx.guild.id)]["timeout"]}')
		print(f'\n{ctx.guild.name}:  changed timeout to {guilds[str(ctx.guild.id)]["timeout"]}  time: {args}')
	else:
		await ctx.send("not allowed (Admin command)")


@bot.command()
async def category(ctx, args=None):
	if args == None:
		await ctx.channel.send(f'category = {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}')
	elif ctx.author.top_role.id == int(guilds[str(ctx.guild.id)]["adminrole"]):
		guilds[str(ctx.guild.id)]["category"] = str(args)
		savejsonvalues("VoiceChannelCreaterBot_data.json")
		await ctx.send(f'category changed to {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}')
		print(f'\n{ctx.guild.name}:  changed category to {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}  id: {args}')
	else:
		await ctx.send("not allowed (Admin command)")


@bot.command()
async def start(ctx):
	if ctx.author.avatar == Admin:
		await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening,name = "_help"))
		testing.start()
		await ctx.send(f'started')
		print(f'\nstarted')
	else:
		await ctx.send("not allowed (owner command)")
		print(ctx.author.avatar)


@bot.command()
async def setadmin(ctx,args):
	global guilds
	if ctx.author.avatar == Admin:
		guilds[str(ctx.guild.id)] = {"category" : None,"timeout" : None, "adminrole" : str(args)}
		savejsonvalues("VoiceChannelCreaterBot_data.json")
		await ctx.send(f'server adminrole changed to {ctx.guild.get_role(int(args))}')
		print(f'\n{ctx.guild.name}:  server adminrole changed to {ctx.guild.get_role(int(args))}')
	else:
		await ctx.send("not allowed (owner command)")


@bot.command()
async def c(ctx,*args):
	try:
		guilds[str(ctx.guild.id)]
	except:
		await ctx.channel.send('guild not registered')
		print('\nguild not registered')
		return
		
	try:
		st = ""
		if len(args) == 0:
			st = uuid4().hex[randint(0,4):randint(8,12)]
		else:
			for s in args:
				st += s + " ";
		ch = await ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"])).create_voice_channel(name=st,user_limit=None)
	except:
		
		await ctx.channel.send(f'creation failed {st} in {guilds[str(ctx.guild.id)]["category"]}')
		print(f'\n{ctx.guild.name}:  creation failed {st} in {guilds[str(ctx.guild.id)]["category"]}')
		return
	channels[ch] = [time(),str(ctx.guild.id),ctx.channel]
	await ctx.channel.send(f'{ch} created in {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}')
	print(f'\n{ctx.guild.name}:  {ch} created in {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}')


@bot.command()
async def help(ctx):
	s = "Commands:\n"

	s += "_c <name> \n creates Voice Channel\n  _c gamechannel \n  _c  \n"
	s += "\n"

	s += "_category \n prints category\n"
	s += "\n"

	s += "_timeout \n prints timeout\n"
	s += "\n"
	
	s += "_ontime \n prints ontime\n"
	s += "\n"
	
	s += "\n"
	s += "\n"

	s += "Admin commands:\n"
	
	s += "_category <id>\n changes category\n"
	s += "\n"

	s += "_timeout <sec>\n changes timeout\n"
	s += "\n"
	
	s += "\n"
	s += "\n"

	s += "Owner commands:\n"

	s += "_start\n starts deleting channels\n"
	s += "\n"
	
	s += "_setadmin <id>\n adds guild to json file and changes admin role id\n"
	s += "\n"

	await ctx.send(f"```{s}```")

@bot.command()
async def ontime(ctx):
	await ctx.send(f'ontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')
	print(f'\nontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')


loadjsonvalues("VoiceChannelCreaterBot_data.json")

bot.run(Token)