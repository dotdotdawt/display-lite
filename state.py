"""
states.py
"""

# -------------------------------------- --------------------------------------
# Display names as strings.
MAIN = 'main'
CONTROL = 'control'
WORLD = 'world'
PLAYER = 'player'
TEXT = 'text'
EMPTY = 'empty'

# Global list of displays.
DISPLAYS = [
    MAIN,
    CONTROL,
    WORLD,
    PLAYER,
    TEXT,
    EMPTY
    ]


# -------------------------------------- --------------------------------------
class State(object):
    # The State() object for displays. This tells the main display when to show individual
    # displays based on the 'show', 'clear', and 'input' booleans.    
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.show = True
        self.clear = False
        self.input = True
        self.grouped = False
        self.modified = False
        self.setup()

    def setup(self):
        self.setup_colors()
        
        # Set the proper states for each type of display State().
        if self.name == MAIN:
            self.deactivate(invert=True)
            self.modified = True
            self.grouped = False
            self.fill_color = self.colors['black']

        elif self.name == CONTROL:
            self.deactivate(invert=False)
            self.modified = True
            self.moving = False
            self.input = True
            self.grouped = False
            
        elif self.name == WORLD:
            self.deactivate(invert=True)
            self.modified = True
            self.grouped = False
            self.fill_color = self.colors['teal']

        elif self.name == PLAYER:
            self.deactivate(invert=True)
            self.modified = False
            self.grouped = False

        elif self.name == TEXT:
            self.deactivate(invert=True)
            self.modified = False
            self.grouped = True

        elif self.name == EMPTY:
            self.deactivate(invert=False)
            self.modified = True
            self.grouped = False

    def setup_colors(self):
        try:
            self.colors = self.parent.get_colors()
        except AttributeError:
            print("| E | setup_colors() failed. |")

    def deactivate(self, invert=False):
        self.show = invert
        self.input = invert
        self.clear = invert
        
