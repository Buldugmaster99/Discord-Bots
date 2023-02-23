import json
import locale
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List

import requests
from dateutil import parser
from dateutil.parser import parserinfo
from lxml import etree

from defs import Vertretung, Tag

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


def getContentRecursive(element):
    """
    Sometimes HTMLelement contains other <center> tag with content,
    so this method filters this out and returns the complete text
    """
    content = ""
    if element.text is not None:
        content += element.text
    els = element.getchildren()
    for i in els:
        if i.text is not None:
            content += i.text
        els += i.getchildren()
    return content.strip()


def loadSite(url, auth1, auth2):
    try:
        response = requests.get(url, auth=(auth1, auth2))
    except requests.exceptions.RequestException as e:
        print(e, file=sys.stderr)
        return 

    html = etree.HTML(response.content, etree.HTMLParser())

    main = html.xpath("//html/body/a")[0]
    date = parser.parse(str(main.getnext().getnext().text).removeprefix("Vertretungsplan für ").split(", ")[1],
                        parserinfo=parserinfo(dayfirst=True, yearfirst=False))
    queryDate = datetime.now().strftime("(%a) %d.%m.%y %H:%M:%S")

    classes: Dict[str, List[Vertretung]] = {}

    for el in main.getnext().getnext().getnext().getnext().getchildren():  # individual classes
        vertretungen: List[Vertretung] = []
        for el2 in el.getchildren():  # individual replacements
            vertretung: List[str] = []

            for index, el3 in enumerate(el2.getchildren()):  # individual replacements infos
                if el3.tag == "th":
                    # print(f"found class: {getContentRecursive(el3)}")
                    classes[el3.text.strip()] = vertretungen
                else:
                    # print(f"found info: {getContentRecursive(el3)}")
                    vertretung.append(getContentRecursive(el3))

            if len(vertretung) == 5:
                # print(f"vertretung: {vertretung}")
                vertretungen.append(
                    Vertretung(Lehrkraft=vertretung[0], Stunde=vertretung[1], vertretendurch=vertretung[2], Raum=vertretung[3],
                               Bemerkung=vertretung[4]))

    tag = Tag(date=date.strftime("%a, %d.%m.%y"), queryDate=queryDate, classes=classes)

    with open(f"data/{int(date.timestamp())}.json", "w", encoding="utf-8") as f:
        json.dump(asdict(tag), f)
