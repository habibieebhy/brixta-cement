from importlib.metadata import version

from .model import (
    MATERIAL_STATE_SCHEMA_VERSION,
    ChemicalComponent,
    ChemicalComposition,
    MaterialState,
    MeasurementRecord,
    Mineralogy,
    MineralPhase,
)
from .xrd import material_state_from_xrd

__version__ = version("brixta-cement-material")

__all__ = [
    "MATERIAL_STATE_SCHEMA_VERSION",
    "ChemicalComponent",
    "ChemicalComposition",
    "MaterialState",
    "MeasurementRecord",
    "Mineralogy",
    "MineralPhase",
    "__version__",
    "material_state_from_xrd",
]
