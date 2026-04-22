from pynput.keyboard import Key
from pynput.mouse import Button


SPECIAL_KEYS = {
    "space": Key.space,
    "enter": Key.enter,
    "tab": Key.tab,
    "esc": Key.esc,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
    "backspace": Key.backspace,
    "delete": Key.delete,
}

MOUSE_BUTTONS = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}
