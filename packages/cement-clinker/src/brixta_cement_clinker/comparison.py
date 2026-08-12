from __future__ import annotations

from dataclasses import dataclass

from .model import ClinkerState


@dataclass(frozen=True)
class PhaseComparison:
    name: str
    potential_mass_fraction: float | None
    measured_mass_fraction: float | None
    delta_measured_minus_potential: float | None


@dataclass(frozen=True)
class ClinkerComparison:
    potential_method: str
    measured_method: str
    phases: tuple[PhaseComparison, ...]


def compare_major_phases(
    potential: ClinkerState,
    measured: ClinkerState,
) -> ClinkerComparison:
    names = ("C3S", "C2S", "C3A", "C4AF")
    rows: list[PhaseComparison] = []
    for name in names:
        estimated = potential.phase_fraction(name)
        actual = measured.phase_fraction(name)
        delta = None if estimated is None or actual is None else actual - estimated
        rows.append(
            PhaseComparison(
                name=name,
                potential_mass_fraction=estimated,
                measured_mass_fraction=actual,
                delta_measured_minus_potential=delta,
            )
        )

    return ClinkerComparison(
        potential_method=potential.method,
        measured_method=measured.method,
        phases=tuple(rows),
    )
