"""
Thermal Control System (TCS) sizing for lunar lander.

Calculates thermal protection system mass, radiator area, and power requirements
for temperature control during lunar surface operations.
"""

import numpy as np
from typing import Tuple, Dict


def size_thermal_control_system(
    width: float = 5.0,
    height: float = 3.5,
    frontal_area_propulsion: float = 28.0,
    habitable_area: float = 66.63,
    heat_load: float = 4500,
    lox_tank_area: float = 51.65,
    lh2_tank_area: float = 86.55,
    propulsion_lateral_area: float = 85.76
) -> Tuple[float, float, float]:
    """
    Size the thermal control system for the lunar lander.
    
    Parameters
    ----------
    width : float
        Lander diameter [m]
    height : float
        Lander height [m]
    frontal_area_propulsion : float
        Frontal area of propulsion section [m^2]
    habitable_area : float
        Surface area of habitable section [m^2]
    heat_load : float
        Total heat load from power systems [W]
    lox_tank_area : float
        LOX tank surface area [m^2]
    lh2_tank_area : float
        LH2 tank surface area [m^2]
    propulsion_lateral_area : float
        Lateral area of propulsion section [m^2]
        
    Returns
    -------
    tps_mass : float
        Thermal Protection System mass [kg]
    tps_volume : float
        TPS volume [m^3]
    tcs_power : float
        TCS active cooling power requirement [W]
        
    Notes
    -----
    TCS consists of:
    - Multi-Layer Insulation (MLI) for cryogenic tanks
    - Radiators for heat rejection
    - Active thermal control (heaters, pumps)
    - Phase Change Materials (PCM) for thermal buffering
    
    This is a simplified model. Complete TCS design requires detailed
    thermal modeling with ESATAN or similar tools.
    """
    # Total surface area requiring thermal control
    total_area = (habitable_area + frontal_area_propulsion + 
                 lox_tank_area + lh2_tank_area + propulsion_lateral_area)
    
    # MLI mass estimation (typical 0.5-1.0 kg/m^2)
    mli_specific_mass = 0.7  # kg/m^2
    mli_mass = total_area * mli_specific_mass
    
    # Radiator sizing
    # Assumes radiators reject ~50% of heat load
    stefan_boltzmann = 5.67e-8  # W/m^2/K^4
    radiator_temp = 300  # K (typical operating temp)
    sink_temp = 100  # K (lunar environment average)
    radiator_emissivity = 0.85
    
    heat_rejection_capacity = (stefan_boltzmann * radiator_emissivity * 
                              (radiator_temp**4 - sink_temp**4))
    
    radiator_area_required = (heat_load * 0.5) / heat_rejection_capacity  # m^2
    radiator_specific_mass = 5.0  # kg/m^2 (typical for space radiators)
    radiator_mass = radiator_area_required * radiator_specific_mass
    
    # Active cooling system (pumps, heat pipes, heaters)
    active_cooling_mass = 150  # kg (estimated)
    
    # Total TPS mass
    tps_mass = mli_mass + radiator_mass + active_cooling_mass
    
    # TPS volume (very approximate)
    mli_thickness = 0.03  # m (30 mm typical)
    tps_volume = total_area * mli_thickness
    
    # TCS power requirement (pumps + heaters + control)
    pump_power = 200  # W
    heater_power = 500  # W
    control_power = 50  # W
    tcs_power = pump_power + heater_power + control_power
    
    return tps_mass, tps_volume, tcs_power


