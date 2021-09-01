import discord
from discord.ext.commands import Bot
from discord.ext import tasks, commands
from time import time
import datetime
import json

import traceback 

Token = None
Admin = None

guilds = {}

channels = []

bot = commands.Bot(command_prefix="?", help_command=None)

started = False

starttime = datetime.datetime.now()


@bot.event
async def on_ready():
    print('Ready')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="?help"))


def loadjsonvalues(path):
    global Token, guilds, Admin
    with open(path, 'r') as file:
        json_data = json.load(file)
        Token = json_data["Token"]
        Admin = int(json_data["Admin"])
        guilds = json_data["guilds"]


def savejsonvalues(path):
    with open(path, 'w') as file:
        data = {}
        data["Token"] = Token
        data["Admin"] = Admin
        data["guilds"] = guilds
        json.dump(data, file, indent=4)


class Channel:
    voiceChannel = None
    deletetime = None
    guild = None
    count = None

    def __init__(self, channel, deletetime, guild, count):
        self.voiceChannel = channel
        self.deletetime = deletetime
        self.guild = guild
        self.count = count

    def update(self, timeout):
        if self.deletetime < time() + timeout:
            self.deletetime = time() + timeout


@commands.Cog.listener()
async def on_voice_state_update(member, bevore, after):
    if after == None or not started:
        return
    if after.channel == member.guild.get_channel(int(guilds[str(member.guild.id)]["monitorchannel"])):
        if guilds[str(member.guild.id)]["countup"]:
            repeat = True
            count = 1
            while repeat:
                for channel in channels:
                    if channel.guild.id == member.guild.id and str(count) == str(channel.count).strip():
                        repeat = True
                        count += 1
                repeat = False
        else:
            count = ""

        ch = await member.guild.get_channel(int(guilds[str(member.guild.id)]["category"])).create_voice_channel(name=guilds[str(member.guild.id)]["name"] + " " + str(count), user_limit=int(guilds[str(member.guild.id)]["defaultmaxmembers"]))
        await member.move_to(ch)
        channels.append(Channel(
            ch, time() + int(guilds[str(member.guild.id)]["timeout"]), member.guild, count))
        print(f'\n{member.guild.name}:  new channel created: {ch} in {member.guild.get_channel(int(guilds[str(member.guild.id)]["category"]))}')

bot.add_listener(on_voice_state_update)


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


@bot.command()
async def category(ctx, args=None):
    if args == None:
        await ctx.channel.send(f'category = {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}')
    elif ctx.author.top_role.id == int(guilds[str(ctx.guild.id)]["adminrole"]):
        guilds[str(ctx.guild.id)]["category"] = str(args)
        savejsonvalues("VoiceChannel^2-data.json")
        await ctx.send(f'category changed to {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}')
        print(
            f'\n{ctx.guild.name}:  changed category to {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"]))}  id: {args}')
    else:
        await ctx.send("not allowed (Admin command)")


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
        savejsonvalues("VoiceChannel^2-data.json")
        await ctx.send(f'timeout changed to {guilds[str(ctx.guild.id)]["timeout"]}')
        print(
            f'\n{ctx.guild.name}:  changed timeout to {guilds[str(ctx.guild.id)]["timeout"]}  time: {args}')
    else:
        await ctx.send("not allowed (Admin command)")


@bot.command()
async def rename(ctx, *args):
    if ctx.author.voice == None:
        await ctx.send('You have to be connected to a voice channel')
        return

    for Channel in channels:
        if Channel.voiceChannel == ctx.author.voice.channel:
            ch = Channel

    if ch == None:
        await ctx.send(f'You have to be connected to a {guilds[str(ctx.guild.id)]["name"]} channel')
        return
	
    st = ""
    for s in args:
        st += s + " "
	
    ch.count = -1
	
    await ctx.send(f'{ch.voiceChannel.name} renamed to {st.strip()}')
    print(f'\n{ctx.guild.name}:  {ch.voiceChannel.name} renamed to {st.strip()}')
    
    await ch.voiceChannel.edit(name=st.strip())
	
	

