#!/usr/bin/env python
"""
Debug script to understand FLake initialization and compare with test file.
"""

import numpy as np
import f90nml

# Read NML file
nml = f90nml.read('Heiligensee80-96.nml')

# Extract simulation parameters
sim = nml['SIMULATION_PARAMS']
T_wML_in_C = float(sim['T_wML_in'])  # 4.0°C from NML
T_bot_in_C = float(sim['T_bot_in'])  # 4.0°C from NML
h_ML_in = float(sim['h_ML_in'])      # 3.0 m from NML

# Lake parameters
lake = nml['LAKE_PARAMS']
depth_w = float(lake['depth_w_lk'])  # 5.9 m

# Convert to Kelvin
T_wML_init_K = T_wML_in_C + 273.15  # 277.15 K
T_bot_init_K = T_bot_in_C + 273.15  # 277.15 K

# Read test file to see what row 0 actually contains
with open('Heiligensee80-96.test', 'r') as f:
    lines = f.readlines()

# Parse row 0 (line index 2, skipping 2 header lines)
row0_data = lines[2].split()
row0_no = int(row0_data[0])
row0_time = float(row0_data[1])
row0_Ts = float(row0_data[2])    # Surface temp (should match T_wML when no ice)
row0_Tm = float(row0_data[3])    # Mean water temp (T_mnw)
row0_Tb = float(row0_data[4])    # Bottom temp (T_bot)
row0_h_ML = float(row0_data[14])
row0_C_T = float(row0_data[15])
row0_H_B1 = float(row0_data[16])
row0_T_B1 = float(row0_data[17])

print("="*80)
print("FLake Initialization Debug")
print("="*80)

print("\n1. NML Input Values:")
print(f"   T_wML_in = {T_wML_in_C:.5f}°C ({T_wML_init_K:.2f}K)")
print(f"   T_bot_in = {T_bot_in_C:.5f}°C ({T_bot_init_K:.2f}K)")
print(f"   h_ML_in  = {h_ML_in:.5f}m")
print(f"   depth_w  = {depth_w:.1f}m")

print("\n2. Test File Row 0 Values (timestep 0):")
print(f"   No       = {row0_no}")
print(f"   time     = {row0_time:.5f}")
print(f"   Ts       = {row0_Ts:.5f}°C  (surface/mixed-layer temp)")
print(f"   Tm       = {row0_Tm:.5f}°C  (mean water column temp)")
print(f"   Tb       = {row0_Tb:.5f}°C  (bottom temp)")
print(f"   h_ML     = {row0_h_ML:.5f}m")
print(f"   C_T      = {row0_C_T:.5f}")
print(f"   H_B1     = {row0_H_B1:.5f}m")
print(f"   T_B1     = {row0_T_B1:.5f}°C")

print("\n3. Analysis:")
print(f"   Ts (row 0) = {row0_Ts:.5f}°C  vs  NML T_wML = {T_wML_in_C:.5f}°C")
print(f"   → Match: {abs(row0_Ts - T_wML_in_C) < 0.001}")
print(f"")
print(f"   Tm (row 0) = {row0_Tm:.5f}°C  vs  NML T_wML = {T_wML_in_C:.5f}°C")
print(f"   → Difference: {row0_Tm - T_wML_in_C:.6f}°C")
print(f"   → Tm is LESS than Ts by {row0_Ts - row0_Tm:.6f}°C")
print(f"")
print(f"   Tb (row 0) = {row0_Tb:.5f}°C  vs  NML T_bot = {T_bot_in_C:.5f}°C")
print(f"   → Difference: {row0_Tb - T_bot_in_C:.6f}°C")
print(f"   → Tb is LESS than NML by {T_bot_in_C - row0_Tb:.6f}°C")
print(f"")
print(f"   h_ML (row 0) = {row0_h_ML:.5f}m  vs  NML h_ML = {h_ML_in:.5f}m")
print(f"   → Match: {abs(row0_h_ML - h_ML_in) < 0.001}")

print("\n4. Hypothesis:")
print("   Row 0 represents the INITIAL state where:")
print("   - Ts = T_wML from NML (4.0°C) ✓")
print("   - h_ML = h_ML from NML (3.0m) ✓")
print("   - C_T = 0.5 (default) ✓")
print("   - Tm and Tb are CALCULATED from the temperature profile")
print("     using the FLake shape function integration")

