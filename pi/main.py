from canopy import canopy
from sensors import sensors
from solar_controller_endpoint import solar_controller_endpoint as solar
import explorerhat as eh
from time import sleep
from threading import Thread

VERBOSE = True
POLLING_FREQUNCY = 0.5 # seconds

class MainController(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.terminated = False
        # up to lower threshold: definitely safe (open)
        # from lower to upper: transition area (keep current canopy state)
        # from upper: definitely unsafe (close)
        self.wind_lower_threshold = 0.2
        self.wind_upper_threshold = 0.6
        self.precipitation_lower_threshold = 0.2
        self.precipitation_upper_threshold = 0.4
        self.light_upper_threshold = 0.8 # inverse (low light unsafe)
        self.light_lower_threshold = 0.7
        self.manual = False
        self.manualOpen = False
    
    def data_to_dict(self):
        return {
            "manual": self.manual,
            "output_solar": solar.get_current_volt(),
            "canopy_state": canopy.get_state_description(),
            "environment_eval": self.get_environment_eval_str(),
            "wind": sensors.get_wind(),
            "precipitation": sensors.get_precipitation(),
            "light": sensors.get_light(),
            "wind_lower_threshold": self.wind_lower_threshold,
            "wind_upper_threshold": self.wind_upper_threshold,
            "precipitation_lower_threshold": self.precipitation_lower_threshold,
            "precipitation_upper_threshold": self.precipitation_upper_threshold,
            "light_upper_threshold": self.light_upper_threshold,
            "light_lower_threshold": self.light_lower_threshold
        }
    
    def get_environment_eval(self):
        wind = sensors.get_wind()
        light = sensors.get_light()
        precipitation = sensors.get_precipitation()
        safe = 0 # 0 - safe, 1 - moderate, 2 - unsafe
        if wind > self.wind_upper_threshold:
            safe = 2
        elif wind > self.wind_lower_threshold:
            safe = max(1, safe)
        if light < self.light_lower_threshold:
            safe = 2
        elif light < self.light_upper_threshold:
            safe = max(1, safe)
        if precipitation > self.precipitation_upper_threshold:
            safe = 2
        elif precipitation > self.precipitation_lower_threshold:
            safe = max(1, safe)
        if VERBOSE:
            print(
                "safe: ", safe, 
                "light: ", light, 
                "rain: ", precipitation, 
                "wind: ", wind, 
                "solar: ", solar.get_current_volt(), 
                "switch 1: ", eh.input.one.read(), 
                "switch 2: ", eh.input.two.read(), 
                "canopy: ", canopy.get_state_description()
            )
        return safe
    
    def get_environment_eval_str(self):
        safe = self.get_environment_eval()
        if safe == 0:
            return "safe"
        elif safe == 1:
            return "moderate"
        else:
            return "unsafe"
    
    def terminate(self):
        self.terminated = True
    
    def update(self):
        if not self.manual:
            safe = self.get_environment_eval()
            if safe == 0:
                canopy.open()
            elif safe == 2:
                canopy.close()
        else:
            if self.manualOpen:
                canopy.open()
            else:
                canopy.close()
    
    def run(self):
        while not self.terminated:
            self.update()
            sleep(POLLING_FREQUNCY)

main_controller = MainController()
main_controller.start()