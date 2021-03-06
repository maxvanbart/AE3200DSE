from pathlib import Path
from misc.openData import openData
from misc.ISA import getPressure, getDensity, getTemperature, getSpeedOfSound


class State:
    def __init__(self, name):
        self.name = name

        self.source = openData(Path('data', 'states', f'{name}.yaml'))
        # self.viscosity =
        self.velocity = self.source['velocity']
        self.range = self.source['range']

    @property
    def dynamic_pressure(self):
        return 0.5 * self.density * self.velocity ** 2

    # @property
    # def velocity(self):
        # return self.source["velocity"]

    @property
    def altitude(self):
        return self.source["altitude"]

    # @property
    # def range(self):
        # return self.source["range"]

    @property
    def duration(self):
        return self.source["range"] / self.source["velocity"]

    @property
    def pressure(self):
        return getPressure(self.altitude)

    @property
    def density(self):
        return getDensity(self.altitude)

    @property
    def temperature(self):
        return getTemperature(self.altitude)

    @property
    def speed_of_sound(self):
        return getSpeedOfSound(self.altitude)

    @property
    def reynolds_number(self):
        return self.density * self.velocity * length / self.viscosity
