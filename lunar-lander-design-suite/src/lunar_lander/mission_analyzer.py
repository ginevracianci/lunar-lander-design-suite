"""
Main mission analyzer for iterative lunar lander design.

This module implements the iterative mass closure loop that sizes all subsystems
and converges to a consistent vehicle design.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Optional
import warnings

from .mass_estimation import (
    estimate_masses_statistical,
    estimate_payload_requirements
)
from .propellant_system import estimate_propellant_lunar_mission
from .propulsion_system import design_propulsion_system
from .subsystems.eps import design_eps
from .subsystems.tcs import size_thermal_control_system
from .utils.constants import (
    G0_EARTH, DELTA_V_LLO_TO_SURFACE, DELTA_V_SURFACE_TO_LLO,
    SAFETY_MARGIN, MIXTURE_RATIO_LOX_LH2,
    ECLSS_MASS_BASELINE, ECLSS_VOLUME_BASELINE, ECLSS_POWER_BASELINE,
    AVIONICS_MASS_BASELINE, AVIONICS_VOLUME_BASELINE, AVIONICS_POWER_BASELINE
)


class LunarLanderDesigner:
    """
    Complete lunar lander design with iterative mass closure.
    
    Implements the concurrent engineering approach used in the original MATLAB code,
    iterating through all subsystems until mass convergence is achieved.
    """
    
    def __init__(
        self,
        initial_total_mass: float = 30000,
        n_crew: int = 4,
        mission_duration: int = 15,
        delta_v_descent: float = None,
        delta_v_ascent: float = None,
        isp: float = 438.3,
        payload_override: float = None
    ):
        """
        Initialize lunar lander design parameters.
        
        Parameters
        ----------
        initial_total_mass : float
            Initial guess for total vehicle mass [kg]
        n_crew : int
            Number of crew members
        mission_duration : int
            Mission duration on lunar surface [days]
        delta_v_descent : float, optional
            Delta-V for descent [m/s] (default: 1905 * 1.05)
        delta_v_ascent : float, optional
            Delta-V for ascent [m/s] (default: 1963 * 1.05)
        isp : float
            Specific impulse [s] (default: RL10B-2 engine)
        payload_override : float, optional
            Fixed payload mass [kg], overrides statistical estimate
        """
        self.initial_total_mass = initial_total_mass
        self.n_crew = n_crew
        self.mission_duration = mission_duration
        self.isp = isp
        self.payload_override = payload_override
        
        # Delta-V with safety margins
        if delta_v_descent is None:
            self.delta_v_descent = DELTA_V_LLO_TO_SURFACE * SAFETY_MARGIN
        else:
            self.delta_v_descent = delta_v_descent
            
        if delta_v_ascent is None:
            self.delta_v_ascent = DELTA_V_SURFACE_TO_LLO * SAFETY_MARGIN
        else:
            self.delta_v_ascent = delta_v_ascent
        
        # Storage for iteration history
        self.history = {
            'iteration': [],
            'total_mass': [],
            'payload': [],
            'dry_mass': [],
            'inert_mass': [],
            'propellant_mass': [],
            'structure_mass': [],
            'subsystems_mass': []
        }
        
        # Final design results
        self.results = None
        
    def estimate_structure_and_landing_gear(
        self,
        dry_mass: float,
        inert_mass: float
    ) -> Tuple[float, float]:
        """
        Estimate structure and landing gear mass using statistical correlations.
        
        Parameters
        ----------
        dry_mass : float
            Dry mass (without propellant) [kg]
        inert_mass : float
            Inert mass (dry + payload) [kg]
            
        Returns
        -------
        structure_mass : float
            Structure + TPS mass [kg]
        landing_gear_mass : float
            Landing gear mass [kg]
            
        Notes
        -----
        Uses Merill correlation: m = 1.325*(m_dry/1000)^2.863 + 5.651e-5*(m_inert/1000)^5.269 + 1390
        Landing gear: 8% of dry mass
        """
        # Structure + TPS (Merill correlation)
        structure_tps_mass = (1.325 * (dry_mass / 1000)**2.863 + 
                             5.651e-5 * (inert_mass / 1000)**5.269 + 
                             1390)
        
        # Landing gear (8% of dry mass)
        landing_gear_mass = 0.08 * dry_mass
        
        return structure_tps_mass, landing_gear_mass
    
    def calculate_subsystems(self) -> Dict:
        """
        Calculate all subsystem masses, volumes, and power.
        
        Returns
        -------
        dict
            Subsystem parameters (masses, volumes, powers)
        """
        # Avionics (GNC, Communication, CDH)
        avionics = {
            'mass': AVIONICS_MASS_BASELINE,
            'volume': AVIONICS_VOLUME_BASELINE,
            'power': AVIONICS_POWER_BASELINE
        }
        
        # ECLSS (Environmental Control & Life Support)
        eclss = {
            'mass': ECLSS_MASS_BASELINE,
            'volume': ECLSS_VOLUME_BASELINE,
            'power': ECLSS_POWER_BASELINE
        }
        
        # EPS (Electrical Power System)
        A_SA, M_SA, mass_water, EPS_mass, Psa = design_eps(
            power_eclipse=4000,
            power_daylight=4700
        )
        eps = {
            'mass': EPS_mass,
            'solar_array_area': A_SA,
            'solar_array_mass': M_SA,
            'power_capability': Psa
        }
        
        # TCS (Thermal Control System)
        TCS_mass, TCS_volume, TCS_power = size_thermal_control_system()
        tcs = {
            'mass': TCS_mass,
            'volume': TCS_volume,
            'power': TCS_power
        }
        
        return {
            'avionics': avionics,
            'eclss': eclss,
            'eps': eps,
            'tcs': tcs
        }
    
    def iterate_design(
        self,
        max_iterations: int = 20,
        tolerance: float = 10.0,
        verbose: bool = True
    ) -> Dict:
        """
        Perform iterative mass closure to converge on final design.
        
        Parameters
        ----------
        max_iterations : int
            Maximum number of iterations
        tolerance : float
            Convergence tolerance [kg] for total mass change
        verbose : bool
            Print iteration progress
            
        Returns
        -------
        dict
            Final converged design
            
        Notes
        -----
        Iteration loop:
        1. Estimate payload, dry mass from total mass (statistical)
        2. Calculate propellant needed (Tsiolkovsky)
        3. Size propulsion system (engines + tanks)
        4. Size subsystems (AOCS, EPS, TCS, ECLSS)
        5. Calculate structure + landing gear
        6. Update dry mass = sum of all components
        7. Update inert mass = dry + payload
        8. Calculate new total mass = inert + propellant
        9. Check convergence
        10. Repeat
        """
        # Initialize
        total_mass = self.initial_total_mass
        converged = False
        
        if verbose:
            print("=" * 80)
            print("LUNAR LANDER ITERATIVE DESIGN")
            print("=" * 80)
            print(f"Initial mass:    {total_mass:.0f} kg")
            print(f"Crew:            {self.n_crew}")
            print(f"Mission:         {self.mission_duration} days")
            print(f"ΔV descent:      {self.delta_v_descent:.0f} m/s")
            print(f"ΔV ascent:       {self.delta_v_ascent:.0f} m/s")
            print(f"Isp:             {self.isp:.1f} s")
            print("\n" + "-" * 80)
            print(f"{'Iter':<6} {'Total':>10} {'Payload':>10} {'Dry':>10} {'Propel':>10} {'Change':>10}")
            print("-" * 80)
        
        for iteration in range(max_iterations):
            # 1. Statistical mass estimation
            payload, dry_mass_stat, inert_mass_stat = estimate_masses_statistical(total_mass)
            
            # Override payload if specified
            if self.payload_override is not None:
                payload = self.payload_override
            
            # Use statistical dry mass as initial inert mass (will be updated)
            inert_mass = inert_mass_stat
            
            # 2. Calculate propellant requirements
            m_h2, m_o2, v_h2, v_o2, vt_h2, vt_o2 = estimate_propellant_lunar_mission(
                inert_mass=inert_mass,
                delta_v_descent=self.delta_v_descent,
                delta_v_ascent=self.delta_v_ascent,
                isp=self.isp
            )
            propellant_mass = m_h2 + m_o2
            
            # 3. Size propulsion system
            propulsion = design_propulsion_system(
                total_mass=total_mass,
                propellant_mass=propellant_mass,
                m_hydrogen=m_h2,
                m_oxygen=m_o2,
                vol_tank_h2=vt_h2,
                vol_tank_o2=vt_o2
            )
            
            # 4. Calculate subsystems
            subsystems = self.calculate_subsystems()
            
            # 5. Calculate structure and landing gear
            structure_mass, landing_gear_mass = self.estimate_structure_and_landing_gear(
                dry_mass_stat, inert_mass
            )
            
            # 6. Update dry mass with actual component masses
            dry_mass_actual = (
                subsystems['avionics']['mass'] +
                subsystems['eclss']['mass'] +
                subsystems['eps']['mass'] +
                subsystems['tcs']['mass'] +
                structure_mass +
                landing_gear_mass +
                propulsion['engine']['m_engine_total'] +
                propulsion['tank_h2']['mass'] +
                propulsion['tank_o2']['mass']
            )
            
            # 7. Update inert mass
            inert_mass_actual = payload + dry_mass_actual
            
            # 8. Calculate new total mass
            total_mass_new = inert_mass_actual + propellant_mass
            
            # 9. Check convergence
            mass_change = abs(total_mass_new - total_mass)
            
            # Store history
            self.history['iteration'].append(iteration + 1)
            self.history['total_mass'].append(total_mass_new)
            self.history['payload'].append(payload)
            self.history['dry_mass'].append(dry_mass_actual)
            self.history['inert_mass'].append(inert_mass_actual)
            self.history['propellant_mass'].append(propellant_mass)
            self.history['structure_mass'].append(structure_mass + landing_gear_mass)
            self.history['subsystems_mass'].append(
                subsystems['avionics']['mass'] + subsystems['eclss']['mass'] +
                subsystems['eps']['mass'] + subsystems['tcs']['mass']
            )
            
            if verbose:
                print(f"{iteration+1:<6} {total_mass_new:>10.0f} {payload:>10.0f} "
                      f"{dry_mass_actual:>10.0f} {propellant_mass:>10.0f} {mass_change:>10.1f}")
            
            # Check convergence
            if mass_change < tolerance:
                converged = True
                if verbose:
                    print("-" * 80)
                    print(f"✓ Converged after {iteration+1} iterations (Δm = {mass_change:.1f} kg)")
                break
            
            # Update for next iteration
            total_mass = total_mass_new
        
        if not converged:
            warnings.warn(f"Did not converge after {max_iterations} iterations. Δm = {mass_change:.1f} kg")
        
        # Store final results
        self.results = {
            'converged': converged,
            'iterations': iteration + 1,
            'total_mass': total_mass_new,
            'payload': payload,
            'dry_mass': dry_mass_actual,
            'inert_mass': inert_mass_actual,
            'propellant_mass': propellant_mass,
            'propellant': {
                'm_hydrogen': m_h2,
                'm_oxygen': m_o2,
                'vol_h2': v_h2,
                'vol_o2': v_o2,
                'vol_tank_h2': vt_h2,
                'vol_tank_o2': vt_o2
            },
            'propulsion': propulsion,
            'subsystems': subsystems,
            'structure': {
                'structure_tps': structure_mass,
                'landing_gear': landing_gear_mass,
                'total': structure_mass + landing_gear_mass
            },
            'mass_fractions': {
                'payload_fraction': payload / total_mass_new,
                'dry_fraction': dry_mass_actual / total_mass_new,
                'propellant_fraction': propellant_mass / total_mass_new,
                'mass_ratio': total_mass_new / inert_mass_actual
            }
        }
        
        return self.results
    
    def plot_convergence(self):
        """Plot mass convergence history."""
        if not self.history['iteration']:
            print("No iteration history available. Run iterate_design() first.")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        iterations = self.history['iteration']
        
        # Plot 1: Mass components
        ax1.plot(iterations, self.history['total_mass'], 'b-o', linewidth=2, label='Total Mass')
        ax1.plot(iterations, self.history['propellant_mass'], 'r-s', label='Propellant')
        ax1.plot(iterations, self.history['dry_mass'], 'g-^', label='Dry Mass')
        ax1.plot(iterations, self.history['payload'], 'orange', marker='d', label='Payload')
        
        ax1.set_xlabel('Iteration', fontsize=12)
        ax1.set_ylabel('Mass [kg]', fontsize=12)
        ax1.set_title('Mass Convergence History', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Mass change per iteration
        if len(iterations) > 1:
            mass_changes = [abs(self.history['total_mass'][i] - self.history['total_mass'][i-1]) 
                           for i in range(1, len(iterations))]
            ax2.semilogy(iterations[1:], mass_changes, 'b-o', linewidth=2)
            ax2.axhline(y=10, color='r', linestyle='--', label='Tolerance (10 kg)')
            ax2.set_xlabel('Iteration', fontsize=12)
            ax2.set_ylabel('Mass Change [kg]', fontsize=12)
            ax2.set_title('Convergence Rate', fontsize=14, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3, which='both')
        
        plt.tight_layout()
        plt.show()
    
    def plot_mass_breakdown(self):
        """Plot final mass breakdown pie chart."""
        if self.results is None:
            print("No results available. Run iterate_design() first.")
            return
        
        # Prepare data
        masses = [
            self.results['payload'],
            self.results['propellant']['m_hydrogen'],
            self.results['propellant']['m_oxygen'],
            self.results['propulsion']['engine']['m_engine_total'],
            self.results['propulsion']['tank_h2']['mass'] + self.results['propulsion']['tank_o2']['mass'],
            self.results['structure']['total'],
            self.results['subsystems']['avionics']['mass'],
            self.results['subsystems']['eclss']['mass'],
            self.results['subsystems']['eps']['mass'],
            self.results['subsystems']['tcs']['mass']
        ]
        
        labels = [
            'Payload',
            'Hydrogen',
            'Oxygen',
            'Engines',
            'Tanks',
            'Structure + LG',
            'Avionics',
            'ECLSS',
            'EPS',
            'TCS'
        ]
        
        colors = plt.cm.tab20(range(len(masses)))
        
        fig, ax = plt.subplots(figsize=(12, 8))
        wedges, texts, autotexts = ax.pie(
            masses, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 10}
        )
        
        ax.set_title(f'Lunar Lander Mass Breakdown\nTotal: {self.results["total_mass"]:.0f} kg',
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def generate_report(self):
        """Generate complete design report."""
        if self.results is None:
            print("No results available. Run iterate_design() first.")
            return
        
        print("\n" + "=" * 80)
        print("LUNAR LANDER FINAL DESIGN REPORT")
        print("=" * 80)
        
        r = self.results
        
        print(f"\n{'MASS SUMMARY':^80}")
        print("-" * 80)
        print(f"Total mass:          {r['total_mass']:>10.0f} kg")
        print(f"Payload:             {r['payload']:>10.0f} kg  ({100*r['mass_fractions']['payload_fraction']:>5.1f}%)")
        print(f"Dry mass:            {r['dry_mass']:>10.0f} kg  ({100*r['mass_fractions']['dry_fraction']:>5.1f}%)")
        print(f"Propellant mass:     {r['propellant_mass']:>10.0f} kg  ({100*r['mass_fractions']['propellant_fraction']:>5.1f}%)")
        print(f"Mass ratio:          {r['mass_fractions']['mass_ratio']:>10.3f}")
        
        print(f"\n{'PROPELLANT':^80}")
        print("-" * 80)
        print(f"Hydrogen:            {r['propellant']['m_hydrogen']:>10.0f} kg")
        print(f"Oxygen:              {r['propellant']['m_oxygen']:>10.0f} kg")
        print(f"H2 tank volume:      {r['propellant']['vol_tank_h2']:>10.2f} m³")
        print(f"O2 tank volume:      {r['propellant']['vol_tank_o2']:>10.2f} m³")
        
        print(f"\n{'PROPULSION':^80}")
        print("-" * 80)
        eng = r['propulsion']['engine']
        print(f"Thrust per engine:   {eng['thrust_per_engine']/1000:>10.1f} kN")
        print(f"Total thrust:        {eng['thrust_total']/1000:>10.1f} kN")
        print(f"Specific impulse:    {eng['isp']:>10.1f} s")
        print(f"Engine mass (total): {eng['m_engine_total']:>10.0f} kg")
        print(f"Tank mass (H2):      {r['propulsion']['tank_h2']['mass']:>10.0f} kg")
        print(f"Tank mass (O2):      {r['propulsion']['tank_o2']['mass']:>10.0f} kg")
        
        print(f"\n{'SUBSYSTEMS':^80}")
        print("-" * 80)
        subs = r['subsystems']
        print(f"Avionics:            {subs['avionics']['mass']:>10.0f} kg")
        print(f"ECLSS:               {subs['eclss']['mass']:>10.0f} kg")
        print(f"EPS:                 {subs['eps']['mass']:>10.0f} kg")
        print(f"TCS:                 {subs['tcs']['mass']:>10.0f} kg")
        
        print(f"\n{'STRUCTURE':^80}")
        print("-" * 80)
        print(f"Structure + TPS:     {r['structure']['structure_tps']:>10.0f} kg")
        print(f"Landing gear:        {r['structure']['landing_gear']:>10.0f} kg")
        
        print("\n" + "=" * 80)


# Example usage
if __name__ == "__main__":
    # Create designer
    designer = LunarLanderDesigner(
        initial_total_mass=30000,
        n_crew=4,
        mission_duration=15,
        payload_override=1060  # Fixed payload as in MATLAB code
    )
    
    # Run iterative design
    results = designer.iterate_design(tolerance=10.0, verbose=True)
    
    # Generate report
    designer.generate_report()
    
    # Plot results
    # designer.plot_convergence()
    # designer.plot_mass_breakdown()
