import logging

import interactions
from interactions import Option, OptionType, CommandContext, Guild, Channel, Member

from NewVoiceChannelBot import globals as glob


@glob.bot.command(
    name="rename",
    description="changes the name of current VoiceChannel",
    dm_permission=False,
    options=[
        Option(
            name="new_name",
            description="New name of the VoiceChannel",
            type=OptionType.STRING,
            required=True
        ),
    ]
)
async def _rename(ctx: CommandContext, new_name: str):
    try:
        guild = await ctx.get_guild()
        channel = await _get_member_channel(guild, ctx.member)

        if channel is None:
            await ctx.send("You are not in a VoiceChannel")
            return

        await channel.set_name(new_name)
        await ctx.send(f"Changed name of VoiceChannel to {new_name}")

    except glob.CommandException as e:
        await ctx.send(f"Exception occurred: {e}")  # show custom exceptions
        logging.error(f"Exception occurred {e}")
        return
    except Exception as e:
        await ctx.send(f"Exception occurred")  # hide real exceptions
        logging.error(f"Exception occurred {e}")
        return


async def _get_member_channel(_guild: Guild, member: Member) -> Channel:
    for channel in _guild.channels:
        if channel.type == interactions.ChannelType.GUILD_VOICE and member in channel.members:
            return channel
    glob.err("No channel found for member", _guild)
    raise glob.CommandException("No channel found for member")
