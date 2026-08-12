# brixta-cement-clinker

BRIXTA's cement-specific clinker contract layer.

Version 0.1 intentionally closes the **first usable clinker slice** without pretending
that a high-temperature kiln model already exists.

It provides:

- normalized clinker oxide chemistry;
- LSF / SM / AM descriptors;
- Bogue **potential** C3S / C2S / C3A / C4AF estimates;
- structural adapter from `RawMixSolution`;
- structural adapter from `XrdResult` / Rietveld phase fractions;
- potential-vs-measured major-phase comparison;
- explicit placeholders for free lime, liquid phase and burnability that remain `None`
  until backed by a validated model or measurement.

## Scientific boundary

Bogue values are potential phase estimates from bulk chemistry. They are not direct
mineralogical measurements and are not a kiln-equilibrium, kinetics, burnability,
free-lime or cooling model.

For measured clinker mineralogy use quantitative XRD/Rietveld through
`brixta-cement-xrd`.

The currently integrated CemGEMS hydration system is not used here as a kiln model.

## Example: chemistry -> potential clinker

```python
from brixta_cement_clinker import ClinkerChemistry, estimate_bogue

chemistry = ClinkerChemistry(
    CaO=0.650,
    SiO2=0.215,
    Al2O3=0.052,
    Fe2O3=0.032,
    MgO=0.015,
    SO3=0.008,
)

state = estimate_bogue(chemistry)

print(state.method)
print(state.phase_fraction("C3S"))
```

## Example: RawMixSolution -> potential clinker

The adapter is structural: `brixta-cement-clinker` does not need a runtime dependency
on `brixta-cement-rawmix`.

```python
from brixta_cement_clinker import estimate_from_raw_mix

state = estimate_from_raw_mix(raw_mix_solution)
```

The represented raw-mix oxides are normalized to a clinker oxide basis. This is a
composition bridge only: it does not model CO2 release, alkali/sulfur volatilization,
dust cycles or kiln reactions.

## Example: XRD result -> measured clinker state

```python
from brixta_cement_clinker import from_xrd_result

measured = from_xrd_result(xrd_result)
```

## Next scientific upgrade

The `ClinkerState` contract is the stable boundary. A later validated high-temperature
backend can populate:

- `free_lime_mass_fraction`
- `liquid_phase_mass_fraction`
- `burnability_index`

without changing downstream Cement Intelligence.
