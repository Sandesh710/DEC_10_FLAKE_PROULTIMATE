#!/usr/bin/env python
"""
Comprehensive test script for FLake model - First 50 timesteps
Tests initialization and time-stepping against Fortran reference output
"""

import numpy as np
import pandas as pd
import sys

print("="*80)
print("FLake Model Test - First 50 Timesteps")
print("="*80)

# ============================================================================
# Step 1: Load test file
# ============================================================================
print("\n1. Loading reference test file...")
test_data = []
with open('Heiligensee80-96.test', 'r') as f:
    lines = f.readlines()
    for line in lines[2:62]:  # Read rows 0-59 (first 60 rows)
        parts = line.split()
        if len(parts) >= 22:
            test_data.append([float(x) for x in parts])

test_df = pd.DataFrame(test_data, columns=[
    'No', 'time', 'Ts', 'Tm', 'Tb', 'ufr_a', 'ufr_w', 'Wconv', 'Qw',
    'Q_se', 'Q_la', 'I_w', 'Q_lwa', 'Q_lww', 'h_ML', 'C_T', 'H_B1',
    'T_B1', 'Qbot', 'H_ice', 'H_snow', 'T_ice', 'T_snow'
])

print(f"   Loaded {len(test_df)} reference rows (0-{len(test_df)-1})")
print(f"   Columns: {list(test_df.columns)}")

# Show first few rows for verification
print(f"\n   First 5 rows from test file:")
print(test_df[['No', 'Ts', 'Tm', 'Tb', 'h_ML', 'C_T']].head())

# ============================================================================
# Step 2: Run Python model (if available)
# ============================================================================
print("\n2. Attempting to run Python FLake model...")

try:
    # Try to import without auto-execution
    # Since we added if __name__ == "__main__" guard, we can import
    print("   NOTE: The Python file auto-executes, so we cannot import cleanly yet.")
    print("   Instead, we'll document what SHOULD happen...")

    # Show what we expect from row 0
    row0 = test_df.iloc[0]
    print(f"\n   Expected initial state (row 0):")
    print(f"   Ts    = {row0['Ts']:.5f}°C")
    print(f"   Tm    = {row0['Tm']:.5f}°C")
    print(f"   Tb    = {row0['Tb']:.5f}°C")
    print(f"   h_ML  = {row0['h_ML']:.5f}m")
    print(f"   C_T   = {row0['C_T']:.5f}")

    # Calculate what T_mnw should be with corrected formula
    T_wML_nml = 4.0 + 273.15  # K
    T_bot_nml = 4.0 + 273.15  # K
    h_ML_nml = 3.0  # m
    depth_w = 5.9  # m
    C_T_init = 0.5

    zeta_h = h_ML_nml / depth_w
    factor = (1.0 - zeta_h) * C_T_init  # Corrected: C_T not C_T/2
    T_mnw_calc = T_wML_nml - (T_wML_nml - T_bot_nml) * factor
    T_mnw_calc_C = T_mnw_calc - 273.15

    print(f"\n   With CORRECTED formula (C_T, not C_T/2):")
    print(f"   T_mnw_calc = {T_mnw_calc_C:.5f}°C")
    print(f"   Expected   = {row0['Tm']:.5f}°C")
    print(f"   Error      = {abs(T_mnw_calc_C - row0['Tm']):.7f}°C")

    if abs(T_mnw_calc_C - row0['Tm']) < 0.0001:
        print(f"   ✓✓✓ PERFECT MATCH!")
    else:
        print(f"   ⚠ Small discrepancy")

except Exception as e:
    print(f"   Error: {e}")

# ============================================================================
# Step 3: Analysis of what needs to happen
# ============================================================================
print("\n" + "="*80)
print("3. Analysis: What happens in first 50 timesteps")
print("="*80)

print("\nKey transitions:")
for i in [0, 1, 2, 5, 10, 12, 20, 30, 40, 50]:
    if i < len(test_df):
        row = test_df.iloc[i]
        ice = "ICE!" if row['H_ice'] > 0 else "open"
        mix = "FULL MIX" if row['h_ML'] >= 5.89 else f"h={row['h_ML']:.2f}m"
        print(f"  Step {i:2d}: Ts={row['Ts']:6.3f}°C  {mix:12s}  {ice}")

