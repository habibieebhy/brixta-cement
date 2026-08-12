from __future__ import annotations

from .model import ClinkerChemistry, ClinkerPhase, ClinkerState


def _moduli(chemistry: ClinkerChemistry) -> tuple[float, float, float]:
    c = chemistry.CaO
    s = chemistry.SiO2
    a = chemistry.Al2O3
    f = chemistry.Fe2O3

    lsf_den = 2.8 * s + 1.18 * a + 0.65 * f
    sm_den = a + f
    if lsf_den <= 0 or sm_den <= 0 or f <= 0:
        raise ValueError("CaO-SiO2-Al2O3-Fe2O3 chemistry is insufficient for clinker moduli")

    return c / lsf_den, s / sm_den, a / f


def estimate_bogue(
    chemistry: ClinkerChemistry,
    *,
    normalize: bool = True,
    sample_id: str | None = None,
) -> ClinkerState:
    """Estimate potential major clinker phases from bulk oxide chemistry.

    This is the classical four-major-phase Bogue baseline. It is a potential
    composition estimate, not direct mineralogy and not a kiln-process model.
    """

    original_total = chemistry.total
    work = chemistry.normalized() if normalize else chemistry

    c = work.CaO
    s = work.SiO2
    a = work.Al2O3
    f = work.Fe2O3

    c3s = 4.071 * c - 7.600 * s - 6.718 * a - 1.430 * f
    c2s = 2.867 * s - 0.7544 * c3s
    c3a = 2.650 * a - 1.692 * f
    c4af = 3.043 * f

    calculated = {
        "C3S": c3s,
        "C2S": c2s,
        "C3A": c3a,
        "C4AF": c4af,
    }
    outside = {name: value for name, value in calculated.items() if not 0.0 <= value <= 1.0}
    if outside:
        details = ", ".join(f"{name}={value:.6f}" for name, value in outside.items())
        raise ValueError(
            "Bogue result is outside a physical mass-fraction range; "
            f"check clinker oxide basis/composition: {details}"
        )

    warnings = [
        "Bogue values are potential major-phase estimates, not measured clinker mineralogy.",
        "Free lime, kiln liquid phase and burnability are not predicted by this baseline.",
    ]
    if normalize and abs(original_total - 1.0) > 0.005:
        warnings.append(
            f"Reported oxides summed to {original_total:.6f} and were normalized to 1.0."
        )

    lsf, sm, am = _moduli(work)
    phases = tuple(
        ClinkerPhase(name=name, mass_fraction=value, source="bogue-potential")
        for name, value in calculated.items()
    )

    return ClinkerState(
        method="bogue-potential",
        sample_id=sample_id,
        chemistry=work,
        phases=phases,
        lsf=lsf,
        sm=sm,
        am=am,
        warnings=tuple(warnings),
        provenance={"calculation": "classical-four-phase-bogue"},
    )
