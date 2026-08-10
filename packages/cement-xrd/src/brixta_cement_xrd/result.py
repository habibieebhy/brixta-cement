from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EngineInfo:
    """Normalized metadata for a usable GSAS-II runtime."""

    engine: str
    engine_version: str
    adapter_version: str
    source_path: str
    binary_path: str
    python_version: str
    numpy_version: str

    def to_dict(self) -> dict[str, str]:
        """Return JSON-friendly engine metadata."""

        return asdict(self)
