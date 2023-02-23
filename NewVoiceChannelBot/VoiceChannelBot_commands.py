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
#
#
# @Globals.bot.command()
# async def ontime(ctx: Context):
#     await ctx.send(f"ontime: {str(datetime.datetime.now() - Globals.starttime).split(".")[0]}")
#     print(f"\nontime: {str(datetime.datetime.now() - Globals.starttime).split(".")[0]}")