print("\n5. Computing Tm and Tb from profile:")

# FLake uses shape functions to describe T(z) profile
# The mean temperature Tm integrates T over depth
# T_mnw = integral(T(z) dz) / depth_w

# Mixed layer (0 to h_ML): T = T_wML (constant)
# Thermocline (h_ML to depth_w): T varies from T_wML to T_bot according to shape function

# Shape function parameter
C_T = 0.5
zeta_h = h_ML_in / depth_w  # dimensionless mixed layer depth

# According to FLake theory (Mironov 2008, Kirillin et al.):
# The temperature profile in thermocline uses shape function Phi_T
# T(z) = T_wML - (T_wML - T_bot) * Phi_T(zeta)
# where zeta = (z - h_ML) / (depth_w - h_ML) ranges from 0 to 1

# The mean temperature over the entire water column:
# T_mnw = [integral(0 to h_ML) T_wML dz + integral(h_ML to D) T(z) dz] / D
#
# For the thermocline integral, using self-similar profile:
# integral(h_ML to D) T(z) dz = (D - h_ML) * [T_wML - (T_wML - T_bot) * integral(Phi_T)]
#
# integral(Phi_T from 0 to 1) = C_T^2 / (2*C_T) = C_T/2
# (This comes from the specific form of Phi_T used in FLake)

# Therefore:
# T_mnw = h_ML/D * T_wML + (1 - h_ML/D) * [T_wML - (T_wML - T_bot) * C_T/2]
# T_mnw = T_wML - (T_wML - T_bot) * (1 - h_ML/D) * C_T/2

# BUT: We need to find T_bot such that when integrated, we get the observed T_mnw!
# This is a diagnostic calculation that happens during initialization

# From the test file, we know:
# Ts = 4.00000, Tm = 3.99509, Tb = 3.98001, h_ML = 3.0, C_T = 0.5

# Let's verify the relationship:
Ts_test = row0_Ts
Tm_test = row0_Tm
Tb_test = row0_Tb
h_ML_test = row0_h_ML
C_T_test = row0_C_T

zeta_h_test = h_ML_test / depth_w
factor = (1.0 - zeta_h_test) * C_T_test / 2.0

# Check if: T_mnw = T_wML - (T_wML - T_bot) * factor
Tm_calc = Ts_test - (Ts_test - Tb_test) * factor
Tm_err = abs(Tm_calc - Tm_test)

print(f"   Given: Ts={Ts_test}, Tb={Tb_test}, h_ML={h_ML_test}, C_T={C_T_test}")
print(f"   Factor = (1 - h_ML/D) * C_T/2 = {factor:.6f}")
print(f"   Calculated: Tm = Ts - (Ts - Tb) * factor")
print(f"             Tm = {Ts_test} - ({Ts_test} - {Tb_test}) * {factor:.6f}")
print(f"             Tm = {Tm_calc:.5f}°C")
print(f"   Expected:  Tm = {Tm_test:.5f}°C")
print(f"   Error:         {Tm_err:.6f}°C  {'✓ MATCHES!' if Tm_err < 0.0001 else '✗ NO MATCH'}")

print("\n6. Conclusion:")
if Tm_err < 0.0001:
    print("   ✓ The formula T_mnw = T_wML - (T_wML - T_bot) * (1 - h_ML/D) * C_T/2")
    print("     correctly predicts T_mnw from the profile!")
    print("\n   This means:")
    print("   - T_bot is set from NML, then adjusted based on physics")
    print("   - T_mnw is DERIVED from the profile, not input directly")
    print("   - The Python code should calculate T_mnw using this formula")

    print("\n7. Initialization Fix Needed:")
    print("   Current Python code (line 3664):")
    print("       T_mnw_0 = T_wML_0    # WRONG!")
    print("\n   Correct initialization:")
    print("       # Set T_bot from physics/equilibrium (needs investigation)")
    print("       T_bot_0 = ... # Calculate from initial conditions")
    print("       # Then derive T_mnw from profile:")
    print("       zeta_h = h_ML_0 / depth_w")
    print("       factor = (1.0 - zeta_h) * C_T_min / 2.0")
    print("       T_mnw_0 = T_wML_0 - (T_wML_0 - T_bot_0) * factor")
else:
    print("   ✗ The formula doesn't match - need more investigation")

print("\n" + "="*80)
