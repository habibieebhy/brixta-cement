import pytest

from brixta_cement_rawmix import ModulusTarget, OxideComposition, RawMaterial, RawMixProblem


def test_problem_rejects_infeasible_material_bounds() -> None:
    materials = (
        RawMaterial("A", OxideComposition(0.5, 0.1, 0.05, 0.02), min_fraction=0.7),
        RawMaterial("B", OxideComposition(0.1, 0.5, 0.15, 0.08), min_fraction=0.4),
    )
    target = ModulusTarget(target=1.0, minimum=0.9, maximum=1.1)
    with pytest.raises(ValueError, match="minimum"):
        RawMixProblem(materials=materials, lsf=target, sm=target, am=target)
