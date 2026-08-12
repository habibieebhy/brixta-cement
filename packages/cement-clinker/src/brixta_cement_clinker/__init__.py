from importlib.metadata import PackageNotFoundError, version

from .adapters import (
    RawMixSolutionLike,
    XrdPhaseLike,
    XrdResultLike,
    chemistry_from_raw_mix,
    estimate_from_raw_mix,
    from_xrd_result,
)
from .bogue import estimate_bogue
from .comparison import ClinkerComparison, PhaseComparison, compare_major_phases
from .model import ClinkerChemistry, ClinkerPhase, ClinkerState

try:
    __version__ = version("brixta-cement-clinker")
except PackageNotFoundError:  # source-tree import before installation
    __version__ = "0.1.0"

__all__ = [
    "ClinkerChemistry",
    "ClinkerComparison",
    "ClinkerPhase",
    "ClinkerState",
    "PhaseComparison",
    "RawMixSolutionLike",
    "XrdPhaseLike",
    "XrdResultLike",
    "__version__",
    "chemistry_from_raw_mix",
    "compare_major_phases",
    "estimate_bogue",
    "estimate_from_raw_mix",
    "from_xrd_result",
]
