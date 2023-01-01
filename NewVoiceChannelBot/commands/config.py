from typing import List

import interactions
from interactions import Channel, Guild, Member, EmbedField
from interactions.client.context import CommandContext
from interactions.client.enums import OptionType
from interactions.client.models import Option

from NewVoiceChannelBot import globals as glob


@glob.bot.command(
    name="config",
    description="configures this bot, used by server admin",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    dm_permission=False,
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
            description="VoiceChannel to monitor and create new VoiceChannel if someone joins",
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
            description="Default max Members allowed in Custom VoiceChannel (change for current VoiceChannel with /limit)",
            type=OptionType.NUMBER,
            required=False,
            min_value=1,
            max_value=99
        ),
    ]
)
async def _config(ctx: CommandContext, category: Channel = None, timeout: int = None, monitor_voice_channel: Channel = None,
                  new_channel_name: str = None, default_max_members: int = None):
    # try:
    guild = await ctx.get_guild()
    my_guild = await _check_guild(int(ctx.guild_id))
    member = await _get_pub_member(guild)

    fields: list[EmbedField] = []
    fields.append(await _handle_category(category, guild, my_guild)),
    fields.append(await _handle_timeout(timeout, guild, my_guild)),
    fields.append(await _handle_monitor_VoiceChannel(monitor_voice_channel, guild, my_guild)),
    fields.append(await _handle_new_channel_name(new_channel_name, guild, my_guild)),
    fields.append(await _handle_default_max_members(default_max_members, guild, my_guild))

    embed = interactions.Embed(
        title="Config",
        color=255,
        footer=interactions.EmbedFooter(text=guild.name, icon_url=guild.icon_url),
        author=interactions.EmbedAuthor(name=member.name, icon_url=glob.bot.me.icon_url),
        fields=fields
    )

    await ctx.send(embeds=embed)


# except glob.CommandException as e:
#     await ctx.send(f"Exception occurred: {e}")  # show custom exceptions
#     logging.error(f"Exception occurred {e}")
#     return
# except Exception as e:
#     await ctx.send(f"Exception occurred")  # hide real exceptions
#     logging.error(f"Exception occurred {e}")
#     return


async def _get_pub_member(_guild: Guild) -> Member:
    return next(member for member in _guild.members if member.id == glob.bot.me.id)


async def _check_guild(guild_id: int) -> glob.CustomGuild:
    guild = glob.guilds[guild_id]

    if guild is None:
        glob.err(f"No category registered for this guild; id:{guild_id}")
        raise glob.CommandException("Guild not registered (BotAdmin needs to register guild)")

    return guild


async def _handle_category(_category: Channel | None, _guild: Guild, _my_guild: glob.CustomGuild) -> EmbedField:
    if _category is None:
        if _my_guild.category_id is None:
            glob.err("No category registered for this guild", _guild)
            raise glob.CommandException("No category registered for this guild")

        category = next((ch for ch in await _guild.get_all_channels() if ch.id == _my_guild.category_id), None)
        if category is None:
            glob.err(f"Category registered for this guild wasn't found; categoryId:[{_my_guild.category_id}]", _guild)
            raise glob.CommandException("Category registered for this guild wasn't found (probably deleted)")

        return EmbedField(
            name="Category",
            value=category.name,
            inline=False,
        )
    else:
        if _category.type is not interactions.ChannelType.GUILD_CATEGORY:
            glob.err(f"category must be a category; channel:{_category.name}[{_category.id}]", _guild)
            raise glob.CommandException(f"category must be a Category: {_category.name}")

        old = next((ch for ch in await _guild.get_all_channels() if ch.id == _my_guild.category_id), None)

        _my_guild.category_id = _category.id
        # TODO save

        glob.log(f"changed category to {_category.name}; channel:{_category.name}[{_category.id}]", _guild)
        return EmbedField(
            name="Category",
            value=f'{_category.name} (changed from {old.name if old is not None else "None"})',
            inline=False,
        )


