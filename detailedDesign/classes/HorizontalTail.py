# To check
import numpy as np
from detailedDesign.classes.Component import Component
from misc.unitConversions import *


class HorizontalTail(Component):
    def __init__(self, Tail, design_config):
        super().__init__(design_config)

        self.Tail = Tail
        self.parent = self.Tail

        self.tail_length = None  # [m]
        self.surface_area = None  # [m2]
        self.mean_geometric_chord = None  # [m]
        self.span = 1  # [m]
        self.root_chord = 1  # [m]
        self.quarter_chord_sweep = None  # [rad]
        self.length = None
        self.x_aerodynamic_center = None
        self.installation_angle = None
        self.d_alphah_d_alpha = None

        # Create all the parameters that this component must have here:
        # Using self.property_name = value
        self._freeze()

    def size_self(self):
        self.size_self_geometry()
        self.size_self_mass()
        self.pos = np.array([- self.mean_geometric_chord, 0., 0.])

    @property
    def leading_edge_sweep(self):
        return np.arctan(np.tan(self.three_quarter_chord_sweep) - 4 / self.aspect_ratio * -0.75 * (1 - self.taper) / (1 + self.taper))

    @property
    def tip_chord(self):
        return self.root_chord * self.taper

    def size_self_geometry(self):
        # Sizing dimensions
        wing_area = self.Tail.FuselageGroup.Aircraft.reference_area  # [m2]
        # [m]
        wing_mean_geometric_chord = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.mean_geometric_chord

        y_mean_geometric_chord = self.span / 6 * (1 + self.taper * 2) / (1 + self.taper)
        quarter_chord_sweep = np.arctan(np.tan(self.three_quarter_chord_sweep) - 4 / self.aspect_ratio * (0.25 - 0.75) * (1 - self.taper) / (1 + self.taper))
        # distance from leading edge of root chord
        x_aerodynamic_center = self.root_chord * 0.26 + y_mean_geometric_chord * np.sin(quarter_chord_sweep) 
        self.x_aerodynamic_center = self.Tail.FuselageGroup.Fuselage.length - self.root_chord + x_aerodynamic_center
        self.tail_length = self.x_aerodynamic_center - self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.x_aerodynamic_center

        self.logger.debug(f"{self.tail_length = }")

        self.surface_area = (self.volume_coefficient * wing_area *
                             wing_mean_geometric_chord) / self.tail_length   # [m2]

        self.span = np.sqrt(self.aspect_ratio * self.surface_area)  # [m]

        average_chord = self.span / self.aspect_ratio  # [m]
        self.root_chord = (2 * average_chord)/(1 + self.taper)  # [m]
        self.mean_geometric_chord = 2/3 * self.root_chord * \
            ((1 + self.taper + self.taper**2)/(1 + self.taper))  # [m]

        self.length = self.root_chord

        self.d_alphah_d_alpha = 1 - self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.d_epsilon_d_alpha
        

    @property
    def C_L_alpha(self):
        aspect_ratio = self.aspect_ratio
        V_C = self.Tail.FuselageGroup.Aircraft.states['cruise'].velocity
        speed_of_sound = self.Tail.FuselageGroup.Aircraft.states['cruise'].speed_of_sound
        beta = np.sqrt((1 - (V_C / speed_of_sound) ** 2))
        semi_chord_sweep = np.arctan(np.tan(self.quarter_chord_sweep - (4 / aspect_ratio) * ((0.5-0.25)* ((1 - self.taper)/(1 + self.taper)))))  # [rad]
        k = 1
        C_L_alpha = (2 * np.pi * aspect_ratio) / (2 + np.sqrt(((aspect_ratio * beta) / k) ** 2
                    * (1 + (np.tan(semi_chord_sweep) ** 2) / (beta ** 2)) + 4))
        return np.deg2rad(C_L_alpha)

    def get_C_L(self):
        x_cg = self.Tail.FuselageGroup.Aircraft.cg_loaded_half_fuel[0]
        x_ac_h = self.x_aerodynamic_center 
        x_ac_w = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.x_aerodynamic_center
        z = self.Tail.FuselageGroup.Aircraft.WingGroup.Engines.z_offset_from_cg
        thrust = self.Tail.FuselageGroup.Aircraft.cruise_drag
        wing_area = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.wing_area 
        mean_geometric_chord_wing = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.mean_geometric_chord
        C_L_H_term = - 1 / (0.9 * self.surface_area /\
                    wing_area * (x_ac_h - x_cg))
        C_L = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.get_C_L(self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.installation_angle)
        C_L_term = C_L * (x_cg - x_ac_w) / mean_geometric_chord_wing
        installation_angle_wing = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.installation_angle
        C_m_w = self.Tail.FuselageGroup.Aircraft.WingGroup.Wing.get_C_m(installation_angle_wing)
        C_m_fus = 0
        dynamic_pressure = self.Tail.FuselageGroup.Aircraft.states["cruise"].dynamic_pressure
        thrust_term = thrust * z / (dynamic_pressure * wing_area * mean_geometric_chord_wing)
        return  C_L_H_term * (C_L_term + C_m_w + C_m_fus + thrust_term)

    def get_installation_angle(self, C_L):
        angle = C_L / (2 * np.pi)
        return np.rad2deg(angle)

        




    def size_self_mass(self):
        # Sizing mass
        WingGroup = self.Tail.FuselageGroup.Aircraft.WingGroup
        FuselageGroup = self.Tail.FuselageGroup

        state = FuselageGroup.Aircraft.states["cruise"]

        q = pa_to_psf(0.5 * state.density * state.velocity ** 2)   # [psi]
        n_z = FuselageGroup.Aircraft.ultimate_load_factor   # [-]
        W_O = kg_to_lbs(FuselageGroup.Aircraft.mtom)   # [lbs]

        S_HT = m2_to_ft2(self.surface_area)  # [ft2]
        thickness_to_chord = WingGroup.Wing.thickness_chord_ratio   # [-]

        cruise_C_L = self.get_C_L()
        self.installation_angle = self.get_installation_angle(cruise_C_L)

        # TODO: check MDN
        self.quarter_chord_sweep = np.arctan(np.tan(self.three_quarter_chord_sweep) - 4/self.aspect_ratio * ((0.25 - 0.75)*((1 - self.taper)
                                                                                                                            / (1 + self.taper))))  # [rad]

        # this is now literally taken from Raymer, might have to take both sweeps of the horizontal tail
        mass_lbs = 0.016 * ( (n_z * W_O) ** 0.414) * (q ** 0.168 )* (S_HT ** 0.896 )* (((100 * thickness_to_chord) / np.cos(
            WingGroup.Wing.sweep)) ** (-0.12)) * ((self.aspect_ratio / (np.cos(self.quarter_chord_sweep) ** 2)) ** 0.043) * (self.taper ** (-0.02))

        self.own_mass = lbs_to_kg(mass_lbs)  # [kg]

    def cg_self(self):
        x_cg = 0.4 * self.mean_geometric_chord
        y_cg = 0
        z_cg = 0  # Might change with changing alpha incidence
        self.own_cg = np.array([x_cg, y_cg, z_cg])
