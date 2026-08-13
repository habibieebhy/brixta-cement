from __future__ import annotations

from .model import CementRecipe, CementState, ComponentChemistry


def formulate_cement(recipe: CementRecipe) -> CementState:
    "Apply recipe mass balance and propagate known chemistry to final cement basis."

    clinker_factor = sum(
        component.mass_fraction
        for component in recipe.components
        if component.kind.is_clinker
    )
    scm_factor = sum(
        component.mass_fraction
        for component in recipe.components
        if component.kind.is_scm
    )
    sulfate_carrier_factor = sum(
        component.mass_fraction
        for component in recipe.components
        if component.kind.is_sulfate_carrier
    )
    limestone_factor = sum(
        component.mass_fraction
        for component in recipe.components
        if component.kind.is_limestone
    )

    chemistry_components = [
        component for component in recipe.components if component.chemistry is not None
    ]
    chemistry_coverage = sum(
        component.mass_fraction for component in chemistry_components
    )

    bulk_chemistry: ComponentChemistry | None = None
    if chemistry_components:
        names: dict[str, str] = {}
        for component in chemistry_components:
            assert component.chemistry is not None
            for name in component.chemistry.components:
                names.setdefault(name.casefold(), name)

        values = {
            canonical_name: sum(
                component.mass_fraction * component.chemistry.get(canonical_name)
                for component in chemistry_components
                if component.chemistry is not None
            )
            for canonical_name in names.values()
        }
        bulk_chemistry = ComponentChemistry(
            components=values,
            basis="final-cement-known-contribution",
        )

    warnings: list[str] = []
    if chemistry_coverage < 1.0 - 1e-8:
        warnings.append(
            "Bulk chemistry is partial: chemistry is unavailable for "
            f"{1.0 - chemistry_coverage:.6f} of final cement mass."
        )
    if clinker_factor == 0.0:
        warnings.append("Recipe contains no component classified as clinker.")

    return CementState(
        recipe_id=recipe.recipe_id,
        cement_family=recipe.cement_family,
        components=recipe.components,
        clinker_factor=clinker_factor,
        scm_factor=scm_factor,
        sulfate_carrier_factor=sulfate_carrier_factor,
        limestone_factor=limestone_factor,
        chemistry_coverage_mass_fraction=chemistry_coverage,
        bulk_chemistry=bulk_chemistry,
        warnings=tuple(warnings),
        provenance={"calculation": "cement-recipe-mass-balance-v1"},
    )
