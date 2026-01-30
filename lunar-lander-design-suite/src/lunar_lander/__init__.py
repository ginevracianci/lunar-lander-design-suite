"""
Lunar Lander Design Suite

A Python package for preliminary design and sizing of lunar landers using
systems engineering and concurrent design methodologies.

Main Components:
- Mass estimation (statistical methods)
- Propellant system sizing (LOX/LH2)
- Propulsion system design (engines + tanks)
- Subsystems integration (EPS, TCS, AOCS, ECLSS)
- Iterative mass closure analysis

Author: Ginevra Cianci
Institution: Politecnico di Torino / Politecnico di Milano
Date: January 2026
"""

__version__ = "1.0.0"
__author__ = "Ginevra Cianci"

from .mission_analyzer import LunarLanderDesigner
from .mass_estimation import (
    estimate_masses_statistical,
    estimate_payload_requirements
)
from .propellant_system import estimate_propellant_lunar_mission
from .propulsion_system import RocketEngine, CryogenicTank, design_propulsion_system

__all__ = [
    'LunarLanderDesigner',
    'estimate_masses_statistical',
    'estimate_payload_requirements',
    'estimate_propellant_lunar_mission',
    'RocketEngine',
    'CryogenicTank',
    'design_propulsion_system'
]
