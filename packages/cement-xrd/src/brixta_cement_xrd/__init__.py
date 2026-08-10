from importlib.metadata import version

from .engine import Gsas2Engine
from .errors import Gsas2Error, Gsas2UnavailableError
from .result import EngineInfo

__version__ = version("brixta-cement-xrd")

__all__ = [
    "EngineInfo",
    "Gsas2Engine",
    "Gsas2Error",
    "Gsas2UnavailableError",
    "__version__",
]
