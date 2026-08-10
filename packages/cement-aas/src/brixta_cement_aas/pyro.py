from dataclasses import dataclass
from urllib.parse import quote

from basyx.aas import model


@dataclass(frozen=True)
class ReferencePyroLine:
    object_store: model.DictIdentifiableStore
    aas: model.AssetAdministrationShell
    topology: model.Submodel
    aas_id: str
    topology_id: str


def _id_segment(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be blank")
    return quote(cleaned, safe="-._~")


def _equipment(
    id_short: str,
    children: set[model.SubmodelElement] | None = None,
) -> model.SubmodelElementCollection:
    return model.SubmodelElementCollection(id_short=id_short, value=children or set())


def build_reference_pyro_line(
    plant_id: str,
    line_id: str,
    *,
    namespace: str = "https://brixta.org/aas",
) -> ReferencePyroLine:
    plant_segment = _id_segment(plant_id, "plant_id")
    line_segment = _id_segment(line_id, "line_id")
    base = namespace.rstrip("/")
    if not base:
        raise ValueError("namespace must not be blank")

    asset_id = f"{base}/assets/{plant_segment}/{line_segment}"
    aas_id = f"{base}/shells/{plant_segment}/{line_segment}"
    topology_id = f"{base}/submodels/{plant_segment}/{line_segment}/process-topology"

    preheater = _equipment(
        "Preheater",
        {
            _equipment("Cyclone01"),
            _equipment("Cyclone02"),
            _equipment("Cyclone03"),
            _equipment("Cyclone04"),
        },
    )

    topology = model.Submodel(
        id_=topology_id,
        id_short="ProcessTopology",
        submodel_element={
            model.Property(id_short="PlantId", value_type=model.datatypes.String, value=plant_id),
            model.Property(id_short="LineId", value_type=model.datatypes.String, value=line_id),
            model.Property(
                id_short="ModelStatus",
                value_type=model.datatypes.String,
                value="topology_only_external_process_model_required",
            ),
            preheater,
            _equipment("Precalciner"),
            _equipment("RotaryKiln"),
            _equipment("ClinkerCooler"),
        },
    )

    aas = model.AssetAdministrationShell(
        id_=aas_id,
        id_short="PyroLine",
        asset_information=model.AssetInformation(
            asset_kind=model.AssetKind.INSTANCE,
            global_asset_id=asset_id,
        ),
        submodel={model.ModelReference.from_referable(topology)},
    )

    store: model.DictIdentifiableStore[model.Identifiable] = model.DictIdentifiableStore()
    store.add(topology)
    store.add(aas)

    return ReferencePyroLine(
        object_store=store,
        aas=aas,
        topology=topology,
        aas_id=aas_id,
        topology_id=topology_id,
    )
