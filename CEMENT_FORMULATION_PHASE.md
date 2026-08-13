# Cement Intelligence — formulation slice

## Scope closed by `brixta-cement-formulation 0.1.0`

```text
ClinkerState
+ gypsum / anhydrite / hemihydrate
+ limestone
+ fly ash
+ GGBS
+ calcined clay
+ natural pozzolan / silica fume / other SCM
        ↓
CementRecipe
        ↓
strict mass balance
        ↓
CementState
```

`CementState` exposes clinker factor, SCM factor, sulfate-carrier factor, limestone
factor, final-cement known bulk chemistry, chemistry coverage, component/sample
provenance, and warnings for incomplete chemistry.

## Integration boundaries

`ClinkerState` and `MaterialState` are consumed through structural adapters. The
formulation package does not duplicate clinker science or material measurement models.

The package deliberately does not encode regulatory composition limits for named cement
standards. Those limits vary by jurisdiction/standard/version and belong in a separate
validation layer.

## Not yet claimed

This release does not predict hydration, strength, setting time, durability, grinding
response, sulfate optimisation, or standard compliance.

## Next Cement Intelligence slice

```text
CementState
+ water/cement ratio
+ temperature
+ age / reaction state
        ↓
brixta-cement-thermo 0.2
        ↓
xGEMS / GEMS3K / CemGEMS
        ↓
normalized hydration / equilibrium result
```

Then move into Factory Intelligence.