@bot.command()
async def pause(ctx, args=None):
    if ctx.author.voice == None:
        await ctx.send('You have to be connected to a voice channel')
        return

    for Channel in channels:
        if Channel.voiceChannel == ctx.author.voice.channel:
            ch = Channel

    if ch == None:
        await ctx.send(f'You have to be connected to a {guilds[str(ctx.guild.id)]["name"]} channel')
        return

    try:
        int(args)
    except Exception:
        await ctx.send(f'invalid pause time: {args}min')
        return

    if not 5 <= int(args) <= int(guilds[str(ctx.guild.id)]["maxpause"]):
        await ctx.send(f'invalid pause time: {args}min \nmust be between 5min and {guilds[str(ctx.guild.id)]["maxpause"]}min')
        return

    ch.update(int(args)*60)
    await ctx.send(f'{ch.voiceChannel} paused for {int(args)}min')
    print(f'\n{ctx.guild.name}:  {ch.voiceChannel} paused for {int(args)}min / {int(args)*60}sec')


@bot.command()
async def limit(ctx, args=None):
    if ctx.author.voice == None:
        await ctx.send('You have to be connected to a voice channel')
        return
    ch = None
    for Channel in channels:
        if Channel.voiceChannel == ctx.author.voice.channel:
            ch = Channel

    if ch == None:
        await ctx.send(f'You have to be connected to a {guilds[str(ctx.guild.id)]["name"]} channel')
        return

    try:
        int(args)
    except Exception:
        await ctx.send(f'invalid  member count: {args}')
        return

    if not 0 <= int(args) <= int(guilds[str(ctx.guild.id)]["maxmembers"]):
        await ctx.send(f'invalid member count: {args} \nmust be between 0 and {guilds[str(ctx.guild.id)]["maxmembers"]}')
        return

    await ch.voiceChannel.edit(user_limit=int(args))
    await ctx.send(f'{ch.voiceChannel} max members set to {int(args)}')
    print(f'\n{ctx.guild.name}:  {ch.voiceChannel} max members set to {int(args)}')


@bot.command()
async def create(ctx, *args):
    if ctx.author.top_role.id == int(guilds[str(ctx.guild.id)]["adminrole"]):
        st = ""
        for s in args:
            st += s + " "
        ch = await ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["category"])).create_voice_channel(name=st, user_limit=1)

        guilds[str(ctx.guild.id)]["monitorchannel"] = str(ch.id)
        savejsonvalues("VoiceChannel^2-data.json")
        await ctx.send(f'creationchannel created: {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["monitorchannel"]))}')
        print(
            f'\n{ctx.guild.name}:  creationchannel created: {ctx.guild.get_channel(int(guilds[str(ctx.guild.id)]["monitorchannel"]))}  id: {ch.id}')
    else:
        await ctx.send("not allowed (Admin command)")


@bot.command()
async def setup(ctx, countup, defaultmaxmembers, maxmembers, maxpause):
    if ctx.author.top_role.id == int(guilds[str(ctx.guild.id)]["adminrole"]):
        try:
            if countup != None and countup != "l" and countup != "no":
                guilds[str(ctx.guild.id)]["countup"] = countup == "True"
                await ctx.send(f'countup changed to {guilds[str(ctx.guild.id)]["countup"]}')
                print(f'\n{ctx.guild.name}:  countup changed to {guilds[str(ctx.guild.id)]["countup"]} {countup}')
            if defaultmaxmembers != None and defaultmaxmembers != "l" and defaultmaxmembers != "no":
                guilds[str(ctx.guild.id)]["defaultmaxmembers"] = int(defaultmaxmembers)
                await ctx.send(f'defaultmaxmembers changed to {guilds[str(ctx.guild.id)]["defaultmaxmembers"]}')
                print(f'\n{ctx.guild.name}:  defaultmaxmembers changed to {guilds[str(ctx.guild.id)]["defaultmaxmembers"]} {defaultmaxmembers}')
            if maxmembers != None and maxmembers != "l" and maxmembers != "no":
                guilds[str(ctx.guild.id)]["maxmembers"] = int(maxmembers)
                await ctx.send(f'maxmembers changed to {guilds[str(ctx.guild.id)]["maxmembers"]}')
                print(f'\n{ctx.guild.name}:  maxmembers changed to {guilds[str(ctx.guild.id)]["maxmembers"]} {maxmembers}')
            if maxpause != None and maxpause != "l" and maxpause != "no":
                guilds[str(ctx.guild.id)]["maxpause"] = int(maxpause)
                await ctx.send(f'maxpause changed to {guilds[str(ctx.guild.id)]["maxpause"]}')
                print(f'\n{ctx.guild.name}:  maxpause changed to {guilds[str(ctx.guild.id)]["maxpause"]} {maxpause}')
            savejsonvalues("VoiceChannel^2-data.json")
            
        except Exception as e:
            await ctx.send(f'some error occured: {e}')

    else:
        await ctx.send("not allowed (Admin command)")


