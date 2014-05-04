"""
main.py

Last updated:
May
2
2014 
"""

# -------------------------------------- --------------------------------------
# Local imports
import control


# -------------------------------------- --------------------------------------
def main():
    
    starting_state = 'world'
    debug_level = None
    #debug_level = 'high'

    intialization_settings = {
        'state': starting_state,
        'debug': debug_level
        }
    
    CONTROL = control.Control(intialization_settings)
    CONTROL.main_loop()

if __name__ == '__main__':
    main()

# -------------------------------------- --------------------------------------
