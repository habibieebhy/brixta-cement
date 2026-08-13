# brixta-cement-thermo

BRIXTA integration boundary around the external xGEMS/GEMS3K thermodynamic runtime.

## v0.2

```text
ThermoStateInput
    -> GemsEngine.equilibrate()
    -> xGEMS ChemicalEngine
    -> GEMS3K
    -> ThermoResult
```

The result normalizes phase amounts/masses/volumes/densities/saturation indices,
species amounts and phase membership, pH, pe, Eh, ionic strength, system properties,
convergence diagnostics, and system provenance.

BRIXTA does not implement Gibbs-energy minimization.

## Real runtime

```bash
mamba activate xgems
cd ~/Projects/brixta-cement
python -m pip install -e "packages/cement-thermo"
export BRIXTA_GEMS_SYSTEM="$HOME/xgems/demos/resources/CemGEMS-keyvalue/CemHyds-dat.lst"
```

```python
from brixta_cement_thermo import GemsEngine, ThermoStateInput

engine = GemsEngine(adapter_version="0.2.0")
result = engine.equilibrate(ThermoStateInput())

print(result.ph)
print(result.phase("CSHQ"))
```

With an explicit independent-element inventory, unspecified elements are zeroed by
default. Set `preserve_unspecified_elements=True` only when intentional.

The configured `CemHyds` system is hydration/aqueous thermodynamics, not a
high-temperature clinker-burning model.