@bot.command()
async def name(ctx, *args):
    if len(args) == 0:
        await ctx.channel.send(f'Name = {guilds[str(ctx.guild.id)]["name"]}')
    elif ctx.author.top_role.id == int(guilds[str(ctx.guild.id)]["adminrole"]):
        st = ""
        for s in args:
            st += s + " "
        if st.find("\"") != -1:
            await ctx.send(f'" not allowed {st}')
            print(f'\n{ctx.guild.name}:  " not allowed {st}')
            return
        guilds[str(ctx.guild.id)]["name"] = str(st).strip()
        savejsonvalues("VoiceChannel^2-data.json")
        await ctx.send(f'name changed to {guilds[str(ctx.guild.id)]["name"]}')
        print(
            f'\n{ctx.guild.name}:  name changed to {guilds[str(ctx.guild.id)]["name"]}')
    else:
        await ctx.send("not allowed (Admin command)")


@bot.command()
async def start(ctx):
    global started
    if ctx.author.id == Admin:
        started = True
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="?help"))
        testing.start()
        await ctx.send(f'started')
        print(f'\nstarted')
    else:
        await ctx.send("not allowed (owner command)")


@bot.command()
async def setadmin(ctx, args):
    global guilds
    if ctx.author.id == Admin:
        guilds[str(ctx.guild.id)] = {"category": None, "timeout": "120", "name": "New VC", "countup": True,"defaultmaxmembers": "3", "maxmembers": "12", "maxpause": "120","monitorchannel": None, "adminrole": str(args)}
        savejsonvalues("VoiceChannel^2-data.json")
        await ctx.send(f'server adminrole changed to {ctx.guild.get_role(int(args))}')
        print(
            f'\n{ctx.guild.name}:  server adminrole changed to {ctx.guild.get_role(int(args))}')
    else:
        await ctx.send("not allowed (owner command)")


@bot.command()
async def help(ctx):
    s = "Commands:\n"

    s += "?category \n prints category\n"
    s += "\n"

    s += "?timeout \n prints timeout\n"
    s += "\n"

    s += "?pause <time> \n prevents the channel from getting deleted for <time> min\n"
    s += "\n"

    s += "?limit <members> \n changes max members to <members> \n"
    s += "\n"

    s += "?rename <name>\n changes name of current channel\n"
    s += "\n"

    s += "?name \n prints name of new created channels\n"
    s += "\n"

    s += "?ontime \n prints ontime\n"
    s += "\n"

    s += "\n"
    s += "\n"

    s += "Admin commands:\n"

    s += "?category <id>\n changes category\n"
    s += "\n"

    s += "?timeout <sec>\n changes timeout\n"
    s += "\n"

    s += "?create <name>\n creates creation channel\n"
    s += "\n"

    s += "?name <name>\n changes name of new created channels \n"
    s += "\n"

    s += "?setup <countup> <defaultmaxmembers> <maxmembers> <maxpause>\n changes some default values \n"
    s += "\n"

    s += "\n"
    s += "\n"

    s += "Owner commands:\n"

    s += "?start\n starts deleting channels\n"
    s += "\n"

    s += "?setadmin <id>\n adds guild to json file and changes admin role id\n"
    s += "\n"

    await ctx.send(f"```{s}```")


@bot.command()
async def ontime(ctx):
    await ctx.send(f'ontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')
    print(
        f'\nontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')

loadjsonvalues("VoiceChannel^2-data.json")

bot.run(Token)