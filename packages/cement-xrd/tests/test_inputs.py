import json

import pytest

from brixta_cement_xrd import PhaseModel, RefinementRecipe, XrdAnalysisInput
from brixta_cement_xrd.errors import Gsas2InputError


def _request(tmp_path) -> XrdAnalysisInput:
    pattern = tmp_path / "sample.xy"
    instrument = tmp_path / "instrument.instprm"
    alite = tmp_path / "alite.cif"
    pattern.write_text("pattern", encoding="utf-8")
    instrument.write_text("instrument", encoding="utf-8")
    alite.write_text("cif", encoding="utf-8")
    return XrdAnalysisInput(
        sample_id="clinker-001",
        pattern_path=pattern,
        instrument_path=instrument,
        phases=(PhaseModel("Alite", alite),),
        output_dir=tmp_path / "runs",
    )


def test_analysis_input_resolves_files(tmp_path) -> None:
    validated = _request(tmp_path).validate()

    assert validated.pattern_path.is_absolute()
    assert validated.phases[0].name == "Alite"


def test_analysis_input_rejects_duplicate_phase_names(tmp_path) -> None:
    request = _request(tmp_path)
    duplicate = XrdAnalysisInput(
        sample_id=request.sample_id,
        pattern_path=request.pattern_path,
        instrument_path=request.instrument_path,
        phases=(request.phases[0], request.phases[0]),
        output_dir=request.output_dir,
    )

    with pytest.raises(Gsas2InputError, match="unique"):
        duplicate.validate()


def test_recipe_requires_phase_fraction_refinement() -> None:
    with pytest.raises(Gsas2InputError, match="PhaseFraction or Scale"):
        RefinementRecipe(name="bad", version="1", steps=({"set": {"Cell": True}},))


def test_recipe_rejects_final_refinement_without_phase_fraction() -> None:
    with pytest.raises(Gsas2InputError, match="PhaseFraction or Scale"):
        RefinementRecipe(
            name="bad-final-step",
            version="1",
            steps=(
                {"set": {"PhaseFraction": True}},
                {"clear": {"PhaseFraction": True}, "set": {"Cell": True}},
            ),
        )


def test_recipe_rejects_executable_hook() -> None:
    with pytest.raises(Gsas2InputError, match="forbidden"):
        RefinementRecipe(
            name="bad",
            version="1",
            steps=({"set": {"PhaseFraction": True}, "call": "evil"},),
        )


def test_recipe_loads_from_json(tmp_path) -> None:
    recipe_path = tmp_path / "recipe.json"
    recipe_path.write_text(
        json.dumps(
            {
                "name": "clinker",
                "version": "1",
                "steps": [{"set": {"PhaseFraction": True}}],
            }
        ),
        encoding="utf-8",
    )

    recipe = RefinementRecipe.from_json(recipe_path)

    assert recipe.name == "clinker"
    assert recipe.refines_phase_fractions() is True
