# brixta-cement-thermo

`brixta-cement-thermo` is the BRIXTA thermodynamic integration boundary.

It does **not** implement Gibbs-energy minimization, cement thermodynamics,
activity models, or thermodynamic databases. Those belong to GEMS/xGEMS,
GEMS3K, ThermoFun and cement thermodynamic datasets such as Cemdata.

## 0.1.0

The first release intentionally contains only the runtime boundary:

- discover an importable `xgems` Python module
- verify that the modern `ChemicalEngine` API is exposed
- report Python / engine metadata
- optionally validate a configured GEMS standalone chemical-system path
- `brixta-thermo doctor`

No equilibrium calculation is claimed in `0.1.0`.

This mirrors the BRIXTA XRD strategy: validate the external scientific engine
first, then add a narrow, reproducible orchestration layer once a real cement
chemical system and dataset are available.

## Environment

Optional:

```bash
export BRIXTA_GEMS_SYSTEM="/path/to/exported/gems/system"
```

The configured path may be a directory or a specific exported GEMS input file.
BRIXTA does not invent or synthesize a GEMS chemical system.

## Architecture

```text
BRIXTA raw-mix chemistry / MaterialState
              |
      brixta-cement-thermo
              |
            xGEMS
              |
            GEMS3K
              |
     ThermoFun + Cemdata
```

The official GEMS workflow requires a defined chemical system/model/database
exported for standalone use. BRIXTA therefore treats those scientific assets as
external, versioned inputs rather than embedding guessed thermodynamic data.
