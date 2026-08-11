from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType
from typing import Any, ClassVar

from brixta_cement_xrd import EngineInfo, PhaseModel, RefinementRecipe, XrdAnalysisInput
from brixta_cement_xrd.analysis import run_quantitative_analysis


class FakeHistogram:
    residuals: ClassVar[dict[str, object]] = {
        "wR": 7.5,
        "R": 4.0,
        "text": "ignored",
    }

    def ComputeMassFracs(self) -> dict[str, tuple[float, float]]:
        return {
            "Alite": (0.62, 0.01),
            "Belite": (0.38, 0.02),
        }


class FakeProject:
    last: ClassVar[FakeProject | None] = None

    def __init__(self, newgpx: str) -> None:
        self.newgpx = newgpx
        self.histogram = FakeHistogram()
        self.phases: list[tuple[str, str, list[FakeHistogram], str | None]] = []
        self.refinement_steps: list[dict[str, Any]] | None = None
        self.datafile: str | None = None
        self.iparams: str | None = None
        self.histogram_kwargs: dict[str, Any] = {}
        FakeProject.last = self

    def add_powder_histogram(
        self,
        datafile: str,
        iparams: str,
        **kwargs: Any,
    ) -> FakeHistogram:
        self.datafile = datafile
        self.iparams = iparams
        self.histogram_kwargs = kwargs
        return self.histogram

    def add_phase(
        self,
        phasefile: str,
        phasename: str,
        histograms: list[FakeHistogram],
        fmthint: str | None,
    ) -> None:
        self.phases.append((phasefile, phasename, histograms, fmthint))

    def save(self) -> None:
        Path(self.newgpx).touch()

    def do_refinements(self, steps: list[dict[str, Any]]) -> None:
        self.refinement_steps = steps


class FakeScriptable(ModuleType):
    """Typed fake for the GSASII.GSASIIscriptable module."""

    G2Project = FakeProject


def _engine_info() -> EngineInfo:
    return EngineInfo(
        engine="GSAS-II",
        engine_version="v5.7.9",
        adapter_version="0.2.0",
        source_path="/opt/gsas2/GSASII",
        binary_path="/opt/gsas2/GSASII-bin/test",
        python_version="3.13.7",
        numpy_version="2.2.6",
    )


def test_quantitative_analysis_builds_project_and_normalizes_result(
    tmp_path: Path,
) -> None:
    pattern = tmp_path / "sample.xy"
    instrument = tmp_path / "instrument.instprm"
    alite = tmp_path / "alite.cif"
    belite = tmp_path / "belite.cif"

    for path, value in [
        (pattern, "pattern"),
        (instrument, "instrument"),
        (alite, "alite"),
        (belite, "belite"),
    ]:
        path.write_text(value, encoding="utf-8")

    request = XrdAnalysisInput(
        sample_id="clinker 001",
        pattern_path=pattern,
        instrument_path=instrument,
        phases=(
            PhaseModel("Alite", alite),
            PhaseModel("Belite", belite),
        ),
        output_dir=tmp_path / "runs",
    )
    recipe = RefinementRecipe.minimal_phase_fraction()
    scriptable = FakeScriptable("fake_gsas2_scriptable")

    result = run_quantitative_analysis(
        scriptable=scriptable,
        engine_info=_engine_info(),
        request=request,
        recipe=recipe,
    )

    assert [phase.name for phase in result.phases] == ["Alite", "Belite"]
    assert result.phases[0].mass_fraction == 0.62
    assert result.residuals == {"wR": 7.5, "R": 4.0}
    assert result.input_sha256["phase:Alite"]
    assert result.recipe_sha256
    assert result.warnings == ()

    project = FakeProject.last
    assert project is not None
    assert project.refinement_steps == [{"set": {"PhaseFraction": True}}]

    payload = json.loads(
        Path(result.artifacts["result_json"]).read_text(encoding="utf-8")
    )
    assert payload["sample_id"] == "clinker 001"
    assert payload["phases"][0]["name"] == "Alite"