# FLake Model - Modular Structure

This directory contains the FLake model reorganized into modules following the original Fortran structure.

## Module Organization

The FLake model is organized into **9 core modules** following the Fortran dependency hierarchy:

### Base Layer (Infrastructure)

#### 1. **data_parameters** (`01_data_parameters.ipynb`)
- **Role:** Root module - defines precision kinds and global constants
- **Uses:** None (base module)
- **Defines:** `ireals` (float64), `iintegers` (int32)
- **Used by:** All other modules

### Parameter/Type Layer

#### 2. **flake_derivedtypes** (`02_flake_derivedtypes.ipynb`)
- **Role:** Defines data structures for FLake
- **Uses:** `data_parameters`
- **Defines:** `nband_optic_max`, `OpticparMedium` dataclass
- **Used by:** `flake_paramoptic_ref`, `flake_core`, `flake_interface`

#### 3. **flake_parameters** (`03_flake_parameters.ipynb`)
- **Role:** Empirical and thermodynamic constants
- **Uses:** `data_parameters`
- **Defines:**
  - Mixed-layer depth constants: `c_cbl_1`, `c_cbl_2`, `c_sbl_ZM_*`, `c_relax_*`
  - Shape function parameters: `C_T_min`, `C_T_max`, `C_B1`, `C_B2`, etc.
  - Security constants: `h_Snow_min_flk`, `h_Ice_min_flk`, `h_ML_min_flk`, etc.
  - Thermodynamic parameters: `tpl_grav`, `tpl_T_r`, `tpl_T_f`, densities, specific heats
- **Used by:** `flake_core`, `SfcFlx`

#### 4. **flake_configure** (`04_flake_configure.ipynb`)
- **Role:** Configuration flags for FLake physics options
- **Uses:** `data_parameters`
- **Defines:** `lflk_botsed_use` (bottom sediment scheme flag)
- **Used by:** `flake_driver`

#### 5. **flake_albedo_ref** (`05_flake_albedo_ref.ipynb`)
- **Role:** Reference albedo values for lake surfaces
- **Uses:** `data_parameters`
- **Defines:** Albedos for open water, ice, snow
- **Used by:** `flake_interface`

#### 6. **flake_paramoptic_ref** (`06_flake_paramoptic_ref.ipynb`)
- **Role:** Reference optical parameter sets
- **Uses:** `data_parameters`, `flake_derivedtypes`
- **Defines:** `OpticparMedium` instances for water, ice, snow
- **Used by:** `flake_interface`

### Physics Layer

#### 7. **SfcFlx** (`07_SfcFlx.ipynb`)
- **Role:** Atmospheric surface-layer parameterization for fluxes
- **Uses:** `data_parameters`, `flake_parameters`
- **Defines:**
  - `SfcFlx_lwradatm()` - Downward longwave radiation
  - `SfcFlx_lwradwsfc()` - Upward longwave radiation
  - `SfcFlx_momsenlat()` - Momentum, sensible, and latent heat fluxes
  - `SfcFlx_rhoair()` - Air density
  - `SfcFlx_roughness()` - Aerodynamic roughness lengths
  - `SfcFlx_satwvpres()` - Saturation vapor pressure
  - `SfcFlx_spechum()` - Specific humidity
  - `SfcFlx_wvpreswetbulb()` - Vapor pressure from wet/dry bulb temps
- **Used by:** `flake_interface`

#### 8. **flake_core** (`08_flake_core.ipynb`)
- **Role:** Core FLake model physics and state variables
- **Uses:** `data_parameters`, `flake_parameters`, `flake_configure`
- **State variables:** `T_snow_*_flk`, `T_ice_*_flk`, `T_mnw_*_flk`, `T_wML_*_flk`, `T_bot_*_flk`, `T_B1_*_flk`, `C_T_*_flk`, `h_snow_*_flk`, `h_ice_*_flk`, `h_ML_*_flk`, `H_B1_*_flk`
- **Flux variables:** `Q_snow_flk`, `Q_ice_flk`, `Q_w_flk`, `Q_bot_flk`, `I_*_flk`
- **Functions:**
  - `flake_driver()` - Main time-stepping driver
  - `flake_radflux()` - Shortwave radiation fluxes
  - `flake_buoypar()` - Buoyancy parameter
  - `flake_snowdensity()` - Snow density function
  - `flake_snowheatconduct()` - Snow thermal conductivity
