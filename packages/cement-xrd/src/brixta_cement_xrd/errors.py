class Gsas2Error(RuntimeError):
    """Base exception for BRIXTA GSAS-II integration errors."""


class Gsas2UnavailableError(Gsas2Error):
    """Raised when a usable GSAS-II runtime cannot be found."""


class Gsas2InputError(Gsas2Error, ValueError):
    """Raised when an XRD analysis request or refinement recipe is invalid."""


class Gsas2AnalysisError(Gsas2Error):
    """Raised when GSAS-II fails while building or refining an XRD project."""
