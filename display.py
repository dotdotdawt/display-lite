"""
display.py
"""

# -------------------------------------- --------------------------------------
# System imports
import math
import random
import sys
import random

# 3rd party imports
import pygame
from pygame.locals import *

# Component imports
import state as STATE
import world as WORLD
import template as TEMPLATE


# -------------------------------------- --------------------------------------
class Display(object):
    # This is the screen you are looking at when running this program. Display is
    # also responsible for holding every other object that needs to display, managing
    # individual State(s)(), updating all displays to self.surface, and generally
    # being a badass all around.
    #
    # _____Notable things_____
    # - displays{ (objects), [lists] }
    #    the unique display objects() or {group} of objects()
    #    
    # - states{ (objects) }
    #    the State() objects
    #    
    # - display_keys[list]
    #    just key names
    #
    # - Instantiated by Control() with Display(setup=True)
    def __init__(self, setup=False):
        self.key = 'main'
        self.reset_settings()
        self.setup_states()
        self.setup_pygame()
        if setup:
            self.setup_displays()

    def setup_states(self):
        self.display_keys = STATE.DISPLAYS
        self.state = STATE.State(self.key, self)
        self.displays = {}
        self.states = {}
        self.states['main'] = self.state
        self.state.show = True
        self.state.clear = False
        self.state.input = True
        
        #Create a State() object for every display that can possibly be created.
        # Some of these will remain inactive forever or a lot of the time.
        for x in range(1, len(self.display_keys)):
            self.states[self.display_keys[x]] = STATE.State(self.display_keys[x], self)
            
    def setup_pygame(self):
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.init()
        pygame.font.init()
        self.fps_clock = pygame.time.Clock()
        
    def setup_displays(self):
        for x in range(0, self.default_displays_amount):
            self.construct_display(self.display_keys[x])

    def construct_display(self, key):
        # Main doesn't really do anything but just clear the screen before anything
        # else gets displayed.
        if key == 'main':
            new_display = TEMPLATE.Template(key, self.states[key], 'main')

        # Control doesn't do anything yet either. The only reason it's included here
        # is so that it can have a State() object and can override inputs if needed.
        elif key == 'control':
            new_display = TEMPLATE.Template(key, self.states[key], 'control')

        # World just fills the screen with a color so the Player() has somewhere to
        # walk around.
        elif key == 'world':
            new_display = WORLD.World(key, self.states[key])

        # Example of a nothing display... Will be useful later.
        elif key == 'empty':
            new_display = TEMPLATE.Template(key, self.states[key], 'empty')

        # Not implemented yet.
        """
        elif key == 'text':
            text_type = 'normal'
            new_display = TEXT.Text(
                key, self.states[key], text_type, self.text_objects_amount
                )
            self.text_objects_amount += 1
            
        elif key == 'player':
            new_display = PLAYER.Player(key, self.states[key])
        """
        
        # Now we make a reference to the newly made display object.
        self.displays[key] = new_display
        self.displays[key].state = self.states[key]

    # These deal with updating the screens and ensuring state is handled properly.
    def update(self):
        # This is where all of the displaying occurs. This runs once per frame.
        # First, clear the display with try_clear(), then start showing the displays
        # in order.
        for x in range(0, len(self.display_keys)):
            try:
                self.try_clear(self.displays[self.display_keys[x]], self.display_keys[x])
                self.try_show(self.displays[self.display_keys[x]], self.display_keys[x])
            except KeyError:
                pass

    def try_clear(self, display, key):               
        if display.state.clear:
            self.wipe(custom_color=None)

    def try_show(self, display, key):
        # If the display state is grouped and returns updates in the form of
        # a dict, we go through a loop so we can display each object by
        # itself. This is because the main Display() object only likes to
        # display objects one at a time.
        if display.state.show and not display.state.modified:
            if display.state.grouped:
                objects = display.get_updated_objects()

                for x in range(0, len(objects)):
                    surf, rect = objects[x].get_update()
                    self.show_this(surf, rect)

        # If the display is not in the form of a group, we just display the
        #'display' (tired of using this word) by itself
            elif display.state.grouped == False:
                surf, rect = display.get_update()
                self.show_this(surf, rect)

        # If the display will show and display method IS modified in some way.
        # To clarify: modified means that the way the object displays is not simply
        # using an object (or group of objects) with a surface and a rect and just
        # throwing them up on the screen. The way it displays is fundamentally
        # different.
        #
        # ____Examples of modified display methods____
        #   -- World() just fills up the screen with a color. It's basically a back
        # ground for where the Player() wants to walk. 
        #
        #   -- 'main' is simply a placeholder and does not display anything at all.
        # It does serve a purpose in that it is shown before anything else and is
        # responsible for 'blacking out' the screen before anything else is put up.
        elif display.state.show and display.state.modified:
            self.show_modified(self.displays[key], key)

        # Don't do shit. Maybe something will need to go here later.
        elif display.state.show == False:
            pass

        # You done got errors again, bro.
        else:
            print("| E | >> try_show() error. |")
        
    def wipe(self, custom_color=None):
        # All this does is wipe the screen with black if you have not given this
        # a custom color to fill the screen with. This is how World() displays.
        if custom_color:
            self.surface.fill(custom_color)
        else:
            try:
                self.surface.fill(self.fill_color)
            except AttributeError:
                self.surface.fill( (0,0,0) ) # Fix this fucking [BUG]
        
    def show_modified(self, display, key):
        # Custom display methods for displays that are not cut and dry. To clarify
        # this: modified displays are displays that do not simply return a surf/rect
        # pair (or dictionary of pairs) to be displayed to the screen.
        if key == 'world':
            self.wipe(self.displays['world'].state.fill_color)

        elif key == 'main':
            self.wipe()

        elif key == 'control':
            pass

        elif key == 'text':
            for x in range(0, len(self.displays['text'])):
                surface, rect = self.get_update()
                self.display_this(surface, rect)

        # This is an example of how a display can be treated as a group of individual
        # sprites with surf/rect pairs.
        elif key == 'qwer':
            for key in self.displays['qwer']:
                self.displays['qwer'][key].handle_state()

            if self.states['qwer'].show:
                for key in self.displays['qwer']:
                    surface, rect = self.displays['qwer'].get_update(key)
                    self.display_this(surface, rect)

        elif key == 'empty':
            self.displays['world'].state.fill_color[2] += 20 # To show that it's working.

    def show_this(self, surf, rect):
        # Takes a surface and a rectangle and puts on the damn screen. It really
        # just forces it on there and doesn't give a fuck. Only send display objects
        # here if you know you are showing it at the correct time.
        self.surface.blit(surf, rect)
    
    # More general and widely used functions.
    def send_msg(self, text):
        self.displays['text'].send_msg(text)

    def reset_settings(self):
        self.colors = self.get_colors()
        self.refresh_color = self.colors['teal']
        self.fps = 30
        self.window_size = (300, 300)
        
        self.text_objects_amount = 0
        self.default_displays_amount = 3

    def get_colors(self):
        colors = {
            'black':      (  0,   0,   0, False),
            'white':      (240, 240, 240, False),
            'teal':       (  0, 150, 185, False),
            'lite_green': (  0, 100, 220, False)
            }

        return colors

# -------------------------------------- --------------------------------------
