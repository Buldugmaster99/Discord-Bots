import discord
from discord.ext.commands import Bot
from discord.ext import commands,tasks
import datetime
import time
import json

bot = commands.Bot(command_prefix=">", help_command=None)

Conferences = []

notifychannel = None

Token = None
times = None
alias = None
roles = None
links = None
adminrole = None
notificationtime = None
dailyalltimes = None
dailyclearhour = None
year = None

dailyall = False

starttime = datetime.datetime.now()

@bot.event
async def on_ready():
	print('Ready')
	await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening,name = ">help  "))

def loadjsonvalues(path):
	global Token,times,alias,roles,links,adminrole,notificationtime,dailyclearhour,dailyall,dailyalltimes,year
	with open(path, 'r') as file:
		json_data = json.load(file)
		Token = json_data["Token"]
		times = json_data[json_data["Breaks"] + "times"]
		alias = json_data["alias"]
		roles = json_data["roles"]
		links = json_data["links"]
		adminrole = int(json_data["adminrole"])
		notificationtime = int(json_data["notificationtime"])
		dailyclearhour = int(json_data["dailyclearhour"])
		dailyalltimes = json_data["dailyalltimes"]
		year = int(json_data["year"])

def replace(val):
	for ali, vals in alias.items():
		if val in vals:
			return ali
	return "not found"

class Conference(object):

	subject = ""
	day = ""
	time = ""
	mention = ""
	link = ""
	
	maybe = False
	notified = False

	def __init__(self, sub, date, time,role,maybe = False):
		self.subject = sub
		self.day = date
		self.time = time
		self.link = links[self.subject]
		self.mention = role
		self.maybe = maybe
		self.notified = False

	def respond(self):
		return "subject:" + self.subject.capitalize() + "  date:" + self.day.date().strftime("%d.%m.%Y") + "  start:" + times[self.time][0] + "  end:" + times[self.time][1] + "  maybe:" + str(self.maybe)
	
	def all(self):
		if self.maybe:
			return self.time + ": " + times[self.time][0] + "-" + times[self.time][1] + " " + self.subject.capitalize() + " maybe"
		else:
			return self.time + ": " + times[self.time][0] + "-" + times[self.time][1] + " " + self.subject.capitalize()

	def notifiy(self):
		self.notified = True
		if self.maybe:
			return (f"Maybe {self.subject.capitalize()} conference in {notificationtime} minutes for {self.mention}  {times[self.time][0]} - {times[self.time][1]} \nlink for conference {self.link}")
		else:
			return (f"{self.subject.capitalize()} conference in {notificationtime} minutes for {self.mention}  {times[self.time][0]} - {times[self.time][1]} \nlink for conference: {self.link}")

dailyall = False
hollidays = False

@tasks.loop(seconds=20)
async def notifiy():
	global dailyall, dailyalltimes
	t = datetime.datetime.now()
	if t.hour == dailyclearhour:
		async for mess in notifychannel.history(limit = 50):
			await mess.delete()
		dailyall = False
		
	if hollidays:
		return
		
	if (not dailyall and t.weekday() < 5) and ((t.hour == int(dailyalltimes[0]) and t.minute >= int(dailyalltimes[1])) or (13 > t.hour > int(dailyalltimes[0]))):
		dailyall = True
		prmap = []
		for Conference in Conferences:
			if Conference.day.date().strftime("%d.%m.%Y") == t.strftime("%d.%m.%Y"):
				prmap.append(Conference)
		print(f"\ndaily notify: {len(prmap)} conferences")
		strn = "```Python\n" + t.date().strftime("%d.%m.%Y") + ": \n"
		if len(prmap) == 0:
			strn += "No conferences today"
		else:
			for conf in sorted(prmap, key=lambda x: time.strptime(times[x.time][0], "%H.%M")):
				strn += "  " + conf.all() + "\n"
		strn += '```'
		mess = await notifychannel.send(strn)
		await mess.publish()
	
	for Conference in Conferences:
		if Conference.day.strftime("%d.%m.%Y") == t.strftime("%d.%m.%Y"):
			if (t + datetime.timedelta(minutes=notificationtime)).strftime("%H.%M") == times[Conference.time][0] and not Conference.notified:
				mess = await notifychannel.send(Conference.notifiy())
				await mess.publish()
				print("\n"+Conference.notifiy())
		if Conference.day.strftime("%d.%m.%Y") == t.strftime("%d.%m.%Y") and t.strftime("%H.%M") == (times[Conference.time][1].split('.')[0].zfill(2) + "." + str(int(times[Conference.time][1].split('.')[1])+5).zfill(2)):
			print(f"\nremoved {Conference.respond()}")
			Conferences.remove(Conference)

