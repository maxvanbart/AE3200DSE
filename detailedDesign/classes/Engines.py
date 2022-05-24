# To Check
from detailedDesign.classes.Component import Component


class Engines(Component):
    def __init__(self, WingGroup, design_config):
        super().__init__(design_config)

        self.WingGroup = WingGroup

        self.thrust_specific_fuel_consumption = 1

        # Create all the parameters that this component must have here:
        # Using self.property_name = value

        self._freeze()
