"""
Electrical Power System (EPS) sizing for lunar lander.

This module sizes solar arrays, fuel cells, and batteries for the lander's
electrical power requirements during different mission phases.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict


class ElectricalPowerSystem:
    """
    EPS design for lunar lander with solar arrays and fuel cells.
    
    Accounts for eclipse and daylight power requirements, transmission
    efficiency, degradation, and provides mass/area estimates.
    """
    
    def __init__(
        self,
        power_eclipse: float = 4000,
        power_daylight: float = 4700,
        duration_daylight_hours: float = 75,
        duration_eclipse_minutes: float = 26,
        efficiency_eclipse: float = 0.65,
        efficiency_daylight: float = 0.85,
        solar_cell_efficiency: float = 0.30,
        solar_constant: float = 1367,
        initial_degradation: float = 0.90,
        life_degradation: float = 0.97,
        incidence_angle_deg: float = 23,
        specific_performance: float = 38
    ):
        """
        Initialize EPS design parameters.
        
        Parameters
        ----------
        power_eclipse : float
            Power required during eclipse [W]
        power_daylight : float
            Power required during daylight [W]
        duration_daylight_hours : float
            Daylight duration [hours]
        duration_eclipse_minutes : float
            Eclipse duration [minutes]
        efficiency_eclipse : float
            Transmission efficiency during eclipse
        efficiency_daylight : float
            Transmission efficiency during daylight
        solar_cell_efficiency : float
            Solar cell efficiency (GaAs cells ~0.30)
        solar_constant : float
            Solar irradiance [W/m^2]
        initial_degradation : float
            Initial degradation factor
        life_degradation : float
            End-of-life degradation factor
        incidence_angle_deg : float
            Solar incidence angle [degrees]
        specific_performance : float
            Solar array specific performance [W/kg]
        """
        self.Pe = power_eclipse
        self.Pd = power_daylight
        self.Td = duration_daylight_hours * 3600  # Convert to seconds
        self.Te = duration_eclipse_minutes * 60   # Convert to seconds
        self.Xe = efficiency_eclipse
        self.Xd = efficiency_daylight
        self.eta = solar_cell_efficiency
        self.PI = solar_constant
        self.Id = initial_degradation
        self.Ld = life_degradation
        self.theta = np.radians(incidence_angle_deg)
        self.spec_perf = specific_performance
        
    def calculate_solar_array(self) -> Dict:
        """
        Calculate solar array area and mass.
        
        Returns
        -------
        dict
            Contains: Psa (power capability), A_SA (area), M_SA (mass),
                     P_BOL, P_EOL
        
        Notes
        -----
        Power capability formula accounts for both eclipse and daylight phases:
        Psa = (Pe*Te/Xe + Pd*Td/Xd) / Td
        
        End-of-life power: P_EOL = PI * eta * Id * cos(theta) * Ld
        """
        # Power capability at load input [W]
        Psa = ((self.Pe * self.Te / self.Xe) + 
               (self.Pd * self.Td / self.Xd)) / self.Td
        
        # Power capability produced (before cell efficiency)
        Po = self.PI * self.eta  # W/m^2
        
        # Beginning of life (BOL) power
        P_BOL = Po * self.Id * np.cos(self.theta)  # W/m^2
        
        # End of life (EOL) power
        P_EOL = P_BOL * self.Ld  # W/m^2
        
        # Required solar array area
        A_SA = Psa / P_EOL  # m^2
        
        # Solar array mass
        M_SA = Psa / self.spec_perf  # kg
        
        return {
            'Psa': Psa,
            'Po': Po,
            'P_BOL': P_BOL,
            'P_EOL': P_EOL,
            'A_SA': A_SA,
            'M_SA': M_SA
        }
    
    def calculate_fuel_cells(
        self,
        power_available: float = 5000,
        energy_density: float = 780,
        time_use_hours: float = 5.5,
        efficiency: float = 0.8
    ) -> Dict:
        """
        Calculate fuel cell system mass.
        
        Parameters
        ----------
        power_available : float
            Available fuel cell power [W]
        energy_density : float
            Fuel cell energy density [W*h/kg]
        time_use_hours : float
            Expected usage time [hours]
        efficiency : float
            Fuel cell efficiency
            
        Returns
        -------
        dict
            Contains: mass_fuel_cells, mass_water, power_density
            
        Notes
        -----
        Water mass is estimated as 90% of fuel cell mass (from reaction products).
        """
        # Power density [W/kg]
        power_density = (energy_density / time_use_hours) * efficiency
        
        # Fuel cell mass
        mass_fuel_cells = power_available / power_density  # kg
        
        # Water mass (product of H2 + O2 reaction)
        mass_water = mass_fuel_cells * 0.9  # kg
        
        return {
            'power_available': power_available,
            'power_density': power_density,
            'mass_fuel_cells': mass_fuel_cells,
            'mass_water': mass_water
        }
    
    def design_complete_system(self) -> Dict:
        """
        Complete EPS design with solar arrays and fuel cells.
        
        Returns
        -------
        dict
            Complete EPS design parameters and total mass
        """
        # Solar array design
        solar = self.calculate_solar_array()
        
        # Fuel cell design
        fuel_cells = self.calculate_fuel_cells()
        
        # Total EPS mass
        total_mass = (solar['M_SA'] + 
                     fuel_cells['mass_fuel_cells'] + 
                     fuel_cells['mass_water'])
        
        return {
            'solar_array': solar,
            'fuel_cells': fuel_cells,
            'total_mass': total_mass
        }
    
    def plot_power_profile(self):
        """
        Plot power generation and consumption profile.
        """
        # Time arrays
        t_daylight = np.linspace(0, self.Td / 3600, 100)  # hours
        t_eclipse_start = self.Td / 3600
        t_eclipse = np.linspace(t_eclipse_start, 
                               t_eclipse_start + self.Te / 3600, 50)
        
        # Power arrays
        p_daylight = np.ones_like(t_daylight) * self.Pd
        p_eclipse = np.ones_like(t_eclipse) * self.Pe
        
        # Combine
        t_total = np.concatenate([t_daylight, t_eclipse])
        p_total = np.concatenate([p_daylight, p_eclipse])
        
        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(t_total, p_total, 'b-', linewidth=2, label='Power Required')
        plt.axvspan(t_eclipse_start, t_eclipse_start + self.Te / 3600, 
                   alpha=0.3, color='gray', label='Eclipse Period')
        plt.xlabel('Mission Time [hours]', fontsize=12)
        plt.ylabel('Power [W]', fontsize=12)
        plt.title('Lunar Lander Power Profile', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


def design_eps(
    power_eclipse: float = 4000,
    power_daylight: float = 4700
) -> Tuple[float, float, float, float, float]:
    """
    Simplified EPS design function (compatible with original MATLAB).
    
    Parameters
    ----------
    power_eclipse : float
        Power required during eclipse [W]
    power_daylight : float
        Power required during daylight [W]
        
    Returns
    -------
    A_SA : float
        Solar array area [m^2]
    M_SA : float
        Solar array mass [kg]
    mass_water : float
        Water mass from fuel cells [kg]
    EPS_mass : float
        Total EPS mass [kg]
    Psa : float
        Solar array power capability [W]
    """
    eps = ElectricalPowerSystem(power_eclipse=power_eclipse, 
                                power_daylight=power_daylight)
    design = eps.design_complete_system()
    
    return (
        design['solar_array']['A_SA'],
        design['solar_array']['M_SA'],
        design['fuel_cells']['mass_water'],
        design['total_mass'],
        design['solar_array']['Psa']
    )


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("ELECTRICAL POWER SYSTEM (EPS) DESIGN")
    print("=" * 70)
    
    # Initialize EPS
    eps = ElectricalPowerSystem(power_eclipse=4000, power_daylight=4700)
    
    # Complete design
    design = eps.design_complete_system()
    
    print(f"\n{'SOLAR ARRAY DESIGN':^70}")
    print("-" * 70)
    sa = design['solar_array']
    print(f"Power capability (Psa):  {sa['Psa']:>8.1f} W")
    print(f"BOL power density:       {sa['P_BOL']:>8.1f} W/m²")
    print(f"EOL power density:       {sa['P_EOL']:>8.1f} W/m²")
    print(f"Required area:           {sa['A_SA']:>8.2f} m²")
    print(f"Solar array mass:        {sa['M_SA']:>8.1f} kg")
    
    print(f"\n{'FUEL CELL SYSTEM':^70}")
    print("-" * 70)
    fc = design['fuel_cells']
    print(f"Available power:         {fc['power_available']:>8.0f} W")
    print(f"Power density:           {fc['power_density']:>8.1f} W/kg")
    print(f"Fuel cell mass:          {fc['mass_fuel_cells']:>8.1f} kg")
    print(f"Water mass (product):    {fc['mass_water']:>8.1f} kg")
    
    print(f"\n{'TOTAL EPS MASS':^70}")
    print("-" * 70)
    print(f"Total mass:              {design['total_mass']:>8.1f} kg")
    
    print("\n" + "=" * 70)
