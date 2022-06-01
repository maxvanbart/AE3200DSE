import numpy as np

from detailedDesign.classes.Component import Component
from detailedDesign.classes.Cabin import Cabin
from detailedDesign.classes.FuelContainer import FuelContainer
from detailedDesign.classes.CargoBay import CargoBay
from misc.ISA import getPressure
from misc.unitConversions import *
# from detailedDesign.classes.RemovableFuelContainer import FuelContainer

class Fuselage(Component):
    def __init__(self, FuselageGroup, design_config):
        super().__init__(design_config)
        self.FuselageGroup = FuselageGroup

        self.Cabin = Cabin(self, self.design_config)
        self.Cabin.get_sized()
        self.CargoBay = CargoBay(self, self.design_config)
        self.FuelContainer = FuelContainer(self, self.design_config)
        self.components = [self.Cabin, self.CargoBay, self.FuelContainer]
        # Create all the parameters that this component must have here:
        # Using self.property_name = value

        # Dimensions
        self.diameter = None

        self._freeze()

    @property
    def length(self):
        # TODO add tail cone, nose cone etc
        length = self.Cabin.length + self.FuelContainer.length + self.FuelContainer.radius_tank * 2
        self.logger.debug(f"Cabin length: {self.Cabin.length}")
        self.logger.debug(f"Fuel Compartment Length: {self.FuelContainer.length + self.FuelContainer.radius_tank * 2}")
        return length + self.cockpit_length + self.tail_length

    @property
    def inner_diameter(self):
        return self.Cabin.diameter

    @property
    def outer_diameter(self):
        if self.diameter is not None:
            return self.diameter
        else:
            self.diameter = self.inner_diameter * 1.045 + 0.084
            return self.outer_diameter

    def size_self(self):
        self.diameter = 1.045 * self.Cabin.diameter + 0.084     # [m]

        # if self.CargoBay.width is not None:
        #     S_cabin = self.Cabin.width * self.Cabin.height
        #     S_cargo = self.CargoBay.width * self.CargoBay.height

        #     Print dead space inside the fuselage
        #     print(np.pi * self.diameter ** 2 / 4 - S_cargo - S_cabin)

        # MAKE MASS OF THING
        state = self.FuselageGroup.Aircraft.states["cruise"]

        l_FS = m_to_ft(self.length)  # [ft]

        S_FUS_m = (np.pi * self.diameter ** 2) / 4 * 2 + \
            np.pi * self.diameter * self.length  # [m2]
        S_FUS = m2_to_ft2(S_FUS_m)  # [ft2]

        n_z = self.FuselageGroup.Aircraft.ultimate_load_factor

        W_O = kg_to_lbs(self.FuselageGroup.Aircraft.mtom)   # [lbs]

        # TODO: check MDN
        MAGICAL_DISNEY_NUMBER = 0.55
        l_HT = l_FS * MAGICAL_DISNEY_NUMBER     # [ft]

        d_FS = m_to_ft(self.diameter)      # [ft]

        q = pa_to_psf(0.5 * state.density * state.velocity ** 2)  # [psf]

        V_p = m3_to_ft3(np.pi * self.Cabin.diameter ** 2 /
                        4 * self.Cabin.length)   # [ft3]

        Delta_P = pa_to_psi(getPressure(
            self.Cabin.cabin_pressure_altitude) - state.pressure)   # [psi]
        if Delta_P < 0:
            Delta_P = 0

        mass_lbs = 0.052 * S_FUS ** 1.086 * (n_z * W_O) ** 0.177 * l_HT ** -0.051 * (
            l_FS / d_FS) ** (-0.072) * q ** 0.241 + 11.9 * (V_p * Delta_P) ** 0.271

        self.own_mass = lbs_to_kg(mass_lbs)

    def cg_self(self):
        self.own_cg = np.array([0.5 * self.length, 0., 0.])

    def get_sized(self):
        # TODO update this to work

        for component in self.components:
            component.get_sized()

        self.size_self()
