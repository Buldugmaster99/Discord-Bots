import discord
from discord.ext.commands import Context

import datetime

import VoiceChannelBot_globals as Globals


@Globals.bot.command()
async def category(ctx: Context, args: str = None):
    if args is None:
        await ctx.channel.send(f'category = {ctx.guild.get_channel(Globals.guilds[str(ctx.guild.id)]["category"])}')
    elif ctx.author.top_role.id == Globals.guilds[str(ctx.guild.id)]["adminrole"]:
        try:
            int(args)
        except TypeError:
            await ctx.send(f'category id must be a number {args}')
            print(f'\ncategory id must be a number {args}')
            return
        Globals.guilds[str(ctx.guild.id)]["category"] = int(args)
        Globals.savejsonvalues(Globals.datafile)
        await ctx.send(f'category changed to {ctx.guild.get_channel(Globals.guilds[str(ctx.guild.id)]["category"])}')
        print(
            f'\n{ctx.guild.name}:  changed category to {ctx.guild.get_channel(Globals.guilds[str(ctx.guild.id)]["category"])}  args: {args}')
    else:
        await ctx.send("not allowed (Admin command)")


@Globals.bot.command()
async def timeout(ctx: Context, args: str = None):
    if args is None:
        await ctx.channel.send(f'timeout = {Globals.guilds[str(ctx.guild.id)]["timeout"]}')
    elif ctx.author.top_role.id == Globals.guilds[str(ctx.guild.id)]["adminrole"]:
        try:
            int(args)
        except TypeError:
            await ctx.send(f'timeout must be a number {args}')
            print(f'\ntimeout must be a number {args}')
            return
        Globals.guilds[str(ctx.guild.id)]["timeout"] = int(args)
        Globals.savejsonvalues(Globals.datafile)
        await ctx.send(f'timeout changed to {Globals.guilds[str(ctx.guild.id)]["timeout"]}')
        print(f'\n{ctx.guild.name}:  changed timeout to {Globals.guilds[str(ctx.guild.id)]["timeout"]}  args: {args}')
    else:
        await ctx.send("not allowed (Admin command)")


@Globals.bot.command()
async def create(ctx: Context, *args: str):
    if ctx.author.top_role.id == Globals.guilds[str(ctx.guild.id)]["adminrole"]:
        st = ""
        for s in args:
            st += s + " "
        ch = await ctx.guild.get_channel(Globals.guilds[str(ctx.guild.id)]["category"]).create_voice_channel(name=st, user_limit=1)

        Globals.guilds[str(ctx.guild.id)]["monitorchannel"] = ch.id
        Globals.savejsonvalues(Globals.datafile)
        await ctx.send(f'creationchannel created: {ctx.guild.get_channel(Globals.guilds[str(ctx.guild.id)]["monitorchannel"])}')
        print(
            f'\n{ctx.guild.name}:  creationchannel created: {ctx.guild.get_channel(Globals.guilds[str(ctx.guild.id)]["monitorchannel"])}  args: {args}')
    else:
        await ctx.send("not allowed (Admin command)")


@Globals.bot.command()
async def setup(ctx: Context, countup: str, defaultmaxmembers: str, maxmembers: str, maxpause: str):
    if ctx.author.top_role.id == Globals.guilds[str(ctx.guild.id)]["adminrole"]:
        try:
            if countup is not None and countup != "-" and countup != "no":
                Globals.guilds[str(ctx.guild.id)]["countup"] = countup.capitalize() == "True" or countup == "1"
                await ctx.send(f'countup changed to {Globals.guilds[str(ctx.guild.id)]["countup"]}')
                print(f'\n{ctx.guild.name}:  countup changed to {Globals.guilds[str(ctx.guild.id)]["countup"]} {countup}')

            if defaultmaxmembers is not None and defaultmaxmembers != "-" and defaultmaxmembers != "no":
                Globals.guilds[str(ctx.guild.id)]["defaultmaxmembers"] = int(defaultmaxmembers)
                await ctx.send(f'defaultmaxmembers changed to {Globals.guilds[str(ctx.guild.id)]["defaultmaxmembers"]}')
                print(
                    f'\n{ctx.guild.name}:  defaultmaxmembers changed to {Globals.guilds[str(ctx.guild.id)]["defaultmaxmembers"]} {defaultmaxmembers}')

            if maxmembers is not None and maxmembers != "-" and maxmembers != "no":
                Globals.guilds[str(ctx.guild.id)]["maxmembers"] = int(maxmembers)
                await ctx.send(f'maxmembers changed to {Globals.guilds[str(ctx.guild.id)]["maxmembers"]}')
                print(f'\n{ctx.guild.name}:  maxmembers changed to {Globals.guilds[str(ctx.guild.id)]["maxmembers"]} {maxmembers}')

            if maxpause is not None and maxpause != "-" and maxpause != "no":
                Globals.guilds[str(ctx.guild.id)]["maxpause"] = int(maxpause)
                await ctx.send(f'maxpause changed to {Globals.guilds[str(ctx.guild.id)]["maxpause"]}')
                print(f'\n{ctx.guild.name}:  maxpause changed to {Globals.guilds[str(ctx.guild.id)]["maxpause"]} {maxpause}')
            Globals.savejsonvalues(Globals.datafile)

        except Exception as e:
            await ctx.send(f'error occured: {e}')

    else:
        await ctx.send("not allowed (Admin command)")


