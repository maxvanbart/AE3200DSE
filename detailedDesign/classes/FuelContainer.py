from detailedDesign.classes.Component import Component
import numpy as np


class FuelContainer(Component):
    def __init__(self, Fuselage, design_config):
        super().__init__(design_config)

        self.Fuselage = Fuselage

        # self.RemovableContainers = []
        # self.NonRemovableContainers = []
        # self.components = self.RemovableContainers + self.NonRemovableContainers

        # Create all the parameters that this component must have here:
        # Using self.property_name = value
        self.thickness = 0
        self.inner_diameter = None
        self.inner_radius = None

        self.volume_tank = None
        self.length = None
        self.voltage = None
        self.flow_H2 = None
        self.mass_H2 = None
        self.volume_tank = None
        self.radius_tank = None
        self.mass_tank = None
        self.area_tank = None


        # self.fatiguestrength = 103*10**6 #[MPa], fatigue strength Al 2219-T81 after 500e6 cycles
        # self.yieldstrength = 352*10**6 #[MPa], yield strength Al 2219-T81
        self.SF = 1.5

        # self.density_H2 = 71 # [kg/m3], density LH2
        # self.Vi = 0.072 # extra volume needed for boiloff (literature)

        self._freeze()

    def size_self(self):

        self.inner_diameter = self.Fuselage.inner_diameter - self.thickness * 2
        self.inner_radius = self.inner_diameter/2

        thickness_fatigue = self.tank_pressure*self.inner_radius*self.SF/self.fatiguestrength
        thickness_yield = self.tank_pressure*self.inner_radius*self.SF/(self.yieldstrength)

        self.thickness = max(thickness_fatigue, thickness_yield)

        self.volume_tank = self.mass_H2*(1+self.Vi)/self.density_H2
        self.length = (self.volume_tank - 4*np.pi*self.inner_radius**3/3)/(np.pi*self.inner_radius**2) # we constrained the radius as being an integral tank,\
                                                                                                                #normally the radius is found through this eq

        self.voltage = 1.2*self.Fuselage.FuselageGroup.Power.FuelCells.conversion_efficiency
        # self.power_produced = self.voltage*Aircraft.FuselageGroup.Power.FuelCells.current_density* areafuelcell


        powertest = 600000000

        self.flow_H2 = powertest/(self.voltage*self.Fuselage.FuselageGroup.Power.FuelCells.conversion_efficiency*2*96500*500) #GET POWER FROM PAULA
        self.mass_H2 = self.flow_H2*self.Fuselage.FuselageGroup.Power.FuelCells.duration_flight/(32167*self.Fuselage.FuselageGroup.Power.FuelCells.conversion_efficiency)

        self.volume_tank = self.mass_H2* (1+self.Vi)/self.density_H2
        self.radius_tank = self.inner_radius
        self.mass_tank = self.tank_pressure*4/3*np.pi*(self.radius_tank+self.thickness)**3+np.pi*(self.radius_tank+self.thickness)**2*self.length-self.volume_tank
        self.area_tank = 4*np.pi*self.radius_tank**2+2*np.pi*self.radius_tank*self.length


        thickness_insulation = range(0,20)
        Q_conduction = []
        Q_flow = []
        boiloff_rate = []
        for i in self.thickness_insulation:
            Q_conduction = self.thermal_cond*(self.temp_room-self.temp_LH2)/thickness_insulation
            Q_flow = Q_conduction*self.area_tank
            boiloff_rate = Q_flow/self.E_boiloff
            total_boiloff = boiloff_rate*self.Fuselage.FuselageGroup.Power.FuelCells.duration_flight*3600
            mass_total = total_boiloff+self.mass_tank