- **Used by:** `flake_interface`

### Interface Layer

#### 9. **flake_interface** (`09_flake_interface.ipynb`)
- **Role:** Main interface connecting external forcing to FLake core
- **Uses:** All other modules
- **Defines:** `flake_interface()` - High-level driver function
- **This is the main entry point for running FLake**

## Dependency Diagram

```
                    flake_interface
               /      |      |      \
           flake_core  SfcFlx  ...  ref modules
             |           |
       flake_parameters, flake_derivedtypes, flake_configure
             \          /
            data_parameters
```

## Module Files

| # | Module | File | Status |
|---|--------|------|--------|
| 1 | data_parameters | `01_data_parameters.ipynb` | ✅ Complete |
| 2 | flake_derivedtypes | `02_flake_derivedtypes.ipynb` | ✅ Complete |
| 3 | flake_parameters | `03_flake_parameters.ipynb` | ✅ Complete |
| 4 | flake_configure | `04_flake_configure.ipynb` | ⏳ Pending |
| 5 | flake_albedo_ref | `05_flake_albedo_ref.ipynb` | ⏳ Pending |
| 6 | flake_paramoptic_ref | `06_flake_paramoptic_ref.ipynb` | ⏳ Pending |
| 7 | SfcFlx | `07_SfcFlx.ipynb` | ⏳ Pending |
| 8 | flake_core | `08_flake_core.ipynb` | ⏳ Pending |
| 9 | flake_interface | `09_flake_interface.ipynb` | ⏳ Pending |

## How to Use

### Option 1: Run Individual Modules

Each notebook can be run independently for testing:

```bash
jupyter notebook 01_data_parameters.ipynb
```

### Option 2: Import as Python Modules

Convert notebooks to `.py` files and import:

```bash
jupyter nbconvert --to python *.ipynb
```

Then in your code:
```python
from data_parameters import ireals, iintegers
from flake_parameters import *
from flake_interface import flake_interface
```

### Option 3: Run Full FLake Model

Use the main interface module:

```python
# Import the interface
from flake_interface import flake_interface

# Call with forcing data
result = flake_interface(
    dMsnowdt_in, I_atm_in, Q_atm_lw_in,
    height_u_in, height_tq_in,
    U_a_in, T_a_in, q_a_in, P_a_in,
    depth_w, fetch, depth_bs, T_bs, par_Coriolis, del_time,
    T_snow_in, T_ice_in, T_mnw_in, T_wML_in, T_bot_in, T_B1_in,
    C_T_in, h_snow_in, h_ice_in, h_ML_in, H_B1_in,
    T_sfc_p,
    albedo_water, albedo_ice, albedo_snow,
    opticpar_water, opticpar_ice, opticpar_snow
)
```

## Development Status

**Current Status:** ✅ **Infrastructure modules complete (3/9)**

**Next Steps:**
1. Complete reference parameter modules (04-06)
2. Implement physics modules (07-08)
3. Create interface module (09)
4. Test complete modular system
5. Validate against Fortran reference

## Benefits of Modular Structure

1. **Maintainability:** Each module has a single, well-defined purpose
2. **Testability:** Individual modules can be tested independently
3. **Documentation:** Each notebook includes detailed documentation
4. **Debugging:** Easier to trace bugs to specific modules
5. **Reusability:** Modules can be used in other projects
6. **Fortran Compatibility:** 1:1 mapping to original Fortran structure

## Original Source Files

This modular structure is based on the original Fortran code:

- `data_parameters.f90`
- `flake_derivedtypes.f90`
- `flake_parameters.f90`
- `flake_configure.f90`
- `flake_albedo_ref.f90`
- `flake_paramoptic_ref.f90`
- `SfcFlx.f90` + `.incf` files
- `flake.f90` + `.incf` files
- `src_flake_interface_1D.f90`

## References

- Mironov, D.V. (2008): Parameterization of lakes in numerical weather prediction. Description of a lake model. *COSMO Technical Report*, No. 11.
- FLake documentation: http://www.flake.igb-berlin.de/
