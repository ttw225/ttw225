from dataclasses import dataclass

VALID_ACTION: dict[str, dict[str, str]] = {
    "eat": {"Can": "🥫", "Kibble": "🧆"},
    "play": {"Catnip": "🍀", "Cat_Teaser_Wand": "🎣", "Box": "📦"},
    "sleep": {"Sleep_Well": "🛌", "Angle": "💫", "Sun": "☀️", "Blanket": "👁️"},
    "fun": {"headgear": "🎩"},
}


@dataclass
class Action:
    category: str
    name: str
