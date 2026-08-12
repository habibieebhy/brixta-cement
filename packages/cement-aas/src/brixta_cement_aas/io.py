from pathlib import Path
from typing import Protocol

from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.adapter.json.json_serialization import write_aas_json_file


class AasBundle(Protocol):
    """Minimal BRIXTA bundle contract accepted by the serialization helpers."""

    object_store: model.DictIdentifiableStore
    aas_id: str


def write_json(bundle: AasBundle, destination: str | Path) -> Path:
    """Serialize a BRIXTA AAS bundle to standard AAS JSON using BaSyx."""

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_aas_json_file(str(path), bundle.object_store, indent=2)
    return path


def write_aasx(bundle: AasBundle, destination: str | Path) -> Path:
    """Serialize a BRIXTA AAS bundle to an AASX package using BaSyx."""

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
