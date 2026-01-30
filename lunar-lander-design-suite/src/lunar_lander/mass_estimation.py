"""
Statistical mass estimation for lunar lander based on historical data.

This module provides functions to estimate payload, dry mass, and inert mass
based on total vehicle mass using polynomial regression from historical lander data.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional
import pandas as pd

# Historical lander database (from Dati.xlsx)
HISTORICAL_DATA = {
    'total_mass': np.array([15200, 4700, 10300, 23375, 15847, 43400]),  # kg
    'payload': np.array([2100, 1400, 640, 2480, 1600]),  # kg (5 points, excluding index 5)
    'dry_mass': np.array([2180, 2033, 2245, 3547, 2435])  # kg (5 points)
}


def estimate_payload_from_total_mass(
    total_mass: float,
    plot: bool = False
) -> float:
    """
    Estimate payload mass from total vehicle mass using polynomial regression.
    
    Based on historical lunar lander data, uses 2nd order polynomial fit.
    
    Parameters
    ----------
    total_mass : float
        Total vehicle mass [kg]
    plot : bool, optional
        If True, displays the regression plot
        
    Returns
    -------
    float
        Estimated payload mass [kg]
        
    Examples
    --------
    >>> payload = estimate_payload_from_total_mass(30000)
    >>> print(f"Estimated payload: {payload:.0f} kg")
    """
    # Historical data (excluding 5th element for payload)
    total_hist = HISTORICAL_DATA['total_mass'][[0, 1, 2, 3, 5]]
    payload_hist = HISTORICAL_DATA['payload']
    
    # 2nd order polynomial fit
    coeffs = np.polyfit(total_hist, payload_hist, 2)
    payload_estimated = np.polyval(coeffs, total_mass)
    
    if plot:
        x_range = np.linspace(0, 40000, 1000)
        y_fit = np.polyval(coeffs, x_range)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x_range, y_fit, 'b-', linewidth=2, label='Polynomial fit')
        plt.plot(total_hist, payload_hist, 'go', markersize=12, label='Historical data')
        plt.plot(total_mass, payload_estimated, 'r*', markersize=15, label='Estimation')
        plt.xlim(0, 40000)
        plt.ylim(0, 3000)
        plt.xlabel('Total Mass [kg]', fontsize=12)
        plt.ylabel('Payload [kg]', fontsize=12)
        plt.title('Payload Estimation from Total Mass', fontsize=14)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    return float(payload_estimated)


def estimate_dry_mass_from_total_mass(
    total_mass: float,
    plot: bool = False
) -> float:
    """
    Estimate dry mass from total vehicle mass using polynomial regression.
    
    Dry mass excludes propellant but includes all structure, systems, and payload.
    
    Parameters
    ----------
    total_mass : float
        Total vehicle mass [kg]
    plot : bool, optional
        If True, displays the regression plot
        
    Returns
    -------
    float
        Estimated dry mass [kg]
        
    Examples
    --------
    >>> dry_mass = estimate_dry_mass_from_total_mass(30000)
    >>> print(f"Estimated dry mass: {dry_mass:.0f} kg")
    """
    # Historical data (first 5 elements)
    total_hist = HISTORICAL_DATA['total_mass'][:5]
    dry_hist = HISTORICAL_DATA['dry_mass']
    
    # 2nd order polynomial fit
    coeffs = np.polyfit(total_hist, dry_hist, 2)
    dry_mass_estimated = np.polyval(coeffs, total_mass)
    
    if plot:
        x_range = np.linspace(0, 40000, 1000)
        y_fit = np.polyval(coeffs, x_range)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x_range, y_fit, 'b-', linewidth=2, label='Polynomial fit')
        plt.plot(total_hist, dry_hist, 'go', markersize=12, label='Historical data')
        plt.plot(total_mass, dry_mass_estimated, 'r*', markersize=15, label='Estimation')
        plt.xlim(0, 40000)
        plt.ylim(0, 10000)
        plt.xlabel('Total Mass [kg]', fontsize=12)
        plt.ylabel('Dry Mass [kg]', fontsize=12)
        plt.title('Dry Mass Estimation from Total Mass', fontsize=14)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    return float(dry_mass_estimated)


def estimate_masses_statistical(
    total_mass: float,
    plot: bool = False
) -> Tuple[float, float, float]:
    """
    Estimate payload, dry mass, and inert mass from total vehicle mass.
    
    Uses statistical regression based on historical lunar lander data.
    Inert mass = Payload + Dry mass (excludes propellant only).
    
    Parameters
    ----------
    total_mass : float
        Total vehicle mass [kg]
    plot : bool, optional
        If True, displays regression plots
        
    Returns
    -------
    payload : float
        Estimated payload mass [kg]
    dry_mass : float
        Estimated dry mass (structure + systems) [kg]
    inert_mass : float
        Estimated inert mass (dry + payload) [kg]
        
    Examples
    --------
    >>> payload, dry, inert = estimate_masses_statistical(30000, plot=True)
    >>> print(f"Payload: {payload:.0f} kg, Dry: {dry:.0f} kg, Inert: {inert:.0f} kg")
    """
    payload = estimate_payload_from_total_mass(total_mass, plot=plot)
    dry_mass = estimate_dry_mass_from_total_mass(total_mass, plot=plot)
    inert_mass = payload + dry_mass
    
    return payload, dry_mass, inert_mass


def estimate_payload_requirements(
    n_crew: int = 4,
    mission_duration: int = 15,
    additional_payload_min: float = 500,
    additional_payload_max: float = 2000
) -> Tuple[float, float]:
    """
    Estimate minimum and maximum payload requirements based on crew and mission duration.
    
    Includes crew mass (person + suit), consumables, and additional equipment/cargo.
    
    Parameters
    ----------
    n_crew : int
        Number of crew members
    mission_duration : int
        Mission duration [days]
    additional_payload_min : float
        Minimum additional payload (equipment, cargo) [kg]
    additional_payload_max : float
        Maximum additional payload [kg]
        
    Returns
    -------
    payload_min : float
        Minimum payload mass [kg]
    payload_max : float
        Maximum payload mass [kg]
        
    Notes
    -----
    Consumables formula: 2.9*(1-0.7) + 1.83 + 0.82 + 1.22 = 4.74 kg/crew/day
    This accounts for:
    - Food (30% recycle): 2.9 * 0.3 = 0.87 kg/day
    - Water: 1.83 kg/day
    - Oxygen: 0.82 kg/day
    - Other: 1.22 kg/day
    
    Crew mass: 80 kg (person) + 42 kg (spacesuit) = 122 kg/crew
    
    Examples
    --------
    >>> payload_min, payload_max = estimate_payload_requirements(4, 15)
    >>> print(f"Payload range: {payload_min:.0f} - {payload_max:.0f} kg")
    """
    CREW_MASS_PER_PERSON = 122  # kg (80 body + 42 suit)
    CONSUMABLES_PER_CREW_DAY = 4.74  # kg/day (detailed breakdown in Notes)
    
    m_crew = n_crew * CREW_MASS_PER_PERSON
    m_consumables = n_crew * mission_duration * CONSUMABLES_PER_CREW_DAY
    
    payload_min = m_crew + m_consumables + additional_payload_min
    payload_max = m_crew + m_consumables + additional_payload_max
    
    return payload_min, payload_max


def calculate_mass_fractions(
    total_mass: float,
    inert_mass: float,
    propellant_mass: float
) -> dict:
    """
    Calculate mass fractions for the lunar lander.
    
    Parameters
    ----------
    total_mass : float
        Total vehicle mass [kg]
    inert_mass : float
        Inert mass (dry + payload) [kg]
    propellant_mass : float
        Propellant mass [kg]
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'mass_ratio': Total mass / Inert mass
        - 'propellant_fraction': Propellant mass / Total mass
        - 'inert_fraction': Inert mass / Total mass
    """
    mass_ratio = total_mass / inert_mass if inert_mass > 0 else 0
    propellant_fraction = propellant_mass / total_mass if total_mass > 0 else 0
    inert_fraction = inert_mass / total_mass if total_mass > 0 else 0
    
    return {
        'mass_ratio': mass_ratio,
        'propellant_fraction': propellant_fraction,
        'inert_fraction': inert_fraction
    }


# Example usage
if __name__ == "__main__":
    # Test with typical lunar lander mass
    test_mass = 30000  # kg
    
    print("=" * 60)
    print("LUNAR LANDER STATISTICAL MASS ESTIMATION")
    print("=" * 60)
    print(f"\nInput total mass: {test_mass:.0f} kg\n")
    
    # Estimate masses
    payload, dry_mass, inert_mass = estimate_masses_statistical(test_mass, plot=False)
    
    print(f"Statistical Estimates:")
    print(f"  Payload:     {payload:>8.0f} kg  ({100*payload/test_mass:>5.1f}%)")
    print(f"  Dry mass:    {dry_mass:>8.0f} kg  ({100*dry_mass/test_mass:>5.1f}%)")
    print(f"  Inert mass:  {inert_mass:>8.0f} kg  ({100*inert_mass/test_mass:>5.1f}%)")
    print(f"  Propellant:  {test_mass-inert_mass:>8.0f} kg  ({100*(test_mass-inert_mass)/test_mass:>5.1f}%)")
    
    # Payload requirements
    print(f"\nPayload Requirements (4 crew, 15 days):")
    payload_min, payload_max = estimate_payload_requirements(4, 15)
    print(f"  Minimum: {payload_min:>8.0f} kg")
    print(f"  Maximum: {payload_max:>8.0f} kg")
    
    print("\n" + "=" * 60)
