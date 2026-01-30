"""
Physical constants and reference data for lunar lander design.
"""

import numpy as np

# Gravitational accelerations
G0_EARTH = 9.81  # [m/s^2] Standard Earth gravity
G_MOON = 1.62    # [m/s^2] Lunar surface gravity

# Propellant properties - LOX/LH2
RHO_LOX = 1141.0      # [kg/m^3] Liquid oxygen density
RHO_LH2 = 70.5        # [kg/m^3] Liquid hydrogen density
MIXTURE_RATIO_LOX_LH2 = 5.0  # O/F mass ratio for LOX/LH2

# Propellant properties - LOX/Methane (alternative)
RHO_METHANE = 422.0   # [kg/m^3] Liquid methane density

# RL10B-2 Engine (baseline reference)
ISP_RL10B2 = 438.3    # [s] Specific impulse vacuum
THRUST_RL10B2 = 110100  # [N] Thrust

# Helium pressurization
RHO_HELIUM = 0.1786   # [kg/m^3] Helium density at STP

# Mission delta-V requirements (Artemis baseline)
DELTA_V_LLO_TO_SURFACE = 1905  # [m/s] Descent from Low Lunar Orbit
DELTA_V_SURFACE_TO_LLO = 1963  # [m/s] Ascent to Low Lunar Orbit
SAFETY_MARGIN = 1.05            # 5% margin on delta-V

# Typical structural coefficients
K_STRUCTURE_TPS = 1.325  # Structure mass correlation coefficient
K_LANDING_GEAR = 0.08     # Landing gear as fraction of dry mass

# Power system
POWER_REQUIREMENT = 4000  # [W] Baseline power requirement

# ECLSS baseline (4 crew, 15 days)
ECLSS_MASS_BASELINE = 2840.45  # [kg]
ECLSS_VOLUME_BASELINE = 13.52   # [m^3]
ECLSS_POWER_BASELINE = 3160     # [W]

# Avionics baseline
AVIONICS_MASS_BASELINE = 185.805  # [kg]
AVIONICS_VOLUME_BASELINE = 1.5371  # [m^3]
AVIONICS_POWER_BASELINE = 837.9    # [W]

# Thermal control
TCS_AREA_HABITABLE = 66.63  # [m^2] Habitable section area
TCS_HEAT_LOAD = 4500        # [W] Heat load baseline

# Engine sizing parameters
GAMMA_LOX_LH2 = 1.209       # Specific heat ratio
R_GAS_LOX_LH2 = 704.6       # [J/kg*K] Gas constant for mixture
C_STAR_LOX_LH2 = 2323.8     # [m/s] Characteristic velocity
T_CHAMBER_LOX_LH2 = 3241    # [K] Chamber temperature
M_MOLAR_LOX_LH2 = 0.0118    # [kg/mol] Molar mass

# Tank design
TANK_ULLAGE = 0.10  # 10% ullage volume
PRESSURE_CHAMBER = 3.5e6  # [Pa] Chamber pressure (typical)
PRESSURE_EXIT = 10256     # [Pa] Exit pressure (assumed)

# Conversion factors
PSI_TO_PA = 6895  # Conversion factor psi to Pa
