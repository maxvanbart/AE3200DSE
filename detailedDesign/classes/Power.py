# To check
from detailedDesign.classes.Component import Component
from detailedDesign.classes.FuelCells import FuelCells
from detailedDesign.classes.Batteries import Batteries


class Power(Component):
    def __init__(self, FuselageGroup, config):
        my_config = super().__init__(config)
        self.FuselageGroup = FuselageGroup
        self.FuelCells = FuelCells(self, my_config)
        self.Batteries = Batteries(self, my_config)
        self.components += [self.FuelCells, self.Batteries]
