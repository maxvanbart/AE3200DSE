import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from functools import reduce
from misc.unitConversions import *

# Personnel constants
salaryPilot = 69  # [$/h]
salaryAttendant = 38  # [$/h]
salaryMaintenance = 50  # [$/h]
crewCount = 5  # [-]
annualAttendantSalary = 85e3  # [$]
annualPilotSalary = 175e3  # [$]
# TODO: check this number and unit for cost burden
costBurden = 2  # [$]

# Operational constants
h2_price = 1.9  # [$/kg] as suggested by hydrogen experts
ground_time = 2  # [h]  --> refuelling (depends on fuel) + boarding payload
maintenance_time = 2749  # [h]
block_time_supplement = 1.8  # [h]
f_atc = 0.7  # [-] 0.7 as ATC fees for transatlantic

# CAPEX constants
# TODO: Revise CAPEX calculations to incorporate fuel tank costs properly
P_OEW = 1200  # [$/kg] operating empty weight
W_eng = 200  # Weight per engine [kg]
P_eng = 2600  # [$/kg] engine
P_fc = 608  # [$/kg] fuel cell
P_tank = 550  # [$/kg] LH2

IR = 0.05  # 5% Interest rate
f_rv = 0.1  # 10% Residual value factor
f_ins = 0.005  # 0.5% insurance cost
f_misc = 0.05  # Misc 5% contingency factor to account for new tech
PMac = 0.0  # typically 20% profit margin for manufacturer
DP = 14  # Depreciation period [yrs]

# Return on investment constants
price_per_ticket = 935.80  # Adjusted for inflation expectation in 2040
subsidy = 0.2  # expected subsidy for green aviation


