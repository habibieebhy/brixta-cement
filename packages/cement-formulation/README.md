# brixta-cement-formulation

BRIXTA's cement formulation and mass-balance contract layer.

Version 0.1 provides a product-neutral representation for composing cement from:

- clinker;
- gypsum;
- anhydrite;
- hemihydrate;
- limestone;
- fly ash;
- GGBS/slag;
- calcined clay;
- natural pozzolan;
- silica fume;
- other SCMs/additions.

It calculates exact recipe mass balance, clinker factor, SCM factor,
sulfate-carrier factor, limestone factor, known bulk chemistry on the final-cement
mass basis, chemistry coverage, and component/sample provenance.

It deliberately does **not** impose OPC/PPC/PSC/LC3 regulatory percentage limits.
Those limits depend on the applicable product standard and belong in a later
standards/validation layer.

## Example

```python
from brixta_cement_formulation import (
    CementComponent,
    CementComponentKind,
    CementRecipe,
    ComponentChemistry,
    formulate_cement,
)

recipe = CementRecipe(
    recipe_id="opc-demo",
    cement_family="OPC",
    components=(
        CementComponent(
            name="clinker",
            kind=CementComponentKind.CLINKER,
            mass_fraction=0.95,
            chemistry=ComponentChemistry(
                {"CaO": 0.65, "SiO2": 0.215, "Al2O3": 0.052, "Fe2O3": 0.032}
            ),
        ),
        CementComponent(
            name="gypsum",
            kind=CementComponentKind.GYPSUM,
            mass_fraction=0.05,
            chemistry=ComponentChemistry({"CaO": 0.326, "SO3": 0.465}),
        ),
    ),
)

state = formulate_cement(recipe)
print(state.clinker_factor)
print(state.sulfate_carrier_factor)
print(state.bulk_component_fraction("SO3"))
```

## Structural adapters

The package consumes `ClinkerState` and `MaterialState` through structural typing,
so it does not duplicate clinker science or material measurement models.

## Scientific boundary

This package performs formulation bookkeeping and composition propagation. It does not
predict hydration, strength, setting, durability, grinding performance, or compliance
with a named cement standard.

The next Cement Intelligence slice is:

```text
CementState
+ water/cement ratio
+ temperature / curing state
    -> brixta-cement-thermo
    -> xGEMS / GEMS3K / CemGEMS
    -> normalized hydration result
```
