import discord
from discord.ext.commands import Bot
from discord.ext import tasks,commands
import datetime
from datetime import timezone

Token = "--Token--"

bot = commands.Bot(command_prefix="|", help_command=None)

reportchannel = None

deletetimeint = 180

started = False

starttime = datetime.datetime.now()

Admin = 0000

@bot.event
async def on_ready():
	print('Ready')
	await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening,name = "|help"))

@tasks.loop(seconds=5)
async def testing():
	try:
		utc = datetime.datetime.now(tz = timezone.utc) - datetime.timedelta(0,deletetimeint)
		async for mess in reportchannel.history(limit = 50):
			if mess.created_at.replace(tzinfo=timezone.utc) < utc and mess.author == bot.user:
				await mess.delete()
	except Exception as e:
		print(e)

@commands.Cog.listener()
async def on_voice_state_update(member,bevore,after):
	if not started:
		return 
	try:
		if not bevore.channel:
			print(f'\n{str(datetime.datetime.now())}:  {member.display_name} joined {after.channel.name}')
			await reportchannel.send(f'{member.display_name} joined {after.channel.name}')

		if bevore.channel and not after.channel:
			print(f'\n{str(datetime.datetime.now())}:  {member.display_name} left {bevore.channel.name}')
			await reportchannel.send(f'{member.display_name} left {bevore.channel.name}')

		if bevore.channel and after.channel and not bevore.channel == after.channel:
			print(f'\n{str(datetime.datetime.now())}:  {member.display_name} switched from {bevore.channel.name} to {after.channel.name}')
			await reportchannel.send(f'{member.display_name} switched from {bevore.channel.name} to {after.channel.name}')
	except Exception:
		pass

bot.add_listener(on_voice_state_update)

stages = []

@tasks.loop(seconds=0.5)
async def repeat():
	try:
		for stage in stages:
			for member in stage.requesting_to_speak:
				print(f"allowed {member} to speak")
				await member.request_to_speak()
	except Exception as e:
		print(e)


@commands.command()
async def stage(ctx, args=None, remove=None):
	if args == None:
		await ctx.channel.send(f'stages = {stages}')
	elif ctx.author.top_role.id == Admin:
		if remove:
			stages.remove(ctx.guild.get_channel(int(args)))
			await ctx.send(f'removed {ctx.guild.get_channel(int(args))} from stages')
			print(f'\nremoved {ctx.guild.get_channel(int(args))} from stages')
		else:
			stages.append(ctx.guild.get_channel(int(args)))
			await ctx.send(f'add {ctx.guild.get_channel(int(args))} to stages')
			print(f'\nadd {ctx.guild.get_channel(int(args))} to stages')

	else:
		await ctx.send("not allowed")

bot.add_command(stage)

@commands.command()
async def channel(ctx, args=None):
	global reportchannel
	if args == None:
		await ctx.channel.send(f'reportchannel = {reportchannel}')
	elif ctx.author.top_role.id == Admin:
		reportchannel = ctx.guild.get_channel(int(args))
		await ctx.send(f'reportchannel changed to {reportchannel}')
		print(f'\nreportchannel changed to {reportchannel}')
	else:
		await ctx.send("not allowed")

bot.add_command(channel)

@commands.command()
async def deletetime(ctx, args=None):
	global deletetimeint
	if args == None:
		await ctx.channel.send(f'deletetime = {deletetimeint} sec')
	elif ctx.author.top_role.id == Admin:
		deletetimeint = int(args)
		await ctx.channel.send(f'deletetime changed to {deletetimeint} sec')
		print(f'\ndeletetime changed to {deletetimeint} sec')
	else:
		await ctx.send("not allowed")

bot.add_command(deletetime)

@commands.command()
async def start(ctx):
	global started
	if ctx.author.top_role.id == Admin:
		started = True
		await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening,name = "|help"))
		testing.start()

		repeat.start()

		await ctx.send('started')
		print('\nstarted')
	else:
		await ctx.send("not allowed")

bot.add_command(start)

@bot.command()
async def help(ctx):
	s = "Commands:\n"
		
	s += "|channel \n prints notification channel\n"
	s += "\n"

	s += "|stage \n prints all where all request to speak are accepted\n"
	s += "\n"
	
	s += "|deletetime \n prints deletetime\n"
	s += "\n"
	
	s += "|ontime \n prints ontime\n"
	s += "\n"
	
	s += "\n"
	s += "\n"

	s += "Admin commands:\n"
	
	s += "|start \n starts listening for voiceupdates and delets old messages\n"
	s += "\n"

	s += "|channel <id> \n sets notification channel\n"
	s += "\n"

	s += "|stage <id> <remove> \n adds / removes stage to accept all request to speak\n"
	s += "\n"
	
	s += "|deletetime <sec> \n sets deletetime\n"
	s += "\n"

	await ctx.send(f"```{s}```")

@commands.command()
async def ontime(ctx):
	await ctx.send(f'ontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')
	print(f'\nontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')

bot.add_command(ontime)

bot.run(Token)
