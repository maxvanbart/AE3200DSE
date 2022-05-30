import numpy as np
from pathlib import Path

from misc.openData import openData
from detailedDesign.classes.Aircraft import Aircraft
from detailedDesign.performAnalyses import perform_analyses
from detailedDesign.getConstraints import get_constraints
from detailedDesign.classes.State import State
from detailedDesign.historicalRelations import get_MTOM_from_historical_relations
from detailedDesign.log import setup_custom_logger


def get_ultimate_load_factor():
    # N_max_des = None # from maneuver/gust diagram
    # N_ult = 1.5*N_max_des # CS25 reg (sam's summaries)
    GUESS_AT_LOAD_FACTOR = 3
    return GUESS_AT_LOAD_FACTOR


def detail_design(debug=False):

    logger = setup_custom_logger("logger", debug)
    states = {"cruise": State('cruise')}

    # State in state
    config_file = Path('data', 'new_designs', 'config.yaml')
    aircraft = Aircraft(openData(config_file), states, debug=True)

    aircraft.mtom = get_MTOM_from_historical_relations(aircraft)
    previous_mtom = aircraft.mtom  # For checking convergence

    # Size the cabin and cargo bay as it is constant and is a dependency for other components
    pre_run = aircraft.FuselageGroup.Fuselage
    pre_run.Cabin.size_self()
    pre_run.CargoBay.size_self()

    # Magical Disney Loop
    while True:
        get_constraints(aircraft)

        aircraft.ultimate_load_factor = get_ultimate_load_factor()

        aircraft.get_sized()
        logger.debug(f"{ aircraft.mtom = }")
        # Check divergence
        # Check divergence
        if np.isnan(aircraft.mtom):
            logger.warn("DIVERGED :(")
            break

        # Check convergence
        if aircraft.mtom - previous_mtom < 5:
            logger.warn("CONVERGED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            break
        previous_mtom = aircraft.mtom

    perform_analyses(aircraft)


if __name__ == "__main__":
    detail_design(debug=True)
