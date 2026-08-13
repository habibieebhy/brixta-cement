from importlib.metadata import PackageNotFoundError, version

from .engine import GemsEngine
from .environment import GEMS_SYSTEM_ENV, ThermoEngineInfo, configured_system_path
from .errors import ThermoConfigurationError, ThermoError, ThermoUnavailableError
from .model import ThermoPhase, ThermoResult, ThermoSpecies, ThermoStateInput

try:
    __version__ = version("brixta-cement-thermo")
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = [
    "GEMS_SYSTEM_ENV",
    "GemsEngine",
    "ThermoConfigurationError",
    "ThermoEngineInfo",
    "ThermoError",
    "ThermoPhase",
    "ThermoResult",
    "ThermoSpecies",
    "ThermoStateInput",
    "ThermoUnavailableError",
    "__version__",
    "configured_system_path",
]
