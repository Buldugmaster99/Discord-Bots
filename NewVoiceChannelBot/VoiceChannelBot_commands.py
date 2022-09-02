import logging

import interactions
from interactions import Channel, Guild
from interactions.client.context import CommandContext
from interactions.client.enums import OptionType
from interactions.client.models import Option

import VoiceChannelBot_globals as Globals


@Globals.bot.command(
    name="config",
    description="configures this bot, used by server admin",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    dm_permission=False,
    scope=Globals.ids,
    options=[
        Option(
            name="category",
            description="Category to create VoiceChannels in",
            type=OptionType.CHANNEL,
            required=False,
        ),
        Option(
            name="timeout",
            description="Timeout in seconds after Channels get deleted [0 - 1800]",
            type=OptionType.NUMBER,
            required=False,
            min_value=0,
            max_value=1800
        ),
        Option(
            name="monitor_voice_channel",
            description="VoiceChannel to monitor and create new VoiceChannel if someone joins it",
            type=OptionType.CHANNEL,
            required=False
        ),
        Option(
            name="new_channel_name",
            description="Name of new Channels created by Bot (add {} to add upcounting number)",
            type=OptionType.STRING,
            required=False
        ),
        Option(
            name="default_max_members",
            description="Max Members allowed in VoiceChannel after it was created (change for current VoiceChannel with /limit)",
            type=OptionType.NUMBER,
            required=False,
            min_value=1,
            max_value=99
        ),
    ]
)
async def _config(ctx: CommandContext, category: Channel = None, timeout: int = None, monitor_voice_channel: Channel = None,
                  new_channel_name: str = None, default_max_members: int = None):
    try:
        guild = await ctx.get_guild()
        my_guild = await _checkGuild(int(ctx.guild_id))

        mess = "```\n"
        mess += await _handle_category(category, guild, my_guild) + "\n"
        mess += await _handle_timeout(timeout, guild, my_guild) + "\n"
        mess += await _handle_monitor_VoiceChannel(monitor_voice_channel, guild, my_guild) + "\n"
        mess += await _handle_new_channel_name(new_channel_name, guild, my_guild) + "\n"
        mess += await _handle_default_max_members(default_max_members, guild, my_guild) + "\n"
        mess += "```"

        await ctx.send(mess)
    except Globals.CommandException as e:
        await ctx.send(f"Exception occurred: {e}")  # show custom exceptions
        logging.error(f"Exception occurred {e}")
        return
    except Exception as e:
        await ctx.send(f"Exception occurred")  # hide real exceptions
        logging.error(f"Exception occurred {e}")
        return


async def _checkGuild(guild_id: int) -> Globals.CustomGuild:
    guild = Globals.guilds[guild_id]

    if guild is None:
        Globals.err(f"No category registered for this guild; id:{guild_id}")
        raise Globals.CommandException("Guild not registered (BotAdmin needs to register guild)")

    return guild


async def _handle_category(_category: Channel | None, _guild: Guild, _my_guild: Globals.CustomGuild) -> str:
    if _category is None:
        if _my_guild.category_id is None:
            Globals.err("No category registered for this guild", _guild)
            raise Globals.CommandException("No category registered for this guild")

        category = next((ch for ch in await _guild.get_all_channels() if ch.id == _my_guild.category_id), None)
        if category is None:
            Globals.err(f"Category registered for this guild wasn't found; categoryId:[{_my_guild.category_id}]", _guild)
            raise Globals.CommandException("Category registered for this guild wasn't found (probably deleted)")

        return f"  category: {category}"
    else:
        if _category.type is not interactions.ChannelType.GUILD_CATEGORY:
            Globals.err(f"category must be a category; channel:{_category.name}[{_category.id}]", _guild)
            raise Globals.CommandException(f"category must be a Category: {_category.name}")

        _my_guild.category_id = _category.id
        # TODO save

        Globals.log(f"changed category to {_category.name}; channel:{_category.name}[{_category.id}]", _guild)
        return f"↣ changed category to {_category.name}"


