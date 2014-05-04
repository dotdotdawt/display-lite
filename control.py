"""
control.py 2
"""

# -------------------------------------- --------------------------------------
# System imports
import math
import random
import sys

# 3rd party imports
import pygame
from pygame.locals import *

# Local imports
import display


# -------------------------------------- --------------------------------------
class Control(object):
    """
    ----------------------------------- --------------------------------------
    This is the object that holds the main loop and interprets user events.

    _____Notable things_____
    - self.state is a State() object... If self.state.input=False then all
        inputs will be overriden. This is the same for 'main' State().

    - 
    ----------------------------------- --------------------------------------
    """
    def __init__(self, settings):
        self.debug = settings['debug']
        self.temp_state = settings['state']
        
        if self.debug:
            self.display = display.Display(setup=True)
            #self.display = display.Display(setup=False)
            self.setup()
            
        elif not self.debug:
            self.display = display.Display(setup=True)
            self.setup()

    def setup(self):
        self.set_defaults()

    def set_defaults(self):
        self.state = self.display.states['control']
        self.state.current = self.temp_state
        self.battle = False
        self.menu = False
        self.world = True
        self.on = True
        self.moving = 0
        self.update_settings = False
        self.non_input_states = {}
        self.set_engage_chance()
        self.setup_inputs()
        
    def setup_inputs(self):
        self.left = 0
        self.right = 1
        self.qwer_color_mod = [
            ( 10, -10, -12),
            ( 00, -12,  10),
            (-20,  00,   3),
            ( -3,  20,  03)
            ]
        self.directions = {
            'up': (0, -1), 'down': (0, 1),
            'left': (-1, 0), 'right': (1, 0)
            }
        self.direction_states = {
            'up': False, 'down': False, 'left': False, 'right': False
            }
        self.qwer_states = {
            'q': False, 'w': False, 'e': False, 'r': False
            }
        self.input_states = {
            'world': self.display.displays['world'].state,
            'battle': 'not implemented yet'
            }
        for key in self.display.displays:
            if key not in self.input_states:
                self.non_input_states[key] = ("|_%s_|" % key)
        self.pg_dir_keys = {
            pygame.K_LEFT:'left',
            pygame.K_RIGHT:'right',
            pygame.K_UP: 'up',
            pygame.K_DOWN: 'down'
            }
        self.pg_qwer_keys = {
            pygame.K_q: 'q',
            pygame.K_w: 'w',
            pygame.K_e: 'e',
            pygame.K_r: 'r',
            'q': 0,
            'w': 1,
            'e': 2,
            'r': 3
            }
        self.pg_esc_keys = {
            pygame.K_ESCAPE: 'ESC'
            }
        self.input_keys = [self.pg_dir_keys, self.pg_qwer_keys, self.pg_esc_keys]

    # -------------------------------------- --------------------------------------
    # Main Loop
    # zomg, like really importante
    # -------------------------------------- --------------------------------------
    def main_loop(self):
        
        while self.on:
            """Independent of state, these need to run."""
            self.evaluate_state()
            self.handle_events()

            """In the overworld we need to check to see if a battle needs to happen
            and we need to apply movement updates to the Player()"""
            if self.world:
                if self.state.input and self.moving:
                    self.world_movement()
                    if self.state.moving:
                        self.random_engage()                

            """Check if the battle is over every frame."""
            if self.battle:
                self.check_battle_over()

            """Let Display() do it's thang"""
            self.display.update()
            self.display.fps_clock.tick(self.display.fps)
            pygame.display.update()

        """Goodbye."""
        while not self.on:
            pygame.quit()
            sys.exit()

    # -------------------------------------- --------------------------------------
    # State evaluation!!
    # -------------------------------------- --------------------------------------  
    def evaluate_state(self):
        """All of the state logic for transferring between major states should happen in
        here. That way this function can just be run every loop to reevaluate what state
        the user should be in."""
        if self.world == False and self.battle:
            self.state.current = 'battle'
        elif self.world and self.battle == False:
            self.state.current = 'world'

    def check_left_click(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == self.left:
            event_x = event.pos[0]
            event_y = event.pos[1]

    def check_quit(self, event):
        if event.type == KEYUP:
            if event.key in self.pg_esc_keys:
                self.on = False
            
    def handle_events(self):
        for event in pygame.event.get():
            self.check_left_click(event)
            self.check_quit(event)
            
            if self.debug:
                self.debug_event(event)          
            if self.state.current in self.input_states:
                self.handle_inputs(event)

    def verify_input(self):
        """We determine if input is allowed by adding 1 to allowed each time a State()
        has input=True. If allowed is 1 or more then input is allowed. If either
        Display.state.input or Control.state.input is False then we override all of the
        others."""
        allowed = 0
        for x in range(0, len(self.display.displays)):
            """This can give KeyError because there are inactive displays that are setup but
            dont exist."""
            try:
                """To avoid an error, we need to set component here... No idea why? [BUG]"""
                component = self.display.displays[self.display.display_keys[x]]
                if component.state.input:
                    allowed += 1
                elif not component.state.input:
                    if component.name == 'main' or component.name == 'control':
                        allowed = -30
            except KeyError:
                allowed += 0

        """We have all the information, we tell the master Control() whether to allow inputs."""
        if allowed >= 1:
            self.state.input = True
        else:
            self.state.input = False

        return self.state.input

    def update_direction(self, event, direction, being_pressed):
        if being_pressed:
            self.direction_states[direction] = True
            self.moving += 1
            
        elif not being_pressed:
            if self.direction_states[direction]:
                self.moving -= 1
                self.direction_states[direction] = False

    def update_qwer(self, event, name, num_id):
        self.world_color(name, num_id)

    def handle_inputs(self, event):
        if self.verify_input():
            """This decides whether or not a Player() is trying to move in a certain direction.
            Movement is handled by polling in the World()."""
            if self.state.current == 'world':
                """Keys are being pressed"""
                if event.type == KEYDOWN:
                    being_pressed = True
                    if event.key in self.pg_dir_keys:
                        for key in self.pg_dir_keys:
                            if key == event.key:
                                direction = self.pg_dir_keys[key]
                                self.update_direction(event, direction, being_pressed)

                    """Keys need antidepressants"""
                elif event.type == KEYUP:
                    being_pressed = False
                    if event.key in self.pg_dir_keys:
                        for key in self.pg_dir_keys:
                            if key == event.key:
                                direction = self.pg_dir_keys[key]
                                self.update_direction(event, direction, being_pressed)

                        """Non-directional key depresses"""
                    if event.key in self.pg_qwer_keys:
                        for key in self.pg_qwer_keys:
                            if key == event.key:
                                btn_name = self.pg_qwer_keys[key]
                                btn_num  = self.pg_qwer_keys[self.pg_qwer_keys[key]]
                                self.update_qwer(event, btn_name, btn_num)



                                

            """
            # Battle movement. If allowed, allow the user to move around the menu.
            elif state == 'battle':
                if self.allow_input:
                    if event.type == KEYUP:
                        # Cursor movements through the menu in a battle.
                        if event.key == pygame.K_LEFT:
                            self.display.battle.menu.move_cursor('left')
                        elif event.key == pygame.K_UP:
                            self.display.battle.menu.move_cursor('up')
                        elif event.key == pygame.K_RIGHT:
                            self.display.battle.menu.move_cursor('right')
                        elif event.key == pygame.K_DOWN:
                            self.display.battle.menu.move_cursor('down')

                        # Pressing Q in a battle
                        elif event.key == pygame.K_q:
                            if self.battle_obj.in_menu:
                                self.battle_obj.state_continue('accept')
                            elif self.battle_obj.in_intro:
                                self.battle_obj.state_continue('accept')
                            elif self.battle_obj.in_exit:
                                self.battle_obj.state_continue('accept')
                                self.battle = False
                                self.overworld = True

                        elif event.key == pygame.K_e:
                            self.message(self.state)

                        # Pressing R in a battle
                        elif event.key == pygame.K_r:
                            if self.battle_obj.in_menu:
                                self.battle_obj.state_continue('decline')
                            elif self.battle_obj.in_intro:
                                self.battle_obj.state_continue('decline')
                            elif self.battle_obj.in_exit:
                                 self.battle_obj.state_continue('decline')

            #
            #

            #
            # THIS IS THE ONLY ONE THAT'S RERFERENCING RIGHT.

            #
            #
            #
            
            # User button selection and things that don't require a state.
            if event.type == KEYUP:
                if event.key == pygame.K_q:
                    self.display.displays['qwer']['q'].state = 1
                    self.display.displays['qwer']['q'].active = False
                elif event.key == pygame.K_w:
                    self.display.displays['qwer']['w'].state = 1
                    self.display.displays['qwer']['w'].active = False
                elif event.key == pygame.K_e:
                    self.display.displays['qwer']['e'].state = 1
                    self.display.displays['qwer']['e'].active = False
                elif event.key == pygame.K_r:
                    self.display.displays['qwer']['r'].state = 1
                    self.display.displays['qwer']['r'].active = False

            #
            #
            #
            #
            #

            if event.type == KEYDOWN:
                if event.key == pygame.K_q:
                    self.display.btns['q'].state = 1
                    self.display.btns['q'].active = True
                elif event.key == pygame.K_w:
                    self.display.btns['w'].state = 1
                    self.display.btns['w'].active = True
                elif event.key == pygame.K_e:
                    self.display.btns['e'].state = 1
                    self.display.btns['e'].active = True
                elif event.key == pygame.K_r:
                    self.display.btns['r'].state = 1
                    self.display.btns['r'].active = True

            """
    # -------------------------------------- --------------------------------------
    # World() Player() movements
    # -------------------------------------- --------------------------------------
    def world_movement(self):
        """If the button was pressed it will add 1. total is the sum of directions."""
        total = (self.direction_states['left'] + self.direction_states['right'] +
                 self.direction_states['up'] + self.direction_states['down'])


        """We want to override movement if there are 3 directional inputs
        We allow movement with 2 directions but we slow the movement. This should be done
        using vectors... For now just reducing the speed with the multi True/False flag."""
        if total >= 3:
            override = True
        if total == 2:
            override = False
            multi = True
        if total == 1:
            override = False
            multi = False
        if total == 0:
            override = True
            multi = False

        if override:
            self.no_inputs = True
            pass
        if not override:
            self.no_inputs = False
            for key in self.direction_states:
                self.move_player(key, self.directions[key], multi)

    def move_player(self, key, direction, multi):
        """If the direction_state is pressed, move the player in that direction, accounting
        for multi-directional (diagonal) movement with the multi flag."""
        if self.direction_states[key]:
            self.display.player.move(direction, multi)

    def world_color(self, btn_name, btn_num):
        for x in range(0, 2):
            self.display.displays['world'].change_color(x, self.qwer_color_mod[btn_num][x])

    # -------------------------------------- --------------------------------------
    # World() engagement functionality
    # -------------------------------------- --------------------------------------
    def start_battle(self):
        self.world = False
        self.battle = True
        self.evaluate_state()
        #self.display.battle()
        #self.battle_obj = battle.Battle(self.display.player, random=True)

    def check_battle_over(self):
        if self.battle_obj.completed:
            self.battle = False
            self.world = True
            self.state.current = 'world'
            #self.display.battle.state.show = False
            #self.display.battle.state.clear = True 
            #self.display.world.state.show = True
        
    def random_engage(self):
        """Decide whether or not an engage should occur based on Player movement."""
        self.battle_chance_mod = random.randint(0, self.battle_chance_mod)
        self.battle_chance += self.battle_chance_mod
        roll = random.randint(0, self.battle_chance_max)

        if self.battle_chance >= roll:
            self.set_engage_chance()
            self.start_battle()

    def set_engage_chance(self, chance=None, mod=None, chance_max=None):
        if not chance:
            self.battle_chance = 0
        if not mod:
            self.battle_chance_mod = 4
        if not chance_max:
            self.battle_chance_max = 100
        else:
            self.battle_chance = chance
            self.battle_chance_mod = mod
            self.battle_chance_max = chance_max

    # -------------------------------------- -------------------------------------- #
    # Miscellaneous functions
    # -------------------------------------- -------------------------------------- #
    def debug_event(self, event):
        """If debugging for the mouse (or any other type of event) is needed, we print out
        the information here. Other types of events should be added here if they are in need
        of debugging in an effort to keep the program clean."""
        if self.debug == 'high':
            if   event.type == pygame.MOUSEMOTION: 
                print("| debug=high | mouse at (%d, %d) |" % (event.pos))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == self.left:
                print("| debug=high | STARTED TO LEFT CLICK |")

    def message(self, text):
        self.display.send_msg(text)

# -------------------------------------- --------------------------------------
