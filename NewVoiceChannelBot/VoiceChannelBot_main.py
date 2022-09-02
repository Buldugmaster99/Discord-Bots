import logging

import interactions

import VoiceChannelBot_commands
import VoiceChannelBot_globals as Globals

# must be imported else commands will not be applied

_ = VoiceChannelBot_commands


@Globals.bot.event
async def on_ready():
    print('Ready')
    await Globals.bot.change_presence(interactions.ClientPresence(staus=interactions.StatusType.ONLINE, activities=[
        interactions.PresenceActivity(name="/help", type=interactions.PresenceActivityType.WATCHING, created_at=0, emoji=":)")
    ]))


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
    logging.basicConfig(level=logging.INFO)
    Globals.loadjsonvalues(Globals.datafile)

    # Globals.starttime = datetime.datetime.now()

    Globals.bot.start()