async def _handle_timeout(_timeout: int | None, _guild: Guild, _my_guild: Globals.CustomGuild) -> str:
    if _timeout is None:
        if _my_guild.timeout is None:
            Globals.err("No timeout defined for this guild", _guild)
            raise Globals.CommandException("No timeout defined for this guild")

        return f"  timeout: {_my_guild.timeout}"
    else:
        _my_guild.timeout = _timeout
        # TODO save

        Globals.log(f"changed timeout to {_timeout}", _guild)
        return f"↣ changed timeout to {_timeout}"


async def _handle_monitor_VoiceChannel(_monitor_VoiceChannel: Channel | None, _guild: Guild, _my_guild: Globals.CustomGuild) -> str:
    if _monitor_VoiceChannel is None:
        if _my_guild.monitor_voice_channel_id is None:
            Globals.err("No monitor_voice_channel registered for this guild", _guild)
            raise Globals.CommandException("No monitor_voice_channel registered for this guild")

        monitor_VoiceChannel = next((ch for ch in await _guild.get_all_channels() if ch.id == _my_guild.monitor_voice_channel_id), None)
        if monitor_VoiceChannel is None:
            Globals.err(
                f"monitor_voice_channel registered for this guild wasn't found; monitor_voice_channelId:[{_my_guild.monitor_voice_channel_id}]",
                _guild)
            raise Globals.CommandException("monitor_voice_channel registered for this guild wasn't found (probably deleted)")

        return f"  monitor_voice_channel: {monitor_VoiceChannel}"
    else:
        if _monitor_VoiceChannel.type is not interactions.ChannelType.GUILD_VOICE:
            Globals.err(f"monitor_voice_channel must be a VoiceChannel; channel:{_monitor_VoiceChannel.name}[{_monitor_VoiceChannel.id}]",
                        _guild)
            raise Globals.CommandException(f"monitor_voice_channel must be a VoiceChannel: {_monitor_VoiceChannel.name}")

        _my_guild.monitor_voice_channel_id = _monitor_VoiceChannel.id
        # TODO save

        Globals.log(
            f"changed monitor_voice_channel to {_monitor_VoiceChannel.name}; channel:{_monitor_VoiceChannel.name}[{_monitor_VoiceChannel.id}]",
            _guild)
        return f"↣ changed monitor_voice_channel to {_monitor_VoiceChannel.name}"


async def _handle_new_channel_name(_new_channel_name: str | None, _guild: Guild, _my_guild: Globals.CustomGuild) -> str:
    if _new_channel_name is None:
        if _my_guild.new_channel_name is None:
            Globals.err("No new_channel_name defined for this guild", _guild)
            raise Globals.CommandException("No new_channel_name defined for this guild")

        return f"  monitor_voice_channel: {_my_guild.new_channel_name}"
    else:
        _my_guild.new_channel_name = _new_channel_name
        # TODO save

        Globals.log(f"changed new_channel_name to {_new_channel_name}", _guild)
        return f"↣ changed new_channel_name to {_new_channel_name}"


async def _handle_default_max_members(_default_max_members: int | None, _guild: Guild, _my_guild: Globals.CustomGuild) -> str:
    if _default_max_members is None:
        if _my_guild.default_max_members is None:
            Globals.err("No default_max_members defined for this guild", _guild)
            raise Globals.CommandException("No default_max_members defined for this guild")

        return f"  default_max_members: {_my_guild.default_max_members}"
    else:
        _my_guild.default_max_members = _default_max_members
        # TODO save

        Globals.log(f"changed default_max_members to {_default_max_members}", _guild)
        return f"↣ changed default_max_members to {_default_max_members}"

