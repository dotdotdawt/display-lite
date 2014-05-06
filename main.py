"""
main.py

Last updated:
May
5
2014 
"""

# -------------------------------------- --------------------------------------
# Local imports
import control


# -------------------------------------- --------------------------------------
def main():

    intialization_settings = {
        'state': 'world',
        'debug': None
        }
    
    CONTROL = control.Control(intialization_settings)
    CONTROL.main_loop()

if __name__ == '__main__':
    main()

# -------------------------------------- --------------------------------------
