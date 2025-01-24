from dataclasses import dataclass
from typing import List, Dict

@dataclass
class GameMessage:
    phase: str
    player: str
    content: str
    visibility: str = "public"  # public, private, or narrator
