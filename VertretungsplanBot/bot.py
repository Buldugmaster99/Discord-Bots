import json
import os
from datetime import datetime
from typing import Dict
from dacite import from_dict

import interactions
from interactions.client.context import CommandContext as Context

from VertretungsplanBot.defs import Tag

ids = [859820328631926795, 821030130703925248]
bot = interactions.Client(token="")

startTime: datetime = datetime.now()
days: Dict[str, Tag] = {}

for date in os.listdir("data"):
    with open(f"data/{date}", "r") as f:
        tag: Tag = from_dict(data_class=Tag, data=json.load(f))
        days[tag.date] = tag


@bot.command(
    name="vertretungsplan",
    description="gibt Vertretungen für eine bestimmte Klasse an einem bestimmten Tag zurück",
    scope=ids,
    options=[
        interactions.Option(
            name="tag",
            description="Tag für den vertretungen ausgegeben werden sollen",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[interactions.Choice(name=option, value=option) for option in [day for day in days.keys()]]
        ),
        interactions.Option(
            name="klasse",
            description="Klasse für die vertretungen ausgegeben werden sollen",
            required=True,
            type=interactions.OptionType.STRING,
        ),
    ]
)
async def send(ctx: Context, klasse: str, tag: str):
    data = days[tag]
    klasse = klasse.strip()

    if klasse not in data.classes:
        await ctx.send(f"Klasse {klasse} am {tag} nicht gefunden")
        print(f'send: Vertretungen für Klasse {klasse} an {tag} nicht gefunden')
    else:
        embed = interactions.Embed(title=f"Vertretungen für {klasse} am {data.date}", colour=0x3e038c)

        embed.description = f"Abfragezeit: {str(data.queryDate)}"

        for v in data.classes[klasse]:
            embed.add_field(name=v.Stunde, value=f"{v.Lehrkraft} -> {v.vertretendurch} | {v.Raum} ({v.Bemerkung})", inline=True)

        await ctx.send(embeds=embed)
        print(f'send: Vertretungen für Klasse {klasse} an {tag} ausgegeben')


bot.start()
