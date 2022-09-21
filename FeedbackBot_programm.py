import datetime
import json
from datetime import timezone

import discord
from discord.ext import tasks, commands
from discord.ext.commands import Context

Token = None
Admin = None

reportchannel = None

deletetimeint = 180

started = False

bot = commands.Bot(command_prefix="|", help_command=None)

starttime = datetime.datetime.now()


@bot.event
async def on_ready():
    print('Ready')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="|help"))


def loadjsonvalues(path: str):
    global Token, Admin, reportchannel, deletetimeint
    with open(path, 'r') as file:
        json_data = json.load(file)
        Token = json_data["Token"]
        Admin = json_data["Admin"]
        reportchannel = json_data["reportchannel"]
        deletetimeint = json_data["deletetimeint"]

def savejsonvalues(path: str):
    with open(path, 'w') as file:
        data = {"Token": Token, "Admin": Admin, "reportchannel": reportchannel, "deletetimeint": deletetimeint}
        json.dump(data, file, indent=2)

@tasks.loop(seconds=5)
async def testing():
    try:
        utc = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(0, deletetimeint)
        async for mess in reportchannel.history(limit=50):
            if mess.created_at.replace(tzinfo=timezone.utc) < utc and mess.author == bot.user:
                await mess.delete()
    except Exception as e:
        print(e)


@commands.Cog.listener()
async def on_voice_state_update(member, bevore, after):
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
    except Exception as e:
        print(f'\n{str(datetime.datetime.now())}:  Exception: {e}, Member: {member}') 


bot.add_listener(on_voice_state_update)


@bot.command()
async def channel(ctx: Context, args: str = None):
    global reportchannel
    if args is None:
        await ctx.channel.send(f'reportchannel = {reportchannel}')
    elif ctx.author.top_role.id == Admin:
        try:
            int(args)
        except TypeError:
            await ctx.send(f'reportchannel id must be a number {args}')
            print(f'\nreportchannel id must be a number {args}')
            return
        reportchannel = ctx.guild.get_channel(int(args))
        savejsonvalues("FeedbackBot_data.json")
        await ctx.send(f'reportchannel changed to {reportchannel}')
        print(f'\nreportchannel changed to {reportchannel}')
    else:
        await ctx.send("not allowed (Admin Command)")


@bot.command()
async def deletetime(ctx: Context, args: str = None):
    global deletetimeint
    if args == None:
        await ctx.channel.send(f'deletetime = {deletetimeint} sec')
    elif ctx.author.top_role.id == Admin:
        try:
            int(args)
        except TypeError:
            await ctx.send(f'deletetime must be a number {args}')
            print(f'\ndeletetime must be a number {args}')
            return
        deletetimeint = int(args)
        savejsonvalues("FeedbackBot_data.json")
        await ctx.channel.send(f'deletetime changed to {deletetimeint} sec')
        print(f'\ndeletetime changed to {deletetimeint} sec')
    else:
        await ctx.send("not allowed (Admin Command)")


@bot.command()
async def start(ctx: Context):
    global started
    if ctx.author.top_role.id == Admin:
        started = True
        await bot.change_presence(status=discord.Status.online,
                                  activity=discord.Activity(type=discord.ActivityType.listening, name="|help"))
        if not testing.is_running(): 
            testing.start()

        await ctx.send('started')
        print('\nstarted')
    else:
        await ctx.send("not allowed (Admin Command)")


@bot.command()
async def help(ctx: Context):
    s = "Commands:\n"

    s += "|channel \n prints notification channel\n"
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

    s += "|deletetime <sec> \n sets deletetime\n"
    s += "\n"

    await ctx.send(f"```{s}```")


@bot.command()
async def ontime(ctx: Context):
    await ctx.send(f'ontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')
    print(f'\nontime: {str(datetime.datetime.now() - starttime).split(".")[0]}')


if __name__ == "__main__":
	loadjsonvalues("FeedbackBot_data.json")
	bot.run(Token)
