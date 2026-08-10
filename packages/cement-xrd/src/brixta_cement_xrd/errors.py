class Gsas2Error(RuntimeError):
    """Base exception for BRIXTA GSAS-II integration errors."""


class Gsas2UnavailableError(Gsas2Error):
    """Raised when a usable GSAS-II runtime cannot be found."""
