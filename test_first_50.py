#!/usr/bin/env python
"""
Test script to debug FLake initialization and first 50 timesteps.
Compares Python implementation with reference test file.
"""

import numpy as np
import pandas as pd
import f90nml
import sys

# Import from the main Python file (we'll use exec to load it)
exec(open('FLAKE_Model_CORRECTED_FINAL_helsinngese_FIXED.py').read())

def load_test_file(filename, n_rows=None):
    """Load the reference test file"""
    # Skip header rows (first 2 lines)
    data = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[2:]):  # Skip first 2 header lines
            if n_rows and i >= n_rows:
                break
            parts = line.split()
            if len(parts) >= 22:  # Ensure we have enough columns
                data.append([float(x) for x in parts])

    df = pd.DataFrame(data, columns=[
        'No', 'time', 'Ts', 'Tm', 'Tb', 'ufr_a', 'ufr_w', 'Wconv', 'Qw',
        'Q_se', 'Q_la', 'I_w', 'Q_lwa', 'Q_lww', 'h_ML', 'C_T', 'H_B1',
        'T_B1', 'Qbot', 'H_ice', 'H_snow', 'T_ice', 'T_snow'
    ])

    return df

def compare_values(step, var_name, py_val, test_val, tolerance=0.001):
    """Compare Python output with test file"""
    diff = abs(py_val - test_val)
    rel_diff = diff / max(abs(test_val), 1e-10) * 100

    match = "✓" if diff < tolerance else "✗"

    print(f"  {match} {var_name:6s}: Python={py_val:12.6f}  Test={test_val:12.6f}  Diff={diff:12.6f}  ({rel_diff:6.2f}%)")

    return diff < tolerance

