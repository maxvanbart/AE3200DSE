import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from misc.constants import g, energyDensityHydrogen
from detailedDesign.get_drag import get_drag


def make_payload_range_diagram(aircraft):
    fg = aircraft.FuselageGroup.Fuselage  # [Fuselage]
    max_fuel_mass = fg.AftFuelContainer.mass_H2 + fg.AssFuelContainer.mass_H2 + fg.ForwardFuelContainer.mass_H2  # [kg]

    # This factor decides how much fuel will be exchanged for additional payload weight
    # TODO: change this
    fuel_dump_percentage = 0.2  # [-]

    # print("HELLO FUEL:", max_fuel_mass, aircraft.fuel_mass)
    # TODO: check the source of the fuel masses since there seem to be conflicting variables
    total_fuel_capacity = max_fuel_mass

    MTOM = aircraft.mtom
    payload_mass = aircraft.get_payload_mass

    m1 = MTOM  # mtom and no fuel
    m_f1 = 0
    m2 = MTOM  # mtom with max payload and 80% fuel
    m_f2 = total_fuel_capacity * (1 - fuel_dump_percentage)
    m3 = MTOM  # mtom with max fuel and rest payload
    m_f3 = total_fuel_capacity
    m4 = MTOM - payload_mass  # mtom without any payload
    m_f4 = total_fuel_capacity

    p = [payload_mass + fuel_dump_percentage * total_fuel_capacity, payload_mass + fuel_dump_percentage * total_fuel_capacity, payload_mass, 0]
    r = [calc_range(m1, m1 - m_f1, aircraft), calc_range(m2, m2 - m_f2, aircraft), calc_range(m3, m3 - m_f3, aircraft), calc_range(m4, m4 - m_f4, aircraft)]
    print("total fuel capacity:", total_fuel_capacity)

    p, r = np.array(p), np.array(r)
    r = r * 10 ** -3
    p = p

    plt.figure()
    plt.grid()
    plt.plot(r, p, "o-")
    for x, y, i in zip(r, p, range(4)):
        plt.annotate(i+1, (x+100, y+50000/20))

    plt.title("Payload Range Diagram")
    plt.xlabel("Range [km]")
    plt.ylabel("Payload mass [kg]")
    # plt.xticks(fontsize=11)
    # plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.savefig(Path("plots", "payload_range_diagram.pdf"))


def calc_range(W0, W1, aircraft):
    print("Fraction W5/W4:", W1/W0)
    prop_eff = aircraft.FuselageGroup.Power.propulsive_efficiency
    c_p = 1 / energyDensityHydrogen

    # TODO: implement realistic L/D
    L = (aircraft.mtom - 0.5 * (W0 - W1)) * 9.81
    D = aircraft.cruise_drag
    L_over_D_cruise = L / D

    # Range formula from ADSEE I
    power = aircraft.FuselageGroup.Power

    result = (prop_eff / g / c_p) * L_over_D_cruise * np.log(W0 / W1 * power.fuel_fraction_misc * power.fuel_fraction_loiter)

    return max(result, 0)

def calc_range(W0, W1, aircraft):
    print("Fraction W5/W4:", W1/W0)
    prop_eff = aircraft.FuselageGroup.Power.propulsive_efficiency
    c_p = 1 / energyDensityHydrogen

    # TODO: implement realistic L/D
    L = (aircraft.mtom - 0.5 * (W0 - W1)) * 9.81
    D = aircraft.cruise_drag
    L_over_D_cruise = L / D

    # Range formula from ADSEE I
    power = aircraft.FuselageGroup.Power

    result = (prop_eff / g / c_p) * L_over_D_cruise * np.log(W0 / W1 * power.fuel_fraction_misc * power.fuel_fraction_loiter)

    return max(result, 0)
