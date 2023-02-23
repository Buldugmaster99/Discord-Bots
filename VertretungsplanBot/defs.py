from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Vertretung:
    Lehrkraft: str
    Stunde: str
    vertretendurch: str
    Raum: str
    Bemerkung: str


@dataclass
class Tag:
    date: str
    queryDate: str
    classes: Dict[str, List[Vertretung]]