@commands.command()
async def add(ctx, sub, date, time, maybe=False):
	
	if replace(sub.lower()) == "not found":
		await ctx.send(f"```Subject {sub} not found \n>help \nfor information```")
		return

	if not time in times:
		await ctx.send(f"```Lesson {time} not found \n>help \nfor information```")
		return
	
	try:
		if len(date.split('.')) == 3:
			day = datetime.datetime(int(date.split('.')[2]), int(date.split('.')[1]),int(date.split('.')[0]))
		else:
			day = datetime.datetime(year, int(date.split('.')[1]),int(date.split('.')[0]))
	except:
		await ctx.send(f"```Date {date} not found \n>help \nfor information```")
		return

	idd = int(roles[replace(sub.lower())])
	
	neww = Conference(replace(sub.lower()), day, time,ctx.guild.get_role(idd).mention,maybe)
	
	double = False
	for tmp in Conferences:
		if tmp.day == neww.day and tmp.time == neww.time:
			double = tmp

	if double == False:
		Conferences.append(neww)
		await ctx.send(f"```Python\nadded {neww.respond()}```")
		print("\nadded {" + neww.respond() + "}")
	else:
		await ctx.send(f"```Python\nallready conference listed: {double.respond()} \n>remove {double.day.date().strftime('%d.%m.%Y')} {double.time} \nto delete previous entry```")
		print(f"\nallready conference listed: {double.respond() }")

bot.add_command(add)


@commands.command()
async def remove(ctx, date, time):
	if len(date.split('.')) == 3:
		day = datetime.datetime(int(date.split('.')[2]), int(date.split('.')[1]),int(date.split('.')[0]))
	else:
		day = datetime.datetime(year, int(date.split('.')[1]),int(date.split('.')[0]))

	find = False
	for tmp in Conferences:
		if tmp.day == day and tmp.time == time:
			find = tmp

	if find != False:
		Conferences.remove(find)
		await ctx.send(f"```Python\ndeleting {find.respond()}```")
		print("\ndeleted {" + find.respond() + "}")
	else:
		await ctx.send(f"```Python\nno Conference listed at: {day.date().strftime('%d.%m.%Y')} {time} \n>all \nto show all Conferences```")
		print(f"\nno Conference listed at: {day.date().strftime('%d.%m.%Y')} {time}")

bot.add_command(remove)

@commands.command()
async def rm(ctx, date, time):
	await remove(ctx, date, time);

bot.add_command(rm)


@commands.command()
async def all(ctx):
	if len(Conferences) != 0:
		prmap = {}
		for Conference in Conferences:
			try:
				prmap[Conference.day].append(Conference) 
			except KeyError:
				prmap[Conference.day] = []
				prmap[Conference.day].append(Conference)

		for dt in sorted(prmap):
			strn = "```Python\n" + dt.date().strftime("%d.%m.%Y") + ":\n"
			for conf in sorted(prmap[dt], key=lambda x: time.strptime(times[x.time][0], "%H.%M")):
				strn += "  " + conf.all() + "\n"
			strn += '```'
			await ctx.send(strn)
	else:
		await ctx.send("```Python\n No Conferences listed \n```")


bot.add_command(all)

@commands.command()
async def link(ctx, sub):
	try:
		await ctx.send(f'link for {sub} is {links[replace(sub.lower())]}')
		print(f'\nlink for {sub} is {links[replace(sub.lower())]}')
	except:
		await ctx.send(f'link for {sub} not found')
		print(f'\nlink for {sub} not found')


