# brixta-cement-aas

`brixta-cement-aas` provides BRIXTA-owned cement compositions on top of the
Eclipse BaSyx / Asset Administration Shell ecosystem.

The package does not replace the AAS metamodel or BaSyx runtime.

## 0.2.0

Version `0.2.0` adds the Material Intelligence bridge:

```text
MaterialState
    |
build_material_state_submodel(...)
    |
BaSyx Submodel
```

It also provides `build_material_sample_aas(...)` for a standalone AAS
representing an observed material sample or batch.

Chemistry and mineralogy are independent. If XRF chemistry is unavailable,
the AAS explicitly records `ChemistryStatus = "unavailable"` while preserving
available XRD mineralogy and its measurement provenance.

```python
from brixta_cement_aas import build_material_sample_aas
from brixta_cement_material import material_state_from_xrd

state = material_state_from_xrd(xrd_result, material_type="clinker")
bundle = build_material_sample_aas(state)
```

The generated Material State submodel is a BRIXTA composition, not a claim of
conformance to an IDTA cement-specific submodel template.

## Existing reference topology

The package continues to provide the reference precalciner pyro-line topology:

```text
PyroLine
├── Preheater
│   ├── Cyclone01
│   ├── Cyclone02
│   ├── Cyclone03
│   └── Cyclone04
├── Precalciner
├── RotaryKiln
└── ClinkerCooler
```

The topology does not embed homemade kiln physics. External process models
remain external.

## Architecture principle

Integrate first. Compose second. Invent last.

BRIXTA owns cement-domain composition, mapping and orchestration. BaSyx owns
the generic AAS implementation.
