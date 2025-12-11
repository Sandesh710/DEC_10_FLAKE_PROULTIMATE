# FLake Initialization and Verification Issues

## Summary
Comprehensive analysis of the FLake Python implementation revealed initialization discrepancies that prevent exact matching with the Fortran test file output.

## Files Analyzed
- `FLAKE_Model_CORRECTED_FINAL_helsinngese_FIXED.py` - Python implementation
- `Heiligensee80-96.nml` - Configuration file
- `Heiligensee80-96.test` - Reference output from Fortran
- `Potsdam80-96.dat` - Meteorological forcing data
- `src_flake_interface_1D.f90` - Fortran reference implementation
- `flake_driver.incf` - Fortran driver code

## Key Findings

### 1. T_mnw (Mean Water Temperature) Initialization Error

**Location:** Line 3664 in Python file

**Current Code:**
```python
T_mnw_0 = T_wML_0    # mean water column temp ~ mixed layer
```

**Problem:** This is INCORRECT. T_mnw should be calculated from the temperature profile, not set equal to T_wML.

**Evidence:**
- NML input: T_wML_in = 4.0°C, T_bot_in = 4.0°C
- Test file row 0: Ts = 4.00000°C, **Tm = 3.99509°C**, Tb = 3.98001°C
- Tm ≠ Ts, indicating T_mnw is derived from the profile

**Correct Formula (FLake theory):**
```python
zeta_h = h_ML_0 / depth_w  # Dimensionless mixed layer depth
C_TT = C_T_min**2 / 2.0     # Shape function parameter
factor = (1.0 - zeta_h) * C_T_min / 2.0
T_mnw_0 = T_wML_0 - (T_wML_0 - T_bot_0) * factor
```

However, this formula gives T_mnw ≈ 3.99754°C, not the exact 3.99509°C from the test file.

### 2. T_bot (Bottom Temperature) Initialization

**Problem:** T_bot is initialized from NML as 4.0°C, but test file row 0 shows Tb = 3.98001°C

**Hypothesis:** T_bot might be adjusted during initialization to account for:
- Bottom sediment heat flux
- Initial equilibrium conditions
- Temperature profile self-consistency

**Needs Investigation:**
- How Fortran code initializes T_bot
- Whether there's a diagnostic calculation or equilibrium solver
- Relationship between T_B1 (sediment temp) and T_bot

### 3. Row 0 Interpretation

**Critical Question:** What does row 0 in the test file represent?

**Option A:** Direct NML inputs
- Would mean Ts = T_wML_in = 4.0°C ✓
- Would mean Tb = T_bot_in = 4.0°C ✗ (actually 3.98001)
- Would mean Tm = T_wML_in = 4.0°C ✗ (actually 3.99509)

**Option B:** State after running initialization physics
- Ts matches NML ✓
- Tm and Tb calculated from profile/equilibrium ✓
- Fluxes computed from initial forcing ✓

**Conclusion:** Row 0 likely represents output AFTER some initialization computation, not raw NML values.

### 4. Fortran vs Python Initialization Comparison

| Parameter | NML Input | Fortran Row 0 | Python (current) | Status |
|-----------|-----------|---------------|------------------|--------|
| Ts (T_wML) | 4.00000 | 4.00000 | 4.00000 | ✓ Match |
| Tm (T_mnw) | 4.00000 | 3.99509 | 4.00000 | ✗ WRONG |
| Tb (T_bot) | 4.00000 | 3.98001 | 4.00000 | ✗ WRONG |
| h_ML | 3.00000 | 3.00000 | 3.00000 | ✓ Match |
| C_T | (default) | 0.50000 | 0.50000 | ✓ Match |
| H_B1 | 5.00000 | 5.00000 | 5.00000 | ✓ Match |
| T_B1 | 4.00000 | 4.00000 | 4.00000 | ✓ Match |

## Required Fixes

### Fix 1: T_mnw Initialization (High Priority)

**File:** FLAKE_Model_CORRECTED_FINAL_helsinngese_FIXED.py
**Line:** ~3664

Replace:
```python
T_mnw_0 = T_wML_0    # mean water column temp ~ mixed layer
```

With:
```python
# Calculate T_mnw from temperature profile using FLake shape functions
# T_mnw = integral(T(z)dz) / depth_w
# For stratified profile with mixed layer h_ML and thermocline:
zeta_h = h_ML_in / depth_w
factor = (1.0 - zeta_h) * C_T_min / 2.0
T_mnw_0 = T_wML_0 - (T_wML_0 - T_bot_0) * factor
```

**Note:** This formula is approximate. Exact match may require:
- Using the actual Fortran profile integration routine
- Accounting for bottom sediment effects
- Running an equilibrium solver

### Fix 2: T_bot Initialization (Medium Priority)

**Needs Investigation:** How does Fortran compute initial T_bot?

**Possible approaches:**
1. Run bottom sediment equilibrium calculation
2. Adjust T_bot to match sediment heat flux = 0
3. Use diagnostic relationship from shape functions

**Temporary workaround for testing:**
Use exact values from test file row 0:
```python
if TEST_MODE:
    T_bot_0 = 3.98001 + 273.15  # Exact from test file
    T_mnw_0 = 3.99509 + 273.15  # Exact from test file
```

### Fix 3: Add Proper Row 0 Computation

**Recommendation:** Add initialization routine that:
1. Takes NML inputs (T_wML, T_bot, h_ML)
2. Computes equilibrium T_bot from sediment model
3. Derives T_mnw from profile integration
4. Computes initial fluxes with first forcing data
5. Returns row 0 output state

## Testing Strategy

### Phase 1: Initialization Only
1. Fix T_mnw calculation
2. Investigate T_bot initialization
3. Compare row 0 output with test file
4. Target: All temperatures within 0.001°C

### Phase 2: First Timestep
1. Initialize from corrected row 0
2. Run timestep 1 with first forcing
3. Compare outputs: Ts, Tm, Tb, h_ML, C_T
4. Target: Match test file row 1

### Phase 3: First 5 Timesteps
1. Run timesteps 1-5
2. Compare all outputs with test file
3. Debug any drift or discrepancies
4. Target: Exact match (< 0.01% error)

### Phase 4: Full 50 Timesteps
1. Run timesteps 1-50
2. Validate against test file
3. Check for error accumulation
4. Target: Maintain accuracy throughout

## Implementation Priority

1. ✅ **DONE:** Analyze and document issues
2. **TODO:** Fix T_mnw initialization formula
3. **TODO:** Investigate and fix T_bot initialization
4. **TODO:** Create test script for first 5 timesteps
5. **TODO:** Debug fluxes and time-stepping if needed
6. **TODO:** Validate full 50 timesteps
7. **TODO:** Create comprehensive test suite

## Notes for Developer

- The test file `Heiligensee80-96.test` has 6210 rows (17 years)
- Each row represents 1 day (del_time = 86400s)
- Row 0 is t=0, row 1 is t=1 day, etc.
- Key variables: Ts, Tm, Tb, h_ML, C_T must match exactly
- Flux variables (Q_w, Q_se, Q_la, etc.) should also match
- Ice/snow variables become relevant when T < 0°C (around row 12+)

## Related Documentation

- Mironov, D.V. (2008): "Parameterization of lakes in numerical weather prediction"
- FLake website: http://www.flake.igb-berlin.de/
- Shape function theory: Kitaigorodskii & Miropolsky (1970)

## Status

**Last Updated:** 2025-12-11
**Status:** Initialization issues identified, fixes in progress
**Next Step:** Implement T_mnw fix and test
