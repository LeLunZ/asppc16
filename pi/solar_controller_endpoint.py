from serial import Serial
from threading import Thread

class SolarControllerEndpoint(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.current_volt = 0
        self._listeners = []
        self.terminated = False
        try:
            self._serial = Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=5) # upper right USB port
        except:
            self._serial = None
            self.terminate()
            self.current_volt = float('nan')
    
    def terminate(self):
        self.terminated = True
    
    def add_change_listener(self, listener):
        self._listeners.append(listener)
    
    def get_current_volt(self):
        return self.current_volt
    
    def run(self):
        while not self.terminated:
            val = self._serial.read(1)
            if len(val) > 0:
                self.current_volt = 2.5 * val[-1] / 255
                for listener in self._listeners:
                    listener(self.current_volt)

solar_controller_endpoint = SolarControllerEndpoint()
solar_controller_endpoint.start()