import numpy as np

from balloonSizing import balloonSizing
from dragModel import dragModel
from energyRequired import energyRequired
from fuelMassEstimation import fuelMassEstimation
from fuselageSizing import fuselageSizing
from propulsionSizing import propulsionSizing
from totalMassEstimation import totalMassEstimation
from wingSizing import wingSizing


def preliminaryDesign(parameters):
    """Perform preliminary design using design parameters"""

    fuselageSizing(parameters)

    rho =  # get rho from isa function

    parameters["totalMass"] = parameters["fuselageMass"]

    i = 0
    while i < 10000:
        # wing
        wingSizing(parameters, rho)

        # balloon sizing
        balloonSizing(parameters, rho)

        # drag model
        dragModel(parameters, rho)

        # propulsion sizing

        # energy required

        # fuel mass estimation

        # total mass

        # check if converged

        i += 1

    return parameters