class ThermalControlSystem:
    """
    Detailed thermal control system design.
    """
    
    def __init__(
        self,
        heat_load: float = 4500,
        habitable_area: float = 66.63,
        tank_areas: Dict[str, float] = None
    ):
        """
        Initialize TCS design.
        
        Parameters
        ----------
        heat_load : float
            Internal heat load [W]
        habitable_area : float
            Habitable section area [m^2]
        tank_areas : dict
            Dictionary with 'lox' and 'lh2' tank areas [m^2]
        """
        self.heat_load = heat_load
        self.habitable_area = habitable_area
        
        if tank_areas is None:
            self.tank_areas = {'lox': 51.65, 'lh2': 86.55}
        else:
            self.tank_areas = tank_areas
    
    def calculate_mli_requirements(self) -> Dict:
        """
        Calculate Multi-Layer Insulation requirements.
        
        Returns
        -------
        dict
            MLI mass, layers, area
        """
        total_area = self.habitable_area + sum(self.tank_areas.values())
        
        # MLI properties
        layers = 20  # Typical for cryogenic applications
        mass_per_layer = 0.035  # kg/m^2 per layer
        total_mli_mass = total_area * layers * mass_per_layer
        
        return {
            'area': total_area,
            'layers': layers,
            'mass': total_mli_mass
        }
    
    def calculate_radiator_requirements(self) -> Dict:
        """
        Calculate radiator requirements for heat rejection.
        
        Returns
        -------
        dict
            Radiator area, mass, heat rejection capacity
        """
        # Radiator design parameters
        T_radiator = 300  # K
        T_sink = 100  # K (lunar environment)
        emissivity = 0.85
        stefan_boltzmann = 5.67e-8  # W/m^2/K^4
        
        # Heat rejection capacity per unit area
        q_radiator = (emissivity * stefan_boltzmann * 
                     (T_radiator**4 - T_sink**4))
        
        # Required area (reject 50% of heat load via radiators)
        area_required = (self.heat_load * 0.5) / q_radiator
        
        # Radiator mass (typical 5-7 kg/m^2)
        specific_mass = 6.0  # kg/m^2
        mass = area_required * specific_mass
        
        return {
            'area': area_required,
            'mass': mass,
            'heat_rejection_capacity': q_radiator * area_required
        }
    
    def calculate_active_cooling(self) -> Dict:
        """
        Calculate active cooling system requirements.
        
        Returns
        -------
        dict
            Pump power, heater power, total power, mass
        """
        # Active cooling components
        pump_power = 200  # W
        heater_power = 500  # W (for cold case)
        control_power = 50  # W
        
        total_power = pump_power + heater_power + control_power
        
        # System mass (pumps, heat pipes, controllers, heaters)
        system_mass = 150  # kg
        
        return {
            'pump_power': pump_power,
            'heater_power': heater_power,
            'control_power': control_power,
            'total_power': total_power,
            'mass': system_mass
        }
    
    def design_complete(self) -> Dict:
        """
        Complete TCS design.
        
        Returns
        -------
        dict
            Complete TCS design parameters
        """
        mli = self.calculate_mli_requirements()
        radiator = self.calculate_radiator_requirements()
        active = self.calculate_active_cooling()
        
        total_mass = mli['mass'] + radiator['mass'] + active['mass']
        
        return {
            'mli': mli,
            'radiator': radiator,
            'active_cooling': active,
            'total_mass': total_mass,
            'total_power': active['total_power']
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("THERMAL CONTROL SYSTEM (TCS) DESIGN")
    print("=" * 70)
    
    # Simple sizing
    tps_mass, tps_volume, tcs_power = size_thermal_control_system()
    
    print(f"\nSimplified TCS Sizing:")
    print(f"  TPS mass:      {tps_mass:>8.1f} kg")
    print(f"  TPS volume:    {tps_volume:>8.2f} m³")
    print(f"  TCS power:     {tcs_power:>8.0f} W")
    
    # Detailed design
    print(f"\n{'DETAILED TCS DESIGN':^70}")
    print("-" * 70)
    
    tcs = ThermalControlSystem(heat_load=4500)
    design = tcs.design_complete()
    
    print(f"\nMulti-Layer Insulation:")
    print(f"  Area:          {design['mli']['area']:>8.1f} m²")
    print(f"  Layers:        {design['mli']['layers']:>8.0f}")
    print(f"  Mass:          {design['mli']['mass']:>8.1f} kg")
    
    print(f"\nRadiators:")
    print(f"  Area:          {design['radiator']['area']:>8.1f} m²")
    print(f"  Mass:          {design['radiator']['mass']:>8.1f} kg")
    print(f"  Heat rejection: {design['radiator']['heat_rejection_capacity']:>7.0f} W")
    
    print(f"\nActive Cooling:")
    print(f"  Pump power:    {design['active_cooling']['pump_power']:>8.0f} W")
    print(f"  Heater power:  {design['active_cooling']['heater_power']:>8.0f} W")
    print(f"  System mass:   {design['active_cooling']['mass']:>8.0f} kg")
    
    print(f"\n{'TOTALS':^70}")
    print("-" * 70)
    print(f"Total TCS mass:  {design['total_mass']:>8.1f} kg")
    print(f"Total TCS power: {design['total_power']:>8.0f} W")
    
    print("\n" + "=" * 70)