def market_estimations(aircraft):
    # Initialise
    state = aircraft.states['cruise']
    n_pax = aircraft.FuselageGroup.Fuselage.Cabin.passenger_count
    n_motor = aircraft.WingGroup.Engines.own_amount_fans

    flight_range = state.range  # [m]
    block_time = state.duration / 3600 + block_time_supplement  # [h]
    mtow = aircraft.mtom  # [kg]
    fuel_mass = aircraft.fuel_mass  # [kg]
    oew = aircraft.oew  # [kg]
    payload = aircraft.get_payload_mass()  # [kg]

    # Calculate yearly flight cycles
    year_time = 365 * 24  # [h]
    operational_time = year_time - maintenance_time  # [h]
    flight_cycles = operational_time / (block_time + ground_time)  # [-]

    # DOC fuel for a year
    DOC_fuel = flight_cycles * h2_price * fuel_mass

    # DOC fees for a year (payload handling, landing, atc)
    DOC_fees = flight_cycles * (payload * 0.1 + 0.01 * mtow + f_atc * flight_range / 1000 * (mtow / 50 / 1000) ** 0.5)

    # DOC crew
    count_attendant = np.ceil(n_pax / 50)  # [-]
    count_pilot = aircraft.count_pilot  # [-]

    DOC_crew = crewCount * (count_attendant * annualAttendantSalary + count_pilot * annualPilotSalary)

    # DOC maintenance
    DOC_maint_material = oew / 1000 * (0.21 * block_time + 13.7) + 57.5
    DOC_maint_personnel = salaryMaintenance * (1 + costBurden) * (
                (0.655 + 0.01 * oew / 1000) * block_time + 0.254 + 0.01 * oew / 1000)
    ton_force = aircraft.reference_thrust * 0.0001124
    DOC_maint_engine = n_motor * (1.5 * ton_force + 30.5 * block_time + 10.6)
    DOC_maintenance = flight_cycles * (DOC_maint_engine + DOC_maint_material + DOC_maint_personnel)  # [$]

    # DOC capex (engines, fuel cell, fuel tak, cont. factor incl)
    # TODO: Revise price_ac calc. Should the other masses be subtracted from oew?
    a = IR * (1 - f_rv * (1 / (1 + IR)) ** DP) / (1 - (1 / (1 + IR)) ** DP)

    price_ac = (P_OEW * (
                oew - W_eng * n_motor - aircraft.FuselageGroup.Fuselage.AftFuelContainer.own_mass - aircraft.FuselageGroup.Fuselage.ForwardFuelContainer.own_mass
                - aircraft.FuselageGroup.Power.FuelCells.own_mass) + W_eng * n_motor * P_eng
                + (
                            aircraft.FuselageGroup.Fuselage.ForwardFuelContainer.own_mass + aircraft.FuselageGroup.Fuselage.AftFuelContainer.own_mass) * P_tank
                + aircraft.FuselageGroup.Power.FuelCells.own_mass * P_fc) * (1 + PMac + f_misc)

    DOC_cap = price_ac * (a + f_ins)

    DOC = DOC_maintenance + DOC_crew + DOC_fees + DOC_fuel + DOC_cap  # [$]
    available_seat_km = flight_cycles * flight_range * n_pax / 1000
    cost_per_passenger_km = DOC / available_seat_km  # [$/km/passenger]

    # Cost Breakdown [%]
    frac_maintenance = DOC_maintenance / DOC * 100
    frac_crew = DOC_crew / DOC * 100
    frac_fees = DOC_fees / DOC * 100
    frac_fuel = DOC_fuel / DOC * 100
    frac_cap = DOC_cap / DOC * 100

    cost_breakdown = [
        {"cost type": "Maintenance", "fraction": frac_maintenance},
        {"cost type": "Crew", "fraction": frac_crew},
        {"cost type": "Fees", "fraction": frac_fees},
        {"cost type": "Fuel", "fraction": frac_fuel},
        {"cost type": "CAPEX", "fraction": frac_cap}
    ]

    cost_type = list(map(lambda x: x['cost type'], cost_breakdown))
    cost_fraction = list(map(lambda x: x['fraction'], cost_breakdown))

    breakdown_summary = reduce(
        lambda out_str, cost_item: f"{out_str}\n  {cost_item['cost type']} : {cost_item['fraction']:.2f} %",
        cost_breakdown, 'Cost breakdown summary:')

    # Plotting pie chart
    colors = [plt.cm.Pastel1(i) for i in range(20)]
    plt.pie(cost_fraction, labels=cost_type, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title("Cost Breakdown [%]")
    plt.axis('equal')
    # costBreakdownPath = Path("plots","costBreakdown")
    # plt.savefig(costBreakdownPath, dpi = 600)
    plt.savefig(Path("plots", "market_pie.png"))

    # Calculating ROI
    revenue_per_flight = price_per_ticket * n_pax * (1 + subsidy)
    cost_per_flight = cost_per_passenger_km * n_pax * flight_range / 1000
    roi = (revenue_per_flight - cost_per_flight) / cost_per_flight * 100  # [%]
    production_cost_estimation(aircraft)

    return price_ac, cost_per_passenger_km, cost_breakdown, breakdown_summary, roi


def production_cost_estimation(aircraft):
    engineering_cost = 0.4
    me_cost = 0.1
    tool_design_cost = 0.15
    tool_fab_cost = 0.348
    support_cost = 0.047

    # non_recurring_costs = [
    #     {"cost": "Engineering", "fraction": engineering_cost},
    #     {"cost": "ME", "fraction": me_cost},
    #     {"cost": "Tool Design", "fraction": tool_design_cost},
    #     {"cost": "Tool Fab", "fraction": tool_fab_cost},
    #     {"cost": "Support", "fraction": support_cost}
    # ]

    wing_mass = aircraft.WingGroup.Wing.own_mass
    empennage_mass = aircraft.FuselageGroup.Tail.total_mass
    fuselage_mass = aircraft.FuselageGroup.Fuselage.own_mass - empennage_mass
    engine_mass = aircraft.WingGroup.Engines.own_mass
    miscellaneous_mass = aircraft.FuselageGroup.Miscellaneous.own_mass

    wing_cost_density = 17731
    empennage_cost_density = 52156
    fuselage_cost_density = 32093
    engine_cost_density = 8691
    miscellaneous_cost_density = 34307

    wing_mass_usd = lbs_to_kg(wing_cost_density) * wing_mass
    empennage_mass_usd = lbs_to_kg(empennage_cost_density) * empennage_mass
    fuselage_mass_usd = lbs_to_kg(fuselage_cost_density) * fuselage_mass
    engine_mass_usd = lbs_to_kg(engine_cost_density) * engine_mass
    miscellaneous_mass_usd = lbs_to_kg(miscellaneous_cost_density) * miscellaneous_mass

    lst_1 = [engineering_cost, me_cost, tool_design_cost, tool_fab_cost, support_cost]
    lst_2 = [wing_mass_usd, empennage_mass_usd, fuselage_mass_usd, engine_mass_usd, miscellaneous_mass_usd]
    nrc_per_kg = np.array([[item_1 * item_2 for item_1 in lst_1] for item_2 in lst_2])
    print(nrc_per_kg)
