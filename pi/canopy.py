import explorerhat as eh
from time import sleep

CANOPY_SPEED = 100
CANOPY_SWITCHES_BOUNCE_TIME = 0.1 # s


class Canopy:
    def __init__(self):
        self._state = -1 # -1 - unknown, 0 - open, 1 - closed, 2 - opening, 3 - closing
        if eh.input.one.read() == 1:
            self._state = 1
        elif eh.input.two.read() == 0:
            self._state = 0
        def on_closed(_):
            if self._state < 2:
                return
            sleep(CANOPY_SWITCHES_BOUNCE_TIME)
            if eh.input.one.read() != 1:
                return
            eh.motor.one.stop()
            self._state = 1
        def on_opened(_):
            if self._state < 2:
                return
            sleep(CANOPY_SWITCHES_BOUNCE_TIME)
            if eh.input.two.read() != 0:
                return
            eh.motor.one.stop()
            self._state = 0
        eh.input.one.on_changed(on_closed) # mostly open -> on_high to preserve energy
        eh.input.two.on_changed(on_opened)

    def close(self):
        if self._state == 1:
            return
        self._state = 3
        print("closing")
        eh.motor.one.speed(CANOPY_SPEED)

    def open(self):
        if self._state == 0:
            return
        self._state = 2
        print("opening")
        eh.motor.one.speed(-CANOPY_SPEED)
    
    def is_opened(self):
        return self._state == 0
    
    def is_closed(self):
        return self._state == 1
    
    def is_moving(self):
        return self._state == 2 or self._state == 3
    
    def is_opening(self):
        return self._state == 2
    
    def is_closing(self):
        return self._state == 3
    
    def get_state_description(self):
        if self._state == -1:
            return "unknown"
        elif self._state == 0:
            return "open"
        elif self._state == 1:
            return "closed"
        elif self._state == 2:
            return "opening"
        elif self._state == 3:
            return "closing"
        else:
            return "undefined"

canopy = Canopy()