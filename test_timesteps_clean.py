#!/usr/bin/env python
"""
Clean test script - initialize from test file row 0, run timesteps 1-5
This isolates time-stepping logic from initialization issues.
"""

import numpy as np
import pandas as pd

print("FLake Clean Timestep Test - Initialize from test file row 0")
print("="*80)

# Load test file
print("\n1. Loading test file...")
test_data = []
with open('Heiligensee80-96.test', 'r') as f:
    lines = f.readlines()
    for line in lines[2:60]:  # Skip headers, read first 58 rows
        parts = line.split()
        if len(parts) >= 22:
            test_data.append([float(x) for x in parts])

test_df = pd.DataFrame(test_data, columns=[
    'No', 'time', 'Ts', 'Tm', 'Tb', 'ufr_a', 'ufr_w', 'Wconv', 'Qw',
    'Q_se', 'Q_la', 'I_w', 'Q_lwa', 'Q_lww', 'h_ML', 'C_T', 'H_B1',
    'T_B1', 'Qbot', 'H_ice', 'H_snow', 'T_ice', 'T_snow'
])

print(f"   Loaded {len(test_df)} rows")

# Extract initial state from row 0
row0 = test_df.iloc[0]
print("\n2. Initial state from test file row 0:")
print(f"   Ts    = {row0['Ts']:.5f}°C")
print(f"   Tm    = {row0['Tm']:.5f}°C")
print(f"   Tb    = {row0['Tb']:.5f}°C")
print(f"   h_ML  = {row0['h_ML']:.5f}m")
print(f"   C_T   = {row0['C_T']:.5f}")
print(f"   H_ice = {row0['H_ice']:.5f}m")
print(f"   H_snow= {row0['H_snow']:.5f}m")

# Load meteorological forcing
print("\n3. Loading meteorological forcing...")
forcing_data = np.loadtxt('Potsdam80-96.dat')
print(f"   Loaded {len(forcing_data)} forcing timesteps")
print(f"   First row: I_solar={forcing_data[0,1]}, T_air={forcing_data[0,2]}, U_wind={forcing_data[0,4]}")

# Now we need to import the FLake functions without running the main script
# This is tricky because the Python file executes on import
# For now, let's just show what SHOULD happen:

print("\n4. What SHOULD happen:")
print("   Step 1: Initialize state from test row 0")
print("           T_wML = 4.0°C,  T_mnw = 3.99509°C, T_bot = 3.98001°C")
print("           h_ML = 3.0m, C_T = 0.5")
print("")
print("   Step 2: Load forcing for timestep 1")
forcing_1 = forcing_data[0]  # First row of forcing file
print(f"           I_solar = {forcing_1[1]:.2f} W/m²")
print(f"           T_air   = {forcing_1[2]:.2f}°C")
print(f"           humid   = {forcing_1[3]:.2f} mb")
print(f"           U_wind  = {forcing_1[4]:.2f} m/s")
print(f"           cloud   = {forcing_1[5]:.2f}")
print("")
print("   Step 3: Call flake_interface()")
print("           → Should compute fluxes, update temperatures, depths")
print("")
print("   Step 4: Compare output with test row 1:")
row1 = test_df.iloc[1]
print(f"           Expected Ts = {row1['Ts']:.5f}°C")
print(f"           Expected Tm = {row1['Tm']:.5f}°C")
print(f"           Expected Tb = {row1['Tb']:.5f}°C")
print(f"           Expected h_ML = {row1['h_ML']:.5f}m")
print("")
print(f"   NOTE: h_ML goes from 3.0m → 5.9m (fully mixed!)")
print(f"         All temps become equal: Ts=Tm=Tb=3.60939°C")
print(f"         This indicates strong cooling/mixing occurred")

print("\n5. Key Findings:")
print("   • Row 0 initialization is complex - involves profile calculations")
print("   • Timestep 0→1 shows full mixing (h_ML reaches depth_w)")
print("   • Strong cooling: 4.0°C → 3.61°C")
print("   • This suggests the physics is working to mix/cool the lake")

print("\n6. ACTION NEEDED:")
print("   To properly test, we need to:")
print("   ① Extract FLake functions into importable module (no auto-exec)")
print("   ② Initialize exactly from test row 0")
print("   ③ Run flake_interface for each timestep")
print("   ④ Compare outputs")
print("")
print("   The current Python file runs automatically on import,")
print("   making it hard to use functions independently.")
print("")
print("   RECOMMENDATION:")
print("   • Add 'if __name__ == \"__main__\":' guard to Python file")
print("   • Or create separate module with just functions")
print("   • Then create proper test harness")

print("\n" + "="*80)
print("Test framework ready - awaiting function extraction")
print("="*80)
