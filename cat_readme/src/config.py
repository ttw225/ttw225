from dataclasses import dataclass
from typing import Dict

VALID_ACTION: Dict[str, Dict[str, str]] = {
    "eat": {"Can": "🥫", "Kibble": "🧆"},
    "play": {"Catnip": "🍀", "Cat_Teaser_Wand": "🎣", "Box": "📦"},
    "sleep": {"Sleep_Well": "🛌", "Angle": "💫", "Sun": "☀️", "Blanket": "👁️"},
    "fun": {"headgear": "🎩"},
}


@dataclass
class Action:
    category: str = ""
    name: str = ""