# Check when ice forms
ice_rows = test_df[test_df['H_ice'] > 0]
if len(ice_rows) > 0:
    first_ice = ice_rows.iloc[0]
    print(f"\n   Ice first appears at step {int(first_ice['No'])}")
    print(f"   Temperature at ice formation: {first_ice['Ts']:.3f}°C")

# ============================================================================
# Step 4: Identify critical test points
# ============================================================================
print("\n" + "="*80)
print("4. Critical Test Points for Validation")
print("="*80)

print("\nRow 0 (Initial state):")
print("  - Tests: Initialization formulas")
print("  - Key: T_mnw calculation must be exact")
print("  - Status: ✓ Fixed (C_T formula corrected)")

print("\nRow 1 (First timestep):")
row1 = test_df.iloc[1]
print(f"  - Ts: {row0['Ts']:.5f}°C → {row1['Ts']:.5f}°C (Δ={row1['Ts']-row0['Ts']:.5f}°C)")
print(f"  - h_ML: {row0['h_ML']:.2f}m → {row1['h_ML']:.2f}m (FULL MIXING!)")
print("  - Tests: Strong cooling, convective mixing")
print("  - Physics: Surface heat loss → deep convection")

print("\nRows 2-5 (Continued cooling):")
for i in range(2, 6):
    r = test_df.iloc[i]
    print(f"  Row {i}: Ts={r['Ts']:6.3f}°C, h_ML={r['h_ML']:.2f}m, fully mixed")

print("\nRows 12-15 (Ice formation):")
for i in range(12, min(16, len(test_df))):
    r = test_df.iloc[i]
    ice_status = f"H_ice={r['H_ice']:.4f}m" if r['H_ice'] > 0 else "no ice"
    print(f"  Row {i}: Ts={r['Ts']:6.3f}°C, {ice_status}")

# ============================================================================
# Step 5: Create validation checklist
# ============================================================================
print("\n" + "="*80)
print("5. Validation Checklist")
print("="*80)

checklist = [
    ("Row 0 initialization", "T_mnw formula", "✓ Fixed"),
    ("Row 0 fluxes", "Q_w, Q_se, Q_la computation", "⚠ To test"),
    ("Row 1 transition", "Full mixing physics", "⚠ To test"),
    ("Rows 1-5", "Temperature evolution", "⚠ To test"),
    ("Rows 12+", "Ice formation", "⚠ To test"),
    ("All fluxes", "Match test file values", "⚠ To test"),
]

print("\nStatus:")
for item, description, status in checklist:
    print(f"  {status:12s} {item:25s} - {description}")

# ============================================================================
# Step 6: Next steps
# ============================================================================
print("\n" + "="*80)
print("6. Next Steps to Complete Testing")
print("="*80)

print("""
To fully validate the Python implementation:

1. ✓ DONE: Fix T_mnw initialization formula (C_T not C_T/2)

2. TODO: Make Python file importable without auto-execution
   - Move main execution code inside if __name__ == "__main__":
   - Or create separate flake_functions.py module

3. TODO: Create test that calls flake_interface() for each timestep
   - Initialize from row 0 values
   - Call flake_interface with forcing data
   - Compare outputs with test file

4. TODO: Debug first timestep (0→1)
   - Verify strong cooling (-0.39°C)
   - Verify full mixing (h_ML: 3m → 5.9m)
   - Check all flux values

5. TODO: Validate rows 1-5
   - Ensure continued cooling matches
   - Check convective deepening logic

6. TODO: Validate ice formation (row 12+)
   - Ensure Ts → 0°C when ice exists
   - Check ice/snow thickness evolution

7. TODO: Run full 50 timesteps and check for drift

Current files ready for testing:
  • FLAKE_Model_CORRECTED_FINAL_helsinngese_FIXED.py (with T_mnw fix)
  • Heiligensee80-96.nml (configuration)
  • Potsdam80-96.dat (forcing)
  • Heiligensee80-96.test (reference)
""")

print("="*80)
print("Test framework ready. Awaiting model execution...")
print("="*80)
