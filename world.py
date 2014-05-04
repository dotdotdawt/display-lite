

class World(object):


    def __init__(self, key, state):
        self.key = key
        self.state = state

    def update(self):
        pass

    def deactivate(self, invert=False):
        self.show = invert
        self.clear = invert
        self.input = invert

    def change_color(self, rgb, change):
        old = self.state.fill_color
        current = old[rgb]
        if current + change > 255:
            output = 255
        elif current + change < 0:
            output = 0
        else:
            output = (current + change)
            
        if rgb == 0:
            clist = [output, old[rgb+1], old[rgb+2]]
        elif rgb == 1:
            clist = [old[rgb-1], output, old[rgb+1]]
        else:
            clist = [old[rgb-2], old[rgb-1], output]

        self.state.fill_color = clist
