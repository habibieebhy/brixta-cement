from importlib.metadata import version

from .chemistry import alumina_modulus, lime_saturation_factor, silica_modulus
from .model import (
    ModulusTarget,
    OxideComposition,
    OxideTarget,
    RawMaterial,
    RawMixProblem,
    RawMixSolution,
)
from .optimizer import BuiltRawMixModel, build_pyomo_model, solve_raw_mix

__version__ = version("brixta-cement-rawmix")

__all__ = [
    "BuiltRawMixModel", "ModulusTarget", "OxideComposition", "OxideTarget",
    "RawMaterial", "RawMixProblem", "RawMixSolution", "__version__",
    "alumina_modulus", "build_pyomo_model", "lime_saturation_factor",
    "silica_modulus", "solve_raw_mix",
]
