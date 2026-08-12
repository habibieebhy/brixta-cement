# brixta-cement-material

`brixta-cement-material` defines the BRIXTA-owned, engine-neutral material state
used to move observed cement-material data between scientific integrations and
the Cement Twin.

It does **not** implement XRD, XRF, thermodynamics, or other scientific
calculations. Those remain owned by upstream scientific engines and their
BRIXTA adapters.

## Scope of 0.1.0

The first release provides:

- `MaterialState`
- optional `ChemicalComposition`
- optional `Mineralogy`
- generic `MeasurementRecord` provenance
- JSON serialization
- structural XRD-result adapter `material_state_from_xrd(...)`

A material state is deliberately partially observable. Chemistry is not
required, so an XRD-derived clinker state is valid even when XRF is unavailable.

```python
from brixta_cement_material import material_state_from_xrd

state = material_state_from_xrd(
    xrd_result,
    material_type="clinker",
)

assert state.chemistry is None
assert state.mineralogy is not None
```

The XRD adapter uses a structural protocol rather than depending on
`brixta-cement-xrd` at runtime. `brixta-cement-xrd` continues to own GSAS-II
orchestration; this package owns only the normalized BRIXTA material-domain
representation.

## Integration boundary

```text
GSAS-II
   |
brixta-cement-xrd
   |
XrdResult
   |
brixta-cement-material
   |
MaterialState
   |
brixta-cement-aas
   |
BaSyx / AAS
```

Chemistry can be added later from quantified XRF/oxide data without changing
the mineralogy contract.

## Status

Experimental alpha. Public contracts may evolve before 1.0.
