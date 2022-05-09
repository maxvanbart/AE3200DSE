import numpy as np


def dragModel(params, rho):
    Cd = get_drag(params, rho)
    D = 0.5 * rho * params['velocity'] ** 2 * \
        Cd * params['balloonVolume'] ** (2 / 3)
    params['totalDrag'] = D


def FFB(finesseratio):
    return 1 + 1.5/(finesseratio**(2/3)) + 7/(finesseratio**(3))


def FFW(tOverC):
    return 1 + 1.2*tOverC + 100 * tOverC**4


def Swet_balloon(volume, finesseratio):
    return 3.88 * volume**(2/3) * finesseratio ** (1/3)


def get_visc(altitude):
    # Sutherland's formula
    # https://www.grc.nasa.gov/www/k-12/airplane/viscosity.html
    visc0 = 1.716e-5  
    T0_R = 273  
    Delta_T = (6.5/1000) * altitude  # degree celsius
    # http://fisicaatmo.at.fcen.uba.ar/practicas/ISAweb.pdf
    T = T0_R - Delta_T
    visc = visc0 * ((T/T0_R)**1.5) * ((T0_R + 111)/(T + 111))
    return visc


def get_oswald_efficiency(aspectRatio, leadingEdgeSweep):
    if leadingEdgeSweep <= np.deg2rad(30): #degree
        return 1.78*(1 - aspectRatio ** 0.68) - 0.64
    else: 
        return 4.61 * (1 - 0.054 * aspectRatio ** 0.68) * ( np.cos( leadingEdgeSweep ))

def estimate_wing_FF(maxThicknessLocationAirfoil, tOverC, machNumber):
    return (1 + 0.6/maxThicknessLocationAirfoil*tOverC + 100*tOverC**4)*(1.34*\
            machNumber**0.18*np.cos(maxThicknessSweep)**0.28)

def estimate_fuselage_FF(fuselageLength, fuselageDiameter):
    fFactor = fuselageLength/fuselageDiameter
    return 1 + 60/(f ** 3) + f / 400


def get_CD_0(params, rho):
    FFb = FFB(params["balloonFinesseRatio"])

    FFw = FFW(params["thicknessOverChord"])

    Swetb = Swet_balloon(params["balloonVolume"],
                         params["balloonFinesseRatio"])

    Swetw = 2 * params['wingArea']

    bw = np.sqrt(params['wingArea']*params['wingAspectRatio'])

    visc = get_visc(params["altitude"])

    Reb = (rho * params['velocity'] * params['balloonLength']) / visc

    Rew = (rho * params['velocity'] * bw) / visc

    Cfb = 0.455/(np.log10(Reb)**2.58)

    Cfw = 0.455/(np.log10(Rew)**2.58)


    CDF = (Cfb * FFb * Swetb) / (params["balloonVolume"]**(2/3)) + \
        (Cfw * FFw * Swetw) / (params["balloonVolume"]**(2/3))

    CD_0 = (CDF) / 0.95
    return CD_0


def estimate_CL_alpha(aspectRatio, sweep=0):
    return 2 * np.pi * aspectRatio/(2 + np.sqrt(4 + aspectRatio*aspectRatio * (1 + np.tan(sweep)**2)))


def estimate_K_factor(aspectRatio):
    return -0.0145*(aspectRatio)**(-4)+0.182*(aspectRatio)**(-3) - \
        0.514*(aspectRatio)**(-2) + 0.838*(1/aspectRatio) - 0.053


def determine_balloon_ar(volume, width):
    return width*width/(2 * volume ** (2/3))


def get_CD_i(params):
    balloonAr = determine_balloon_ar(
        params['balloonVolume'], params['balloonRadius']*2)
    balloonAoA = np.deg2rad(2)  # deg
    balloonC_L = balloonAoA * estimate_CL_alpha(balloonAr)
    wingC_L = params['wingC_L_design']
    kFactor = estimate_K_factor(balloonAr)
    balloonC_D_i = kFactor * balloonC_L ** 2
    conversionRatioWingDrag = params['wingArea'] / \
        (params['balloonVolume'] ** (2/3))
    wingC_D_i = wingC_L**2 / \
        (np.pi * params['wingAspectRatio'] * 0.8) * conversionRatioWingDrag
    return balloonC_D_i + wingC_D_i


def get_drag(params, rho):
    return get_CD_0(params, rho) + get_CD_i(params)