@Globals.bot.command()
async def name(ctx: Context, *args: str):
    if len(args) == 0:
        await ctx.channel.send(f'Name = {Globals.guilds[str(ctx.guild.id)]["name"]}')
    elif ctx.author.top_role.id == Globals.guilds[str(ctx.guild.id)]["adminrole"]:
        st = ""
        for s in args:
            st += s + " "

        Globals.guilds[str(ctx.guild.id)]["name"] = st.strip()
        Globals.savejsonvalues(Globals.datafile)
        await ctx.send(f'name changed to {Globals.guilds[str(ctx.guild.id)]["name"]}')
        print(f'\n{ctx.guild.name}:  name changed to {Globals.guilds[str(ctx.guild.id)]["name"]}')
    else:
        await ctx.send("not allowed (Admin command)")


@Globals.bot.command()
async def rename(ctx: Context, *args: str):
    if ctx.author.voice is None:
        await ctx.send('You have to be connected to a voice channel')
        return

    ch: Globals.Channel = None

    for Channel in Globals.channels:
        if Channel.voiceChannel == ctx.author.voice.channel:
            ch = Channel

    if ch is None:
        await ctx.send(f'You have to be connected to a {Globals.guilds[str(ctx.guild.id)]["name"]} channel')
        return

    st: str = ""
    for s in args:
        st += s + " "

    ch.count = -1

    await ctx.send(f'{ch.voiceChannel.name} renamed to {st.strip()}')
    print(f'\n{ctx.guild.name}:  {ch.voiceChannel.name} renamed to {st.strip()}')

    await ch.voiceChannel.edit(name=st.strip())


@Globals.bot.command()
async def pause(ctx: Context, args: str = None):
    if ctx.author.voice is None:
        await ctx.send('You have to be connected to a voice channel')
        return

    ch = None

    for Channel in Globals.channels:
        if Channel.voiceChannel == ctx.author.voice.channel:
            ch = Channel

    if ch is None:
        await ctx.send(f'You have to be connected to a {Globals.guilds[str(ctx.guild.id)]["name"]} channel')
        return

    try:
        int(args)
    except TypeError:
        await ctx.send(f'invalid pause time: {args}min')
        return

    if not 5 <= int(args) <= Globals.guilds[str(ctx.guild.id)]["maxpause"]:
        await ctx.send(f'invalid pause time: {args} min \nmust be between 5 min and {Globals.guilds[str(ctx.guild.id)]["maxpause"]} min')
        return

    ch.update(int(args) * 60)
    await ctx.send(f'{ch.voiceChannel} paused for {int(args)} min')
    print(f'\n{ctx.guild.name}:  {ch.voiceChannel} paused for {int(args)} min / {int(args) * 60} sec')


@Globals.bot.command()
async def limit(ctx: Context, args: str = None):
    if ctx.author.voice is None:
        await ctx.send('You have to be connected to a voice channel')
        return

    ch: Globals.Channel = None
    for Channel in Globals.channels:
        if Channel.voiceChannel == ctx.author.voice.channel:
            ch = Channel

    if ch is None:
        await ctx.send(f'You have to be connected to a {Globals.guilds[str(ctx.guild.id)]["name"]} channel')
        return

    try:
        int(args)
    except TypeError:
        await ctx.send(f'invalid limit count: {args}')
        return

    if not 0 <= int(args) <= Globals.guilds[str(ctx.guild.id)]["maxmembers"]:
        await ctx.send(f'invalid limit count: {args} \nmust be between 0 and {Globals.guilds[str(ctx.guild.id)]["maxmembers"]}')
        return

    await ch.voiceChannel.edit(user_limit=int(args))
    await ctx.send(f'{ch.voiceChannel} limit set to {int(args)}')
    print(f'\n{ctx.guild.name}:  {ch.voiceChannel} limit set to {int(args)}')


@Globals.bot.command()
async def start(ctx: Context):
    if ctx.author.id == Globals.Admin:
        Globals.started = True
        await Globals.bot.change_presence(status=discord.Status.online,
                                          activity=discord.Activity(type=discord.ActivityType.listening, name="?help"))
        if not Globals.testing.is_running:
            Globals.testing.start()
        await ctx.send(f'started')
        print(f'\nstarted')
    else:
        await ctx.send("not allowed (owner command)")


@Globals.bot.command()
async def setadmin(ctx: Context, args: str):
    if ctx.author.id == Globals.Admin:
        try:
            int(args)
        except TypeError:
            await ctx.send(f'adminrole must be a number {args}')
            print(f'\nadminrole must be a number {args}')
            return

        Globals.guilds[str(ctx.guild.id)] = {"category": None, "timeout": 120, "name": "New Channel", "countup": True,
                                             "defaultmaxmembers": 3, "maxmembers": 12, "maxpause": 120, "monitorchannel": None,
                                             "adminrole": int(args)}
        Globals.savejsonvalues(Globals.datafile)
        await ctx.send(f'server adminrole changed to {ctx.guild.get_role(int(args))}')
        print(f'\n{ctx.guild.name}:  server adminrole changed to {ctx.guild.get_role(int(args))}')
    else:
        await ctx.send("not allowed (owner command)")


@Globals.bot.command()
async def help(ctx: Context):
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

    s += "?ontime \n prints time the bot is online\n"
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

    s += "?setup <countup> <defaultmaxmembers> <maxmembers> <maxpause>\n changes some values for guild \n"
    s += "\n"

    s += "\n"
    s += "\n"

    s += "Owner commands:\n"

    s += "?start\n starts deleting channels\n"
    s += "\n"

    s += "?setadmin <id>\n adds guild to json file and changes admin role id\n"
    s += "\n"

    await ctx.send(f"```{s}```")


@Globals.bot.command()
async def ontime(ctx: Context):
    await ctx.send(f'ontime: {str(datetime.datetime.now() - Globals.starttime).split(".")[0]}')
    print(f'\nontime: {str(datetime.datetime.now() - Globals.starttime).split(".")[0]}')
