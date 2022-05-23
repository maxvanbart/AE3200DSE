# To Check
from detailedDesign.classes.Component import Component
from detailedDesign.classes.Wing import Wing
from detailedDesign.classes.Engines import Engines


class WingGroup(Component):
    def __init__(self, Aircraft, config):
        my_config = super().__init__(config)

        self.Aircraft = Aircraft

        self.Wing = Wing(self, my_config)
        self.Engines = Engines(self, my_config)
        self.components += [self.Wing, self.Engines]

    def size_self(self):
        pass
