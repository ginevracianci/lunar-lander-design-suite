"""
Propellant mass and volume calculations for lunar lander missions.

This module calculates propellant requirements for descent and ascent phases
using the Tsiolkovsky rocket equation and provides tank sizing with ullage.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional
from .utils.constants import (
    G0_EARTH, RHO_LOX, RHO_LH2, MIXTURE_RATIO_LOX_LH2, 
    DELTA_V_LLO_TO_SURFACE, DELTA_V_SURFACE_TO_LLO, TANK_ULLAGE
)


def calculate_propellant_descent_ascent(
    inert_mass: float,
    delta_v_descent: float,
    delta_v_ascent: float,
    isp: float,
    g0: float = G0_EARTH,
    mixture_ratio: float = MIXTURE_RATIO_LOX_LH2
) -> Tuple[float, float]:
    """
    Calculate propellant mass needed for descent and ascent using Tsiolkovsky equation.
    
    The calculation accounts for the fact that ascent propellant must be carried
    during descent, thus increasing the descent propellant requirement.
    
    Parameters
    ----------
    inert_mass : float
        Inert mass (dry mass + payload) [kg]
    delta_v_descent : float
        Delta-V for descent (LLO to surface) [m/s]
    delta_v_ascent : float
        Delta-V for ascent (surface to LLO) [m/s]
    isp : float
        Specific impulse [s]
    g0 : float, optional
        Standard gravity [m/s^2], default is Earth gravity
    mixture_ratio : float, optional
        O/F mixture ratio, default is 5.0 for LOX/LH2
        
    Returns
    -------
    propellant_ascent : float
        Propellant mass for ascent [kg]
    propellant_descent : float
        Propellant mass for descent [kg]
        
    Notes
    -----
    Uses Tsiolkovsky equation: m_prop = m_inert * (exp(ΔV/(Isp*g0)) - 1)
    
    The ascent propellant is calculated first, then added to inert mass for
    descent calculation, since it must be carried down to the surface.
    
    Examples
    --------
    >>> prop_asc, prop_desc = calculate_propellant_descent_ascent(
    ...     inert_mass=10000, delta_v_descent=1905, delta_v_ascent=1963,
    ...     isp=438.3
    ... )
    >>> print(f"Ascent: {prop_asc:.0f} kg, Descent: {prop_desc:.0f} kg")
    """
    # Calculate ascent propellant first
    propellant_ascent = inert_mass * (np.exp(delta_v_ascent / (isp * g0)) - 1)
    
    # For descent, we must carry the ascent propellant as additional inert mass
    mass_at_descent = inert_mass + propellant_ascent
    propellant_descent = mass_at_descent * (np.exp(delta_v_descent / (isp * g0)) - 1)
    
    return propellant_ascent, propellant_descent


def split_propellant_lox_lh2(
    total_propellant: float,
    mixture_ratio: float = MIXTURE_RATIO_LOX_LH2
) -> Tuple[float, float]:
    """
    Split total propellant mass into hydrogen and oxygen components.
    
    Parameters
    ----------
    total_propellant : float
        Total propellant mass [kg]
    mixture_ratio : float, optional
        O/F mixture ratio (default 5.0 for LOX/LH2)
        
    Returns
    -------
    m_hydrogen : float
        Hydrogen mass [kg]
    m_oxygen : float
        Oxygen mass [kg]
        
    Examples
    --------
    >>> m_h2, m_o2 = split_propellant_lox_lh2(12000, mixture_ratio=5.0)
    >>> print(f"H2: {m_h2:.0f} kg, O2: {m_o2:.0f} kg")
    """
    m_hydrogen = total_propellant / (mixture_ratio + 1)
    m_oxygen = total_propellant - m_hydrogen
    
    return m_hydrogen, m_oxygen


def calculate_propellant_volumes(
    m_hydrogen: float,
    m_oxygen: float,
    rho_h2: float = RHO_LH2,
    rho_o2: float = RHO_LOX,
    ullage_factor: float = TANK_ULLAGE
) -> Tuple[float, float, float, float]:
    """
    Calculate propellant volumes and tank volumes including ullage.
    
    Parameters
    ----------
    m_hydrogen : float
        Hydrogen mass [kg]
    m_oxygen : float
        Oxygen mass [kg]
    rho_h2 : float, optional
        Liquid hydrogen density [kg/m^3]
    rho_o2 : float, optional
        Liquid oxygen density [kg/m^3]
    ullage_factor : float, optional
        Ullage margin (default 0.10 for 10% extra volume)
        
    Returns
    -------
    vol_h2 : float
        Hydrogen propellant volume [m^3]
    vol_o2 : float
        Oxygen propellant volume [m^3]
    vol_tank_h2 : float
        Hydrogen tank volume with ullage [m^3]
    vol_tank_o2 : float
        Oxygen tank volume with ullage [m^3]
        
    Examples
    --------
    >>> vol_h2, vol_o2, tank_h2, tank_o2 = calculate_propellant_volumes(2000, 10000)
    >>> print(f"H2 tank: {tank_h2:.1f} m³, O2 tank: {tank_o2:.1f} m³")
    """
    # Propellant volumes
    vol_h2 = m_hydrogen / rho_h2  # m^3
    vol_o2 = m_oxygen / rho_o2    # m^3
    
    # Tank volumes with ullage
    vol_tank_h2 = vol_h2 * (1 + ullage_factor)
    vol_tank_o2 = vol_o2 * (1 + ullage_factor)
    
    return vol_h2, vol_o2, vol_tank_h2, vol_tank_o2


def estimate_propellant_lunar_mission(
    inert_mass: float,
    delta_v_descent: float = DELTA_V_LLO_TO_SURFACE,
    delta_v_ascent: float = DELTA_V_SURFACE_TO_LLO,
    isp: float = 438.3,
    g0: float = G0_EARTH,
    mixture_ratio: float = MIXTURE_RATIO_LOX_LH2,
    rho_h2: float = RHO_LH2,
    rho_o2: float = RHO_LOX,
    ullage_factor: float = TANK_ULLAGE
) -> Tuple[float, float, float, float, float, float]:
    """
    Complete propellant estimation for lunar descent and ascent mission.
    
    This is the main function that combines all propellant calculations.
    
    Parameters
    ----------
    inert_mass : float
        Inert mass (dry mass + payload) [kg]
    delta_v_descent : float, optional
        Delta-V for descent [m/s]
    delta_v_ascent : float, optional
        Delta-V for ascent [m/s]
    isp : float, optional
        Specific impulse [s]
    g0 : float, optional
        Standard gravity [m/s^2]
    mixture_ratio : float, optional
        O/F mixture ratio
    rho_h2 : float, optional
        Hydrogen density [kg/m^3]
    rho_o2 : float, optional
        Oxygen density [kg/m^3]
    ullage_factor : float, optional
        Ullage margin fraction
        
    Returns
    -------
    m_hydrogen : float
        Total hydrogen mass [kg]
    m_oxygen : float
        Total oxygen mass [kg]
    vol_h2 : float
        Hydrogen volume [m^3]
    vol_o2 : float
        Oxygen volume [m^3]
    vol_tank_h2 : float
        Hydrogen tank volume with ullage [m^3]
    vol_tank_o2 : float
        Oxygen tank volume with ullage [m^3]
        
    Examples
    --------
    >>> results = estimate_propellant_lunar_mission(inert_mass=10000)
    >>> m_h2, m_o2, v_h2, v_o2, vt_h2, vt_o2 = results
    >>> print(f"Total propellant: {m_h2 + m_o2:.0f} kg")
    """
    # Calculate propellant for descent and ascent
    prop_ascent, prop_descent = calculate_propellant_descent_ascent(
        inert_mass, delta_v_descent, delta_v_ascent, isp, g0, mixture_ratio
    )
    
    # Total propellant
    total_propellant = prop_ascent + prop_descent
    
    # Split into hydrogen and oxygen
    m_hydrogen, m_oxygen = split_propellant_lox_lh2(total_propellant, mixture_ratio)
    
    # Calculate volumes
    vol_h2, vol_o2, vol_tank_h2, vol_tank_o2 = calculate_propellant_volumes(
        m_hydrogen, m_oxygen, rho_h2, rho_o2, ullage_factor
    )
    
    return m_hydrogen, m_oxygen, vol_h2, vol_o2, vol_tank_h2, vol_tank_o2


def plot_propellant_breakdown(
    m_hydrogen: float,
    m_oxygen: float,
    inert_mass: float
) -> None:
    """
    Create a pie chart showing propellant mass breakdown.
    
    Parameters
    ----------
    m_hydrogen : float
        Hydrogen mass [kg]
    m_oxygen : float
        Oxygen mass [kg]
    inert_mass : float
        Inert mass [kg]
    """
    total_mass = m_hydrogen + m_oxygen + inert_mass
    
    masses = [m_hydrogen, m_oxygen, inert_mass]
    labels = ['Hydrogen', 'Oxygen', 'Inert (Dry + Payload)']
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, texts, autotexts = ax.pie(
        masses, labels=labels, colors=colors, autopct='%1.1f%%',
        startangle=90, textprops={'fontsize': 12}
    )
    
    ax.set_title(f'Lunar Lander Mass Breakdown\nTotal: {total_mass:.0f} kg', 
                 fontsize=14, fontweight='bold')
    
    # Add legend with actual masses
    legend_labels = [f'{label}: {mass:.0f} kg' for label, mass in zip(labels, masses)]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.show()


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("LUNAR LANDER PROPELLANT SYSTEM ANALYSIS")
    print("=" * 70)
    
    # Mission parameters
    inert_mass = 10000  # kg
    delta_v_descent = 1905 * 1.05  # m/s (with 5% margin)
    delta_v_ascent = 1963 * 1.05   # m/s (with 5% margin)
    isp = 438.3  # s (RL10B-2 engine)
    
    print(f"\nMission Parameters:")
    print(f"  Inert mass:      {inert_mass:>8.0f} kg")
    print(f"  ΔV descent:      {delta_v_descent:>8.1f} m/s")
    print(f"  ΔV ascent:       {delta_v_ascent:>8.1f} m/s")
    print(f"  Specific impulse: {isp:>7.1f} s")
    
    # Calculate propellant
    m_h2, m_o2, v_h2, v_o2, vt_h2, vt_o2 = estimate_propellant_lunar_mission(
        inert_mass, delta_v_descent, delta_v_ascent, isp
    )
    
    total_propellant = m_h2 + m_o2
    total_mass = inert_mass + total_propellant
    mass_ratio = total_mass / inert_mass
    
    print(f"\nPropellant Results:")
    print(f"  Hydrogen:        {m_h2:>8.0f} kg  ({100*m_h2/total_propellant:>5.1f}%)")
    print(f"  Oxygen:          {m_o2:>8.0f} kg  ({100*m_o2/total_propellant:>5.1f}%)")
    print(f"  Total propellant: {total_propellant:>7.0f} kg")
    print(f"\nMass Summary:")
    print(f"  Total mass:      {total_mass:>8.0f} kg")
    print(f"  Mass ratio:      {mass_ratio:>8.3f}")
    print(f"  Propellant frac: {100*total_propellant/total_mass:>7.1f}%")
    
    print(f"\nTank Volumes:")
    print(f"  H2 propellant:   {v_h2:>8.2f} m³")
    print(f"  O2 propellant:   {v_o2:>8.2f} m³")
    print(f"  H2 tank (w/ ullage): {vt_h2:>6.2f} m³")
    print(f"  O2 tank (w/ ullage): {vt_o2:>6.2f} m³")
    
    print("\n" + "=" * 70)
