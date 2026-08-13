from importlib.metadata import PackageNotFoundError, version

from .adapters import (
    ClinkerChemistryLike,
    ClinkerStateLike,
    MaterialStateLike,
    component_from_clinker_state,
    component_from_material_state,
)
from .formulation import formulate_cement
from .model import (
    CementComponent,
    CementComponentKind,
    CementRecipe,
    CementState,
    ComponentChemistry,
)

try:
    __version__ = version("brixta-cement-formulation")
except PackageNotFoundError:  # source-tree import before installation
    __version__ = "0.1.0"

__all__ = [
    "CementComponent",
    "CementComponentKind",
    "CementRecipe",
    "CementState",
    "ClinkerChemistryLike",
    "ClinkerStateLike",
    "ComponentChemistry",
    "MaterialStateLike",
    "__version__",
    "component_from_clinker_state",
    "component_from_material_state",
    "formulate_cement",
]
