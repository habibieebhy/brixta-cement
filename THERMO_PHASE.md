# BRIXTA Thermodynamics Integration Phase

## Why this comes before Clinker Intelligence

Clinker chemistry/phase prediction is exactly where BRIXTA should **not**
reimplement generic thermodynamic science.

The external scientific stack is:

```text
GEM-Selektor / cement chemical-system definition
            |
          xGEMS
            |
          GEMS3K
            |
       ThermoFun / Cemdata
```

BRIXTA's responsibility is the adapter contract, normalized inputs/results,
provenance and later orchestration from RawMix/MaterialState.

## 0.1.0

`brixta-cement-thermo` 0.1.0 validates the runtime boundary only.

## 0.2.0 target

Once a real cement GEMS system is available:

```text
RawMixSolution / MaterialState chemistry
              |
      BRIXTA mapping
              |
      xGEMS ChemicalEngine
              |
      equilibrium result
              |
 phases / activities / state / provenance
```

No thermodynamic values should be fabricated to make the integration pass.
