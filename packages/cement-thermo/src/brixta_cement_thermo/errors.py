class ThermoError(RuntimeError):
    """Base error for BRIXTA thermodynamic integration."""


class ThermoUnavailableError(ThermoError):
    """Raised when the external thermodynamic engine is unavailable."""


class ThermoConfigurationError(ThermoError):
    """Raised when configured thermodynamic inputs are invalid."""
