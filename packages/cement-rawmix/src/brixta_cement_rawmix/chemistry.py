from __future__ import annotations

from collections.abc import Mapping


def lime_saturation_factor(oxides: Mapping[str, float]) -> float:
    denominator = 2.8 * oxides["SiO2"] + 1.18 * oxides["Al2O3"] + 0.65 * oxides["Fe2O3"]
    if denominator <= 0:
        raise ValueError("LSF denominator must be positive")
    return oxides["CaO"] / denominator


def silica_modulus(oxides: Mapping[str, float]) -> float:
    denominator = oxides["Al2O3"] + oxides["Fe2O3"]
    if denominator <= 0:
        raise ValueError("SM denominator must be positive")
    return oxides["SiO2"] / denominator


def alumina_modulus(oxides: Mapping[str, float]) -> float:
    denominator = oxides["Fe2O3"]
    if denominator <= 0:
        raise ValueError("AM denominator must be positive")
    return oxides["Al2O3"] / denominator
