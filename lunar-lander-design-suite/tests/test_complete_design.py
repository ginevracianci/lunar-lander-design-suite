"""
Test script to verify complete lunar lander design functionality.

This script tests all major modules and ensures the design converges correctly.
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
from lunar_lander import LunarLanderDesigner


def test_mission_analyzer():
    """Test the complete mission analyzer."""
    print("=" * 80)
    print("TESTING LUNAR LANDER DESIGN SUITE")
    print("=" * 80)
    
    # Create designer
    designer = LunarLanderDesigner(
        initial_total_mass=30000,
        n_crew=4,
        mission_duration=15,
        payload_override=1060
    )
    
    print("\n✓ Designer created successfully")
    
    # Run design
    print("\nRunning iterative design...")
    results = designer.iterate_design(tolerance=10.0, verbose=True)
    
    # Check convergence
    assert results['converged'], "❌ Design did not converge"
    print("\n✓ Design converged successfully")
    
    # Check mass fractions are reasonable
    assert 0.40 < results['mass_fractions']['propellant_fraction'] < 0.65, \
        f"❌ Propellant fraction {results['mass_fractions']['propellant_fraction']:.3f} out of range"
    print("✓ Mass fractions are reasonable")
    
    # Check total mass is in expected range
    assert 10000 < results['total_mass'] < 35000, \
        f"❌ Total mass {results['total_mass']:.0f} kg is out of expected range"
    print(f"✓ Total mass ({results['total_mass']:.0f} kg) is in expected range")
    
    # Check engine performance
    isp = results['propulsion']['engine']['isp']
    assert 430 < isp < 450, f"❌ Isp {isp:.1f} s is out of range"
    print(f"✓ Engine Isp ({isp:.1f} s) is reasonable")
    
    # Check mass ratio
    mass_ratio = results['mass_fractions']['mass_ratio']
    assert 1.5 < mass_ratio < 3.5, f"❌ Mass ratio {mass_ratio:.3f} is out of range"
    print(f"✓ Mass ratio ({mass_ratio:.3f}) is reasonable")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! ✓")
    print("=" * 80)
    
    # Generate report
    designer.generate_report()
    
    return designer, results


if __name__ == "__main__":
    try:
        designer, results = test_mission_analyzer()
        print("\n✓ Lunar Lander Design Suite is working correctly!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise
