# BRIXTA Raw Mix Intelligence — Phase 2A

## Ownership boundary

```text
Raw-material chemistry / bounds / cement targets
                  |
                  v
        brixta-cement-rawmix
                  |
                  v
                Pyomo
                  |
                  v
                HiGHS
                  |
                  v
          RawMixSolution
```

BRIXTA owns the cement-domain problem definition and normalized result.
Pyomo owns the algebraic modeling layer. HiGHS owns optimization.

## 0.1.0 scope

- raw-material oxide tables
- material fraction bounds
- LSF / SM / AM bounds and targets
- oxide bounds
- optional material cost objective contribution
- normalized solver result and provenance

## Deferred

- XRF ingestion
- quarry uncertainty / robust optimization
- stochastic blending
- clinker burnability model
- kiln feedback
- online feeder control

Those are later phases and should not be invented inside this package.