async def _handle_timeout(_timeout: int | None, _guild: Guild, _my_guild: glob.CustomGuild) -> EmbedField:
    if _timeout is None:
        if _my_guild.timeout is None:
            glob.err("No timeout defined for this guild", _guild)
            raise glob.CommandException("No timeout defined for this guild")

        return EmbedField(
            name="Timeout",
            value=_my_guild.timeout,
            inline=False,
        )
    else:
        old = _my_guild.timeout

        _my_guild.timeout = _timeout
        # TODO save

        glob.log(f"changed timeout to {_timeout}", _guild)
        return EmbedField(
            name="Timeout",
            value=f'{_timeout} (changed from {old if old is not None else "None"})',
            inline=False,
        )


async def _handle_monitor_VoiceChannel(_monitor_VoiceChannel: Channel | None, _guild: Guild, _my_guild: glob.CustomGuild) -> EmbedField:
    if _monitor_VoiceChannel is None:
        if _my_guild.monitor_voice_channel_id is None:
            glob.err("No monitor_voice_channel registered for this guild", _guild)
            raise glob.CommandException("No monitor_voice_channel registered for this guild")

        monitor_VoiceChannel = next((ch for ch in await _guild.get_all_channels() if ch.id == _my_guild.monitor_voice_channel_id), None)
        if monitor_VoiceChannel is None:
            glob.err(
                f"monitor_voice_channel registered for this guild wasn't found; monitor_voice_channelId:[{_my_guild.monitor_voice_channel_id}]",
                _guild)
            raise glob.CommandException("monitor_voice_channel registered for this guild wasn't found (probably deleted)")

        return EmbedField(
            name="MonitorVoiceChannel",
            value=monitor_VoiceChannel.name,
            inline=False,
        )
    else:
        if _monitor_VoiceChannel.type is not interactions.ChannelType.GUILD_VOICE:
            glob.err(f"monitor_voice_channel must be a VoiceChannel; channel:{_monitor_VoiceChannel.name}[{_monitor_VoiceChannel.id}]",
                     _guild)
            raise glob.CommandException(f"monitor_voice_channel must be a VoiceChannel: {_monitor_VoiceChannel.name}")

        old = next((ch for ch in await _guild.get_all_channels() if ch.id == _my_guild.monitor_voice_channel_id), None)

        _my_guild.monitor_voice_channel_id = _monitor_VoiceChannel.id
        # TODO save

        glob.log(
            f"changed monitor_voice_channel to {_monitor_VoiceChannel.name}; channel:{_monitor_VoiceChannel.name}[{_monitor_VoiceChannel.id}]",
            _guild)
        return EmbedField(
            name="MonitorVoiceChannel",
            value=f'{_monitor_VoiceChannel.name} (changed from {old.name if old is not None else "None"})',
            inline=False,
        )


async def _handle_new_channel_name(_new_channel_name: str | None, _guild: Guild, _my_guild: glob.CustomGuild) -> EmbedField:
    if _new_channel_name is None:
        if _my_guild.new_channel_name is None:
            glob.err("No new_channel_name defined for this guild", _guild)
            raise glob.CommandException("No new_channel_name defined for this guild")

        return EmbedField(
            name="New Channel Name",
            value=_my_guild.new_channel_name,
            inline=False,
        )
    else:
        old = _my_guild.new_channel_name

        _my_guild.new_channel_name = _new_channel_name
        # TODO save

        glob.log(f"changed new_channel_name to {_new_channel_name}", _guild)
        return EmbedField(
            name="New Channel Name",
            value=f'{_new_channel_name} (changed from {old if old is not None else "None"})',
            inline=False,
        )


async def _handle_default_max_members(_default_max_members: int | None, _guild: Guild, _my_guild: glob.CustomGuild) -> EmbedField:
    if _default_max_members is None:
        if _my_guild.default_max_members is None:
            glob.err("No default_max_members defined for this guild", _guild)
            raise glob.CommandException("No default_max_members defined for this guild")

        return EmbedField(
            name="Default Max Members",
            value=_my_guild.default_max_members,
            inline=False,
        )
    else:
        old = _my_guild.default_max_members

        _my_guild.default_max_members = _default_max_members
        # TODO save

        glob.log(f"changed default_max_members to {_default_max_members}", _guild)
        return EmbedField(
            name="Default Max Members",
            value=f'{_default_max_members} (changed from {old if old is not None else "None"})',
            inline=False,
        )
