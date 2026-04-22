from dataclasses import dataclass


@dataclass
class MacroItem:
    item_id: int
    action_type: str  # "key" or "mouse"
    value: str
    interval: float
    start_delay: float = 0.0
