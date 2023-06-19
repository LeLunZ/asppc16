import explorerhat as eh
from time import time
from array import array

MIN_WIND = 0.05 # in m/s
MAX_WIND = 63 # in m/s
ANEMOMETER_RADIUS = 0.07 # in m
ANEMOMETER_CIRCUMFERENCE = 2*ANEMOMETER_RADIUS*3.14159
MIN_WIND_TIMEOUT = ANEMOMETER_CIRCUMFERENCE/(4*MIN_WIND) # anemometer gets value change every 1/4 rotation
ANEMOMETER_AVERAGE_WINDOW = 10 # in samples

class Sensors:
    def __init__(self):
        self._last_anemometer_time = time()
        self._anemometer_durations = array('d', [0]*ANEMOMETER_AVERAGE_WINDOW)
        self._anemometer_durations_index = 0
        self._anemometer_durations_sum = 0
        def on_anemometer_change(input):
            t = time()
            duration = t - self._last_anemometer_time
            self._anemometer_durations_sum -= self._anemometer_durations[self._anemometer_durations_index]
            self._anemometer_durations[self._anemometer_durations_index] = duration
            self._anemometer_durations_sum += duration
            self._anemometer_durations_index = (self._anemometer_durations_index + 1) % ANEMOMETER_AVERAGE_WINDOW
            self._last_anemometer_time = t
        eh.input.three.on_changed(on_anemometer_change)
    
    """"
    in m/s
    """
    def get_wind(self):
        if time() - self._last_anemometer_time > MIN_WIND_TIMEOUT:
            return 0.0
        if self._anemometer_durations_sum == 0:
            return MAX_WIND
        return ANEMOMETER_CIRCUMFERENCE/(4*self._anemometer_durations_sum/ANEMOMETER_AVERAGE_WINDOW)
    
    """
    0 - no light
    1 - bright light
    """
    def get_light(self):
        return eh.analog.two.read()/5
    
    """
    0 - no precipitation
    1 - high precipitation
    """
    def get_precipitation(self):
        return 1-(eh.analog.one.read()/5)

sensors = Sensors()