#
# @Globals.bot.command()
# async def name(ctx: Context, *args: str):
#     if len(args) == 0:
#         await ctx.channel.send(f"Name = {Globals.guilds[str(ctx.guild.id)]["name"]}")
#     elif ctx.author.top_role.id == Globals.guilds[str(ctx.guild.id)]["adminrole"]:
#         st = ""
#         for s in args:
#             st += s + " "
#
#         Globals.guilds[str(ctx.guild.id)]["name"] = st.strip()
#         Globals.savejsonvalues(Globals.datafile)
#         await ctx.send(f"name changed to {Globals.guilds[str(ctx.guild.id)]["name"]}")
#         print(f"\n{ctx.guild.name}:  name changed to {Globals.guilds[str(ctx.guild.id)]["name"]}")
#     else:
#         await ctx.send("not allowed (Admin command)")
#
#
# @Globals.bot.command()
# async def rename(ctx: Context, *args: str):
#     if ctx.author.voice is None:
#         await ctx.send("You have to be connected to a voice channel")
#         return
#
#     ch: Globals.Channel = None
#
#     for Channel in Globals.channels:
#         if Channel.voiceChannel == ctx.author.voice.channel:
#             ch = Channel
#
#     if ch is None:
#         await ctx.send(f"You have to be connected to a {Globals.guilds[str(ctx.guild.id)]["name"]} channel")
#         return
#
#     st: str = ""
#     for s in args:
#         st += s + " "
#
#     ch.count = -1
#
#     await ctx.send(f"{ch.voiceChannel.name} renamed to {st.strip()}")
#     print(f"\n{ctx.guild.name}:  {ch.voiceChannel.name} renamed to {st.strip()}")
#
#     await ch.voiceChannel.edit(name=st.strip())
#
#
# @Globals.bot.command()
# async def pause(ctx: Context, args: str = None):
#     if ctx.author.voice is None:
#         await ctx.send("You have to be connected to a voice channel")
#         return
#
#     ch = None
#
#     for Channel in Globals.channels:
#         if Channel.voiceChannel == ctx.author.voice.channel:
#             ch = Channel
#
#     if ch is None:
#         await ctx.send(f"You have to be connected to a {Globals.guilds[str(ctx.guild.id)]["name"]} channel")
#         return
#
#     try:
#         int(args)
#     except TypeError:
#         await ctx.send(f"invalid pause time: {args}min")
#         return
#
#     if not 5 <= int(args) <= Globals.guilds[str(ctx.guild.id)]["maxpause"]:
#         await ctx.send(f"invalid pause time: {args} min \nmust be between 5 min and {Globals.guilds[str(ctx.guild.id)]["maxpause"]} min")
#         return
#
#     ch.update(int(args) * 60)
#     await ctx.send(f"{ch.voiceChannel} paused for {int(args)} min")
#     print(f"\n{ctx.guild.name}:  {ch.voiceChannel} paused for {int(args)} min / {int(args) * 60} sec")
#
#
# @Globals.bot.command()
# async def limit(ctx: Context, args: str = None):
#     if ctx.author.voice is None:
#         await ctx.send("You have to be connected to a voice channel")
#         return
#
#     ch: Globals.Channel = None
#     for Channel in Globals.channels:
#         if Channel.voiceChannel == ctx.author.voice.channel:
#             ch = Channel
#
#     if ch is None:
#         await ctx.send(f"You have to be connected to a {Globals.guilds[str(ctx.guild.id)]["name"]} channel")
#         return
#
#     try:
#         int(args)
#     except TypeError:
#         await ctx.send(f"invalid limit count: {args}")
#         return
#
#     if not 0 <= int(args) <= Globals.guilds[str(ctx.guild.id)]["maxmembers"]:
#         await ctx.send(f"invalid limit count: {args} \nmust be between 0 and {Globals.guilds[str(ctx.guild.id)]["maxmembers"]}")
#         return
#
#     await ch.voiceChannel.edit(user_limit=int(args))
#     await ctx.send(f"{ch.voiceChannel} limit set to {int(args)}")
#     print(f"\n{ctx.guild.name}:  {ch.voiceChannel} limit set to {int(args)}")
#
#
# @Globals.bot.command()
# async def start(ctx: Context):
#     if ctx.author.id == Globals.Admin:
#         Globals.started = True
#         await Globals.bot.change_presence(status=discord.Status.online,
#                                           activity=discord.Activity(type=discord.ActivityType.listening, name="?help"))
#
#         if not Globals.testing.is_running():
#             Globals.testing.start()
#         await ctx.send(f"started")
#         print(f"\nstarted")
#     else:
#         await ctx.send("not allowed (owner command)")
#
#
# @Globals.bot.command()
# async def setadmin(ctx: Context, args: str):
#     if ctx.author.id == Globals.Admin:
#         try:
#             int(args)
#         except TypeError:
#             await ctx.send(f"adminrole must be a number {args}")
#             print(f"\nadminrole must be a number {args}")
#             return
#
#         Globals.guilds[str(ctx.guild.id)] = {"category": None, "timeout": 120, "name": "New Channel", "countup": True,
#                                              "defaultmaxmembers": 3, "maxmembers": 12, "maxpause": 120, "monitorchannel": None,
#                                              "adminrole": int(args)}
#         Globals.savejsonvalues(Globals.datafile)
#         await ctx.send(f"server adminrole changed to {ctx.guild.get_role(int(args))}")
#         print(f"\n{ctx.guild.name}:  server adminrole changed to {ctx.guild.get_role(int(args))}")
#     else:
#         await ctx.send("not allowed (owner command)")
#
#
# @Globals.bot.command()
# async def help(ctx: Context):
#     s = "Commands:\n"
#
#     s += "?category \n prints category\n"
#     s += "\n"
#
#     s += "?timeout \n prints timeout\n"
#     s += "\n"
#
#     s += "?pause <time> \n prevents the channel from getting deleted for <time> min\n"
#     s += "\n"
#
#     s += "?limit <members> \n changes max members to <members> \n"
#     s += "\n"
#
#     s += "?rename <name>\n changes name of current channel\n"
#     s += "\n"
#
#     s += "?name \n prints name of new created channels\n"
#     s += "\n"
#
#     s += "?ontime \n prints time the bot is online\n"
#     s += "\n"
#
#     s += "\n"
#     s += "\n"
#
#     s += "Admin commands:\n"
#
#     s += "?category <id>\n changes category\n"
#     s += "\n"
#
#     s += "?timeout <sec>\n changes timeout\n"
#     s += "\n"
#
#     s += "?create <name>\n creates creation channel\n"
#     s += "\n"
#
#     s += "?name <name>\n changes name of new created channels \n"
#     s += "\n"
#
#     s += "?setup <countup> <defaultmaxmembers> <maxmembers> <maxpause>\n changes some values for guild \n"
#     s += "\n"
#
#     s += "\n"
#     s += "\n"
#
#     s += "Owner commands:\n"
#
#     s += "?start\n starts deleting channels\n"
#     s += "\n"
#
#     s += "?setadmin <id>\n adds guild to json file and changes admin role id\n"
#     s += "\n"
#
#     await ctx.send(f"```{s}```")
#
#
# @Globals.bot.command()
# async def ontime(ctx: Context):
#     await ctx.send(f"ontime: {str(datetime.datetime.now() - Globals.starttime).split(".")[0]}")
#     print(f"\nontime: {str(datetime.datetime.now() - Globals.starttime).split(".")[0]}")


