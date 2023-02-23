import logging

from interactions import PresenceActivityType, ClientPresence, StatusType, PresenceActivity, CommandContext
from interactions.ext.voice import VoiceState

from NewVoiceChannelBot import globals as glob
from commands import config, rename

_ = config, rename  # prevent unused import warnings


@glob.bot.event
async def on_start():
    await glob.bot.change_presence(ClientPresence(staus=StatusType.ONLINE, activities=[
        PresenceActivity(name="/help", type=PresenceActivityType.COMPETING, created_at=120)
    ]))


@glob.bot.command(
    name="test",
    description="test",
    dm_permission=False
)
async def _test(ctx: CommandContext):
    await ctx.send("test")


@glob.bot.event
async def on_voice_state_update(vs: VoiceState):
    print(vs.self_mute)


# @commands.Cog.listener()
# async def on_voice_state_update(member: Member, _, after: VoiceChannel):
#     if after.channel is None or not Globals.started:
#         return
#     if after.channel == member.guild.get_channel(Globals.guilds[str(member.guild.id)]["monitorchannel"]):
#         if Globals.guilds[str(member.guild.id)]["countup"]:
#             repeat = True
#             count = 1
#             while repeat:
#                 for channel in Globals.channels:
#                     if channel.guild.id == member.guild.id and str(count) == str(channel.count).strip():
#                         count += 1
#                 repeat = False
#         else:
#             count = ""
#
#         ch = await member.guild.get_channel(Globals.guilds[str(member.guild.id)]["category"]).create_voice_channel(
#             name=Globals.guilds[str(member.guild.id)]["name"] + " " + str(count),
#             user_limit=Globals.guilds[str(member.guild.id)]["defaultmaxmembers"])
#         await member.move_to(ch)
#
#         Globals.channels.append(Globals.Channel(ch, int(time() + Globals.guilds[str(member.guild.id)]["timeout"]), member.guild, count))
#         print(
#             f'\n{member.guild.name}:  new channel created: {ch} in {member.guild.get_channel(Globals.guilds[str(member.guild.id)]["category"])}')
#

# Globals.bot.add_listener(on_voice_state_update)

if __name__ == "__main__":
    logging.disable(level=logging.DEBUG)
    glob.loadjsonvalues(glob.datafile)

    # Globals.starttime = datetime.datetime.now()

    glob.bot.start()
