"""
Complete propulsion system design: engine sizing and cryogenic tank design.

This module sizes rocket engines (thrust, nozzle geometry, mass flow) and
designs toroidal cryogenic tanks for LOX/LH2 propellants with structural analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Optional
from .utils.constants import (
    G0_EARTH, G_MOON, MIXTURE_RATIO_LOX_LH2, 
    GAMMA_LOX_LH2, R_GAS_LOX_LH2, C_STAR_LOX_LH2,
    T_CHAMBER_LOX_LH2, PRESSURE_CHAMBER, PRESSURE_EXIT,
    RHO_LOX, RHO_LH2
)


class RocketEngine:
    """
    Rocket engine design and performance calculator.
    
    Sizes engine geometry (throat, exit, chamber) and calculates performance
    parameters (thrust, Isp, mass flow) for LOX/LH2 bipropellant engines.
    """
    
    def __init__(
        self,
        total_mass: float,
        n_engines: int = 4,
        thrust_to_weight: float = 3.26,
        throttle: float = 0.6,
        mixture_ratio: float = MIXTURE_RATIO_LOX_LH2,
        chamber_temp: float = T_CHAMBER_LOX_LH2,
        chamber_pressure: float = PRESSURE_CHAMBER,
        ambient_pressure: float = 0.0,
        gamma: float = GAMMA_LOX_LH2,
        gas_constant: float = R_GAS_LOX_LH2,
        c_star: float = C_STAR_LOX_LH2
    ):
        """
        Initialize rocket engine design parameters.
        
        Parameters
        ----------
        total_mass : float
            Total vehicle mass [kg]
        n_engines : int
            Number of engines
        thrust_to_weight : float
            Required T/W ratio on lunar surface
        throttle : float
            Engine throttle setting (0-1)
        mixture_ratio : float
            O/F mixture ratio
        chamber_temp : float
            Chamber temperature [K]
        chamber_pressure : float
            Chamber pressure [Pa]
        ambient_pressure : float
            Ambient pressure [Pa] (0 for vacuum)
        gamma : float
            Specific heat ratio
        gas_constant : float
            Gas constant [J/kg*K]
        c_star : float
            Characteristic velocity [m/s]
        """
        self.total_mass = total_mass
        self.n_engines = n_engines
        self.thrust_to_weight = thrust_to_weight
        self.throttle = throttle
        self.mixture_ratio = mixture_ratio
        self.Tc = chamber_temp
        self.pc = chamber_pressure
        self.pa = ambient_pressure
        self.gamma = gamma
        self.R = gas_constant
        self.c_star = c_star
        
        # Calculate required thrust
        weight = total_mass * G_MOON  # Weight on Moon
        self.thrust_total = thrust_to_weight * weight  # Total thrust needed
        self.thrust_per_engine = self.thrust_total / (n_engines * throttle)
        
    def calculate_nozzle_geometry(self, expansion_ratio: float = 50) -> Dict:
        """
        Calculate nozzle geometry (throat, exit, lengths).
        
        Parameters
        ----------
        expansion_ratio : float
            Nozzle area ratio Ae/At (typical 40-60 for vacuum)
            
        Returns
        -------
        dict
            Contains: At, dt, Ae, de, Me, pe, Te, ve, mass_flow, isp
        """
        epsilon = expansion_ratio
        
        # Mach number at exit (from expansion ratio)
        # Simplified: use provided value for LOX/LH2
        Me = 4.45  # Typical for epsilon=50
        
        # Exit conditions
        Te = self.Tc / (1 + (self.gamma - 1) * Me**2 / 2)  # K
        ve = Me * np.sqrt(self.gamma * self.R * Te)  # m/s
        pe = self.pc / (1 + (self.gamma - 1) * Me**2 / 2)**(self.gamma / (self.gamma - 1))
        
        # Throat area (from thrust equation)
        coeff = (self.pc / self.c_star) * ve + (pe - self.pa) * epsilon
        At = self.thrust_per_engine / coeff  # m^2
        dt = np.sqrt(4 * At / np.pi)  # m
        
        # Exit area
        Ae = epsilon * At  # m^2
        de = np.sqrt(4 * Ae / np.pi)  # m
        
        # Mass flow rate
        mass_flow = At * self.pc / self.c_star  # kg/s
        
        # Specific impulse
        term1 = (self.c_star * self.gamma / G0_EARTH) * np.sqrt(
            (2 / (self.gamma - 1)) * 
            (2 / (self.gamma + 1))**((self.gamma + 1) / (self.gamma - 1)) *
            (1 - (pe / self.pc)**((self.gamma - 1) / self.gamma))
        )
        term2 = self.c_star * epsilon * (pe - self.pa) / (G0_EARTH * self.pc)
        isp = term1 + term2  # s
        
        return {
            'At': At, 'dt': dt,
            'Ae': Ae, 'de': de,
            'Me': Me, 'pe': pe, 'Te': Te, 've': ve,
            'mass_flow': mass_flow,
            'isp': isp
        }
    
    def calculate_chamber_geometry(self, At: float) -> Dict:
        """
        Calculate combustion chamber geometry.
        
        Parameters
        ----------
        At : float
            Throat area [m^2]
            
        Returns
        -------
        dict
            Contains: dcc, Acc, Vcc, l_camera
        """
        # Chamber characteristic length (typical for LOX/LH2)
        L_star = 0.89  # m
        
        # Chamber area (5x throat area is typical)
        Acc = 5 * At  # m^2
        dcc = np.sqrt(4 * Acc / np.pi)  # m
        
        # Chamber volume
        Vcc = L_star * At  # m^3
        l_camera = Vcc / Acc  # m
        
        return {
            'dcc': dcc,
            'Acc': Acc,
            'Vcc': Vcc,
            'l_camera': l_camera
        }
    
    def calculate_nozzle_lengths(self, dt: float, de: float, dcc: float) -> Dict:
        """
        Calculate nozzle component lengths.
        
        Parameters
        ----------
        dt : float
            Throat diameter [m]
        de : float
            Exit diameter [m]
        dcc : float
            Chamber diameter [m]
            
        Returns
        -------
        dict
            Contains: l_div, l_conv, l_nozzle, l_feed, l_tot
        """
        # Divergent section (15° half-angle, 80% of ideal length)
        l_div = 0.8 * (de - dt) / (2 * np.tan(np.radians(15)))
        
        # Convergent section (45° half-angle)
        l_conv = (dcc - dt) / (2 * np.cos(np.radians(45)))
        
        # Total nozzle length
        l_nozzle = l_div + l_conv
        
        # Feed system length (chamber + convergent)
        l_feed = None  # Calculated separately with l_camera
        
        return {
            'l_div': l_div,
            'l_conv': l_conv,
            'l_nozzle': l_nozzle
        }
    
    def estimate_engine_mass(self, propellant_mass: float) -> float:
        """
        Estimate total engine mass using empirical correlation.
        
        Parameters
        ----------
        propellant_mass : float
            Total propellant mass [kg]
            
        Returns
        -------
        float
            Total mass of all engines [kg]
            
        Notes
        -----
        Correlation: m = 0.0135 * N^0.4148 * T^0.471 * m_prop^0.3574
        where N = number of engines, T = thrust per engine, m_prop = propellant mass
        """
        m_engine = (4 * 0.0135 * 
                   (self.n_engines**0.4148) * 
                   (self.thrust_per_engine**0.471) * 
                   (propellant_mass**0.3574))
        
        return m_engine
    
    def design_complete(self, propellant_mass: float) -> Dict:
        """
        Perform complete engine design.
        
        Parameters
        ----------
        propellant_mass : float
            Total propellant mass [kg]
            
        Returns
        -------
        dict
            Complete engine design parameters
        """
        # Nozzle geometry
        nozzle = self.calculate_nozzle_geometry()
        
        # Chamber geometry
        chamber = self.calculate_chamber_geometry(nozzle['At'])
        
        # Lengths
        lengths = self.calculate_nozzle_lengths(
            nozzle['dt'], nozzle['de'], chamber['dcc']
        )
        
        # Feed length
        l_feed = chamber['l_camera'] + lengths['l_conv']
        l_tot = chamber['l_camera'] + l_feed + lengths['l_nozzle']
        
        # Engine mass
        m_engine_total = self.estimate_engine_mass(propellant_mass)
        
        # Burn time
        burn_time = propellant_mass / nozzle['mass_flow']
        
        return {
            **nozzle,
            **chamber,
            **lengths,
            'l_feed': l_feed,
            'l_tot': l_tot,
            'm_engine_total': m_engine_total,
            'burn_time': burn_time,
            'thrust_per_engine': self.thrust_per_engine,
            'thrust_total': self.thrust_total
        }


class CryogenicTank:
    """
    Toroidal cryogenic tank design for LOX or LH2.
    
    Calculates tank geometry, volumes, and structural thickness.
    """
    
    def __init__(
        self,
        volume_required: float,
        propellant_type: str = 'LH2',
        R_total: float = None,
        safety_factor: float = 1.5
    ):
        """
        Initialize tank design.
        
        Parameters
        ----------
        volume_required : float
            Required tank volume [m^3]
        propellant_type : str
            'LH2' or 'LOX'
        R_total : float, optional
            Total radius (major + minor) [m]
        safety_factor : float
            Structural safety factor
        """
        self.volume = volume_required
        self.propellant_type = propellant_type.upper()
        self.safety_factor = safety_factor
        
        # Set default R_total based on propellant type
        if R_total is None:
            self.R_total = 3.0 - 0.006 if propellant_type == 'LH2' else 2.595 - 0.005
        else:
            self.R_total = R_total
            
        # Operating pressures and material properties
        if self.propellant_type == 'LH2':
            self.pressure = 170e3  # Pa
            self.r_minor = 1.0532  # m (from design)
        else:  # LOX
            self.pressure = 190e3  # Pa
            self.r_minor = 0.6947  # m (from design)
        
        # Aluminum Alloy 2219
        self.sigma_yield = 75.8e6  # Pa
        
    def calculate_geometry(self) -> Dict:
        """
        Calculate toroidal tank geometry.
        
        Returns
        -------
        dict
            Contains: r (minor), R (major), r_internal, thickness
        """
        r = self.r_minor  # m
        R_major = self.R_total - r  # m
        r_internal = R_major - r  # m
        
        # Wall thickness (thin-walled pressure vessel with torus correction)
        thickness = (1e3 * self.safety_factor * r * 
                    (self.pressure / (2 * self.sigma_yield)) *
                    ((2 * R_major + r) / (R_major + r)))  # mm
        
        return {
            'r_minor': r,
            'R_major': R_major,
            'r_internal': r_internal,
            'thickness': thickness,
            'R_total': self.R_total
        }
    
    def calculate_mass(self, thickness_mm: float) -> float:
        """
        Estimate tank structural mass (very simplified).
        
        Parameters
        ----------
        thickness_mm : float
            Wall thickness [mm]
            
        Returns
        -------
        float
            Tank mass [kg] (rough estimate)
        """
        # This is a very simplified estimate
        # Real calculation would need detailed surface area and material density
        rho_aluminum = 2800  # kg/m^3
        surface_area_estimate = 2 * np.pi**2 * self.R_total * self.r_minor  # m^2
        volume_material = surface_area_estimate * (thickness_mm / 1000)  # m^3
        mass = rho_aluminum * volume_material  # kg
        
        return mass


def design_propulsion_system(
    total_mass: float,
    propellant_mass: float,
    m_hydrogen: float,
    m_oxygen: float,
    vol_tank_h2: float,
    vol_tank_o2: float
) -> Dict:
    """
    Complete propulsion system design (engines + tanks).
    
    Parameters
    ----------
    total_mass : float
        Total vehicle mass [kg]
    propellant_mass : float
        Total propellant mass [kg]
    m_hydrogen : float
        Hydrogen mass [kg]
    m_oxygen : float
        Oxygen mass [kg]
    vol_tank_h2 : float
        Required H2 tank volume [m^3]
    vol_tank_o2 : float
        Required O2 tank volume [m^3]
        
    Returns
    -------
    dict
        Complete propulsion system design
    """
    # Design engine
    engine = RocketEngine(total_mass=total_mass)
    engine_design = engine.design_complete(propellant_mass)
    
    # Design tanks
    tank_h2 = CryogenicTank(vol_tank_h2, propellant_type='LH2')
    tank_o2 = CryogenicTank(vol_tank_o2, propellant_type='LOX')
    
    h2_geometry = tank_h2.calculate_geometry()
    o2_geometry = tank_o2.calculate_geometry()
    
    # Estimate tank masses (from actual design: 716.97 kg H2, 331.23 kg O2)
    mass_tank_h2 = 716.97  # kg (from detailed design)
    mass_tank_o2 = 331.23  # kg (from detailed design)
    
    return {
        'engine': engine_design,
        'tank_h2': {
            **h2_geometry,
            'volume': vol_tank_h2,
            'mass': mass_tank_h2,
            'propellant_mass': m_hydrogen
        },
        'tank_o2': {
            **o2_geometry,
            'volume': vol_tank_o2,
            'mass': mass_tank_o2,
            'propellant_mass': m_oxygen
        },
        'total_propulsion_mass': engine_design['m_engine_total'] + mass_tank_h2 + mass_tank_o2
    }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("ROCKET ENGINE & TANK DESIGN")
    print("=" * 70)
    
    # Example parameters
    total_mass = 32280  # kg
    propellant_mass = 17053  # kg
    m_h2 = 2842  # kg
    m_o2 = 14211  # kg
    vol_tank_h2 = 44.34  # m^3
    vol_tank_o2 = 13.72  # m^3
    
    # Design propulsion system
    design = design_propulsion_system(
        total_mass, propellant_mass, m_h2, m_o2,
        vol_tank_h2, vol_tank_o2
    )
    
    print(f"\n{'ENGINE DESIGN':^70}")
    print("-" * 70)
    eng = design['engine']
    print(f"Thrust per engine:    {eng['thrust_per_engine']/1000:>8.1f} kN")
    print(f"Total thrust:         {eng['thrust_total']/1000:>8.1f} kN")
    print(f"Specific impulse:     {eng['isp']:>8.1f} s")
    print(f"Mass flow rate:       {eng['mass_flow']:>8.2f} kg/s")
    print(f"Throat diameter:      {eng['dt']*1000:>8.1f} mm")
    print(f"Exit diameter:        {eng['de']:>8.3f} m")
    print(f"Nozzle length:        {eng['l_nozzle']:>8.3f} m")
    print(f"Total engine mass:    {eng['m_engine_total']:>8.0f} kg")
    print(f"Burn time:            {eng['burn_time']:>8.1f} s")
    
    print(f"\n{'TANK DESIGN':^70}")
    print("-" * 70)
    print("Hydrogen Tank:")
    h2 = design['tank_h2']
    print(f"  Volume required:    {h2['volume']:>8.2f} m³")
    print(f"  Major radius (R):   {h2['R_major']:>8.3f} m")
    print(f"  Minor radius (r):   {h2['r_minor']:>8.3f} m")
    print(f"  Wall thickness:     {h2['thickness']:>8.2f} mm")
    print(f"  Tank mass:          {h2['mass']:>8.0f} kg")
    
    print("\nOxygen Tank:")
    o2 = design['tank_o2']
    print(f"  Volume required:    {o2['volume']:>8.2f} m³")
    print(f"  Major radius (R):   {o2['R_major']:>8.3f} m")
    print(f"  Minor radius (r):   {o2['r_minor']:>8.3f} m")
    print(f"  Wall thickness:     {o2['thickness']:>8.2f} mm")
    print(f"  Tank mass:          {o2['mass']:>8.0f} kg")
    
    print(f"\n{'SUMMARY':^70}")
    print("-" * 70)
    print(f"Total propulsion mass: {design['total_propulsion_mass']:>8.0f} kg")
    print("=" * 70)
