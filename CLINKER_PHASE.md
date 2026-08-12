# Clinker Intelligence — first executable slice

## Scope closed by `brixta-cement-clinker 0.1.0`

```text
RawMixSolution
    -> represented oxide normalization
    -> Bogue potential major phases
    -> ClinkerState

XrdResult
    -> measured Rietveld phase fractions
    -> ClinkerState

potential ClinkerState + measured ClinkerState
    -> phase comparison
```

## Scientific boundary

This release deliberately does **not** claim to solve the kiln.

Not yet calculated:

- kiln reaction kinetics
- high-temperature phase equilibrium
- melt/liquid fraction
- free-lime prediction
- residence-time effects
- volatilization / internal cycles
- cooling-rate effects
- polymorph stabilization

Those fields remain absent/`None` unless measured or supplied by a later validated backend.

This is enough to move BRIXTA downstream because Cement Intelligence now has a stable
`ClinkerState` contract and can consume either a potential chemistry-derived clinker or
a measured XRD-derived clinker.

## Next

Move directly to Cement Intelligence:

```text
ClinkerState
+ gypsum
+ limestone
+ SCMs
    -> CementState
    -> hydration request
    -> brixta-cement-thermo / xGEMS / CemGEMS
```