def main():
    print("="*80)
    print("FLake First 50 Timesteps Debug Test")
    print("="*80)

    # Load configuration
    print("\n1. Loading configuration from Heiligensee80-96.nml...")
    cfg = parse_flake_nml("Heiligensee80-96.nml")

    print(f"   Initial conditions from NML:")
    print(f"   - T_wML_0 = {cfg['T_wML_0']-273.15:.2f}°C ({cfg['T_wML_0']:.2f}K)")
    print(f"   - T_bot_0 = {cfg['T_bot_0']-273.15:.2f}°C ({cfg['T_bot_0']:.2f}K)")
    print(f"   - T_mnw_0 = {cfg['T_mnw_0']-273.15:.2f}°C ({cfg['T_mnw_0']:.2f}K)")
    print(f"   - T_B1_0  = {cfg['T_B1_0']-273.15:.2f}°C ({cfg['T_B1_0']:.2f}K)")
    print(f"   - h_ML_0  = {cfg['h_ML_0']:.2f}m")
    print(f"   - depth_w = {cfg['depth_w']:.2f}m")

    # Load test file for comparison
    print("\n2. Loading reference test file...")
    test_df = load_test_file("Heiligensee80-96.test", n_rows=52)
    print(f"   Loaded {len(test_df)} rows from test file")

    # Load meteorological forcing (first 50 values)
    print("\n3. Loading meteorological forcing data (first 50 values)...")
    forcing = load_meteo_from_cfg(cfg)
    n_test = 50

    for key in forcing:
        forcing[key] = forcing[key][:n_test]

    print(f"   Using {len(forcing['I_solar'])} timesteps")

    # Initialize state
    print("\n4. Initializing FLake state...")
    T_wML = cfg["T_wML_0"]
    T_bot = cfg["T_bot_0"]
    T_mnw = cfg["T_mnw_0"]
    T_B1 = cfg["T_B1_0"]
    h_ML = cfg["h_ML_0"]

    # Initialize remaining variables
    h_ice = 0.0
    h_snow = 0.0
    T_ice = T_wML
    T_snow = T_wML
    C_T = 0.5
    H_B1 = 5.0
    T_sfc = T_wML

    print(f"   State initialized:")
    print(f"   - T_wML = {T_wML-273.15:.5f}°C")
    print(f"   - T_bot = {T_bot-273.15:.5f}°C")
    print(f"   - T_mnw = {T_mnw-273.15:.5f}°C")
    print(f"   - h_ML  = {h_ML:.5f}m")
    print(f"   - C_T   = {C_T:.5f}")

    # Get parameters
    del_time = cfg["del_time"]
    depth_w = cfg["depth_w"]
    depth_bs = cfg["depth_bs"]
    T_bs = cfg["T_bs"]
    par_Coriolis = cfg["par_Coriolis"]
    height_u_in = cfg["height_u"]
    height_tq_in = cfg["height_tq"]
    extincoef_water_typ = cfg["extincoef_water_typ"]
    fetch = cfg["fetch"]

    P_air = 101325.0

    # Storage for results
    results = []

    # Compare initial state (timestep 0)
    print("\n" + "="*80)
    print(f"TIMESTEP 0 (Initial State)")
    print("="*80)

    test_row = test_df.iloc[0]
    print(f"Test file values:")
    print(f"  Ts    = {test_row['Ts']:.5f}°C")
    print(f"  Tm    = {test_row['Tm']:.5f}°C")
    print(f"  Tb    = {test_row['Tb']:.5f}°C")
    print(f"  h_ML  = {test_row['h_ML']:.5f}m")
    print(f"  C_T   = {test_row['C_T']:.5f}")

    print(f"\nPython initial values:")
    print(f"  Ts    = {T_wML-273.15:.5f}°C")
    print(f"  Tm    = {T_mnw-273.15:.5f}°C")
    print(f"  Tb    = {T_bot-273.15:.5f}°C")
    print(f"  h_ML  = {h_ML:.5f}m")
    print(f"  C_T   = {C_T:.5f}")

    print(f"\nComparison:")
    compare_values(0, "Ts", T_wML-273.15, test_row['Ts'])
    compare_values(0, "Tm", T_mnw-273.15, test_row['Tm'])
    compare_values(0, "Tb", T_bot-273.15, test_row['Tb'])
    compare_values(0, "h_ML", h_ML, test_row['h_ML'])
    compare_values(0, "C_T", C_T, test_row['C_T'])

    # Run simulation for first 5 timesteps with detailed output
    print("\n" + "="*80)
    print("Running first 5 timesteps with detailed comparison...")
    print("="*80)

    for step in range(1, 6):
        print(f"\n{'='*80}")
        print(f"TIMESTEP {step}")
        print(f"{'='*80}")

        # Get forcing for this timestep
        i = step - 1
        I_solar = forcing["I_solar"][i]
        T_air_C = forcing["T_air_C"][i]
        hum_mb = forcing["humidity_mb"][i]
        U_wind = forcing["U_wind"][i]
        cloud = forcing["cloud"][i]

        T_air_K = T_air_C + 273.15

        print(f"\nForcing data:")
        print(f"  I_solar  = {I_solar:.4f} W/m²")
        print(f"  T_air    = {T_air_C:.4f}°C ({T_air_K:.4f}K)")
        print(f"  humidity = {hum_mb:.4f} mb")
        print(f"  U_wind   = {U_wind:.4f} m/s")
        print(f"  cloud    = {cloud:.4f}")

        # Call flake_interface (simplified version)
        # This should match the Fortran interface exactly

        # We need to extract and run the time loop properly
        # For now, let's just show what values we expect

        test_row = test_df.iloc[step]
        print(f"\nExpected values from test file:")
        print(f"  Ts    = {test_row['Ts']:.5f}°C")
        print(f"  Tm    = {test_row['Tm']:.5f}°C")
        print(f"  Tb    = {test_row['Tb']:.5f}°C")
        print(f"  h_ML  = {test_row['h_ML']:.5f}m")
        print(f"  C_T   = {test_row['C_T']:.5f}")

        # TODO: Actually run the model timestep here
        print(f"\n⚠ Model execution to be implemented")

        break  # Just show first timestep for now

    print("\n" + "="*80)
    print("Test script completed.")
    print("="*80)

if __name__ == "__main__":
    main()