bot.add_command(link)

@commands.command()
async def set(ctx, args):
	global notifychannel
	if ctx.author.top_role.id == adminrole:
		notifychannel = ctx.message.guild.get_channel(int(args))
		await ctx.send(f'notifychannel changed to {notifychannel}')
		print(f'\nnotifychannel changed to {notifychannel}')
	else:
		await ctx.send("not allowed")

bot.add_command(set)

@commands.command()
async def start(ctx):
	if ctx.author.top_role.id == adminrole:
		await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening,name = ">help"))
		notifiy.start()
		await ctx.send(f'started notifing in {notifychannel}')
		print(f'\nstarted notifing in {notifychannel}')
	else:
		await ctx.send("not allowed")

bot.add_command(start)

@commands.command()
async def data(ctx):
	if ctx.author.top_role.id == adminrole:
		await ctx.send("``" + str(times) + "``")
		await ctx.send("``" + str(alias) + "``")
		await ctx.send("``" + str(roles) + "``")
		await ctx.send("``" + str(links) + "``")
		await ctx.send("``" + str(adminrole) + "``")
		await ctx.send("``" + str(notificationtime) + "``")
		await ctx.send("``" + str(dailyalltimes) + "``")
		await ctx.send("``" + str(dailyclearhour) + "``")
		await ctx.send("``" + str(year) + "``")
		print(f'\nrequested data')
	else:
		await ctx.send("not allowed")

bot.add_command(data)

@commands.command()
async def ferien(ctx,startstop):
	global hollidays
	if ctx.author.top_role.id == adminrole:
		if startstop == "start":
			hollidays = True
			await ctx.send("https://tenor.com/view/excited-hockey-kid-yeah-gif-10474493")
			print(f'\nstarted holidays')
		elif startstop == "stop":
			hollidays = False
			await ctx.send("https://tenor.com/view/disappointed-disappointed-fan-seriously-what-are-you-doing-judging-you-gif-17485289")
			print(f'\nstoped holidays')
		else:
			await ctx.send("invalid input")
	else:
		await ctx.send("not allowed")

bot.add_command(ferien)

@commands.command()
async def loadjson(ctx):
	if ctx.author.top_role.id == adminrole:
		loadjsonvalues("ConferencesBot_data.json")
		await ctx.send("json loaded")
	else:
		await ctx.send("not allowed")

bot.add_command(loadjson)

@bot.command()
async def help(ctx):
	s = "Commands:\n"

	s += ">add <subject> <date> <lesson>\n adds conference of subject to specific date and lesson\n  >add deutsch 21.01.2021 4 \n  >add info 22.05.2020 1 \n  >add en 12.02.2021 6 \n"
	s += "   all possible subjects:\n"
	for el in alias:
		s += "    "
		for al in alias[el]:
			s += al + ","
		s += "\n"
	s += "\n"

	s += ">remove <date> <lesson> / >rm <date> <lesson>\n removes conference of specific date and lesson\n  >remove 25.05.2020 3 \n  >rm 31.11.2021 5 \n"
	s += "\n"

	s += ">all\n prints all conferences\n"
	s += "\n"
	
	s += ">link <subject>\n prints link to subject's conference\n  >link geo \n  >link informatik \n all possible subjcts listed at >add \n"
	s += "\n"
	
	s += ">ontime \n prints ontime\n"
	s += "\n"

	s += "\n"
	s += "\n"

	s += "Admin commands:\n"
	s += ">set <id>\n changes notifychannel\n"
	s += "\n"
	
	s += ">start \n starts notifing\n"
	s += "\n"
	
	s += ">data \n prints data\n"
	s += "\n"

	s += ">ferien <stop/start> \n prevents the bot from notifing\n"
	s += "\n"
	
	s += ">loadjson \n reloads json data\n"
	s += "\n"

	await ctx.send(f"```{s}```")

@commands.command()
async def ontime(ctx):
	await ctx.send(f'ontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')
	print(f'\nontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')

bot.add_command(ontime)

loadjsonvalues("ConferencesBot_data.json")

bot.run(Token)
