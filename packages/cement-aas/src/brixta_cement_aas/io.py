from pathlib import Path

from basyx.aas.adapter import aasx
from basyx.aas.adapter.json.json_serialization import write_aas_json_file

from .pyro import ReferencePyroLine


def write_json(bundle: ReferencePyroLine, destination: str | Path) -> Path:
    """Serialize a reference pyro-line bundle to standard AAS JSON using BaSyx."""

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_aas_json_file(str(path), bundle.object_store, indent=2)
    return path


def write_aasx(bundle: ReferencePyroLine, destination: str | Path) -> Path:
    """Serialize a reference pyro-line bundle to an AASX package using BaSyx."""

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_store = aasx.DictSupplementaryFileContainer()
    with aasx.AASXWriter(str(path)) as writer:
        writer.write_aas(
            aas_ids=[bundle.aas_id],
            object_store=bundle.object_store,
            file_store=file_store,
        )
    return path