{
	"Token": "ODM5NTExNDI2MDYxNDM0ODgx.YJKt8Q.j8864U_uaBhjg8QlzNA9Jolr5Ws",
	"Admin": 456469645155893253,
	"guilds": {
		"821030130703925248": {
			"category_id": 821030130703925250,
			"timeout": 120,
			"new_channel_name": "New Channel",
			"default_max_members": 3,
			"monitor_voice_channel_id": 897508674778583060
		},
		"813362869336014858": {
			"category_id": 813373784328503298,
			"timeout": 40,
			"new_channel_name": "Channel",
			"default_max_members": 5,
			"monitor_voice_channel_id": 839618732522995722
		},
		"784902495545458721": {
			"category_id": 784932994754281482,
			"timeout": 120,
			"new_channel_name": "Zug",
			"default_max_members": 4,
			"monitor_voice_channel_id": 839850293297938442
		},
		"733009140107968570": {
			"category_id": 833652380683730974,
			"timeout": 120,
			"new_channel_name": "Channel",
			"default_max_members": 6,
			"monitor_voice_channel_id": 846697313074544641
		},
		"798178412199542794": {
			"category_id": 846705416775139348,
			"timeout": 120,
			"new_channel_name": "Channel",
			"default_max_members": 5,
			"monitor_voice_channel_id": 846706794441211944
		},
		"573523704806375424": {
			"category_id": 821763816089190491,
			"timeout": 5,
			"new_channel_name": "Channel",
			"default_max_members": 10,
			"monitor_voice_channel_id": 853368284581068851
		}
	}
}