from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from urllib.parse import quote

from basyx.aas import model
from brixta_cement_material import (
    ChemicalComposition,
    MaterialState,
    MeasurementRecord,
    Mineralogy,
)


@dataclass(frozen=True)
class MaterialStateAas:
    """A standalone AAS bundle for one BRIXTA MaterialState."""

    object_store: model.DictIdentifiableStore
    aas: model.AssetAdministrationShell
    material_state: model.Submodel
    aas_id: str
    material_state_id: str


def _id_segment(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be blank")
    return quote(cleaned, safe="-._~")


def _namespace_base(namespace: str) -> str:
    base = namespace.rstrip("/")
    if not base:
        raise ValueError("namespace must not be blank")
    return base


def _text(id_short: str, value: str) -> model.Property:
    return model.Property(
        id_short=id_short,
        value_type=model.datatypes.String,
        value=value,
    )


def _number(id_short: str, value: float) -> model.Property:
    return model.Property(
        id_short=id_short,
        value_type=model.datatypes.Double,
        value=float(value),
    )


def _collection(
    id_short: str,
    elements: Iterable[model.SubmodelElement],
) -> model.SubmodelElementCollection:
    return model.SubmodelElementCollection(id_short=id_short, value=set(elements))


def _named_string_entries(
    id_short: str,
    values: Mapping[str, str],
    *,
    entry_prefix: str,
) -> model.SubmodelElementCollection | None:
    if not values:
        return None

    entries = []
    for index, (name, value) in enumerate(sorted(values.items()), start=1):
        entries.append(
            _collection(
                f"{entry_prefix}{index:03d}",
                {
                    _text("Name", name),
                    _text("Value", value),
                },
            )
        )
    return _collection(id_short, entries)


def _named_number_entries(
    id_short: str,
    values: Mapping[str, float],
    *,
    entry_prefix: str,
) -> model.SubmodelElementCollection | None:
    if not values:
        return None

    entries = []
    for index, (name, value) in enumerate(sorted(values.items()), start=1):
        entries.append(
            _collection(
                f"{entry_prefix}{index:03d}",
                {
                    _text("Name", name),
                    _number("Value", value),
                },
            )
        )
    return _collection(id_short, entries)


def _chemistry(composition: ChemicalComposition) -> model.SubmodelElementCollection:
    components = []
    for index, component in enumerate(composition.components, start=1):
        values: set[model.SubmodelElement] = {
            _text("Name", component.name),
            _number("MassFraction", component.mass_fraction),
        }
        if component.uncertainty is not None:
            values.add(_number("Uncertainty", component.uncertainty))
        components.append(_collection(f"Component{index:03d}", values))

    return _collection("ChemicalComposition", components)


def _mineralogy(mineralogy: Mineralogy) -> model.SubmodelElementCollection:
    phases = []
    for index, phase in enumerate(mineralogy.phases, start=1):
        values: set[model.SubmodelElement] = {
            _text("Name", phase.name),
            _number("MassFraction", phase.mass_fraction),
        }
        if phase.uncertainty is not None:
            values.add(_number("Uncertainty", phase.uncertainty))
        phases.append(_collection(f"Phase{index:03d}", values))

    return _collection("Mineralogy", phases)


def _measurement(
    measurement: MeasurementRecord,
    *,
    index: int,
) -> model.SubmodelElementCollection:
    elements: set[model.SubmodelElement] = {
        _text("Technique", measurement.technique),
        _text("RunId", measurement.run_id),
        _text("CompletedAt", measurement.completed_at),
    }

    optional_text = {
        "Engine": measurement.engine,
        "EngineVersion": measurement.engine_version,
        "AdapterVersion": measurement.adapter_version,
        "MethodName": measurement.method_name,
        "MethodVersion": measurement.method_version,
        "MethodSha256": measurement.method_sha256,
    }
    for id_short, value in optional_text.items():
        if value is not None:
            elements.add(_text(id_short, value))

    nested = (
        _named_number_entries(
            "Metrics",
            measurement.metrics,
            entry_prefix="Metric",
        ),
        _named_string_entries(
            "Inputs",
            measurement.inputs,
            entry_prefix="Input",
        ),
        _named_string_entries(
            "InputSha256",
            measurement.input_sha256,
            entry_prefix="Hash",
        ),
        _named_string_entries(
            "Artifacts",
            measurement.artifacts,
            entry_prefix="Artifact",
        ),
    )
    elements.update(item for item in nested if item is not None)

    if measurement.warnings:
        elements.add(
            _collection(
                "Warnings",
                {
                    _text(f"Warning{warning_index:03d}", warning)
                    for warning_index, warning in enumerate(measurement.warnings, start=1)
                },
            )
        )

    return _collection(f"Measurement{index:03d}", elements)


def build_material_state_submodel(
    state: MaterialState,
    *,
    namespace: str = "https://brixta.org/aas",
) -> model.Submodel:
    """Map a BRIXTA MaterialState into a BaSyx AAS Submodel."""

    base = _namespace_base(namespace)
    sample_segment = _id_segment(state.sample_id, "sample_id")
    submodel_id = f"{base}/submodels/materials/{sample_segment}/material-state"

    elements: set[model.SubmodelElement] = {
        _text("StateSchemaVersion", state.schema_version),
        _text("SampleId", state.sample_id),
        _text("MaterialType", state.material_type),
        _text("ObservedAt", state.observed_at),
        _text("ChemistryStatus", state.chemistry_status),
        _text("MineralogyStatus", state.mineralogy_status),
    }

    if state.chemistry is not None:
        elements.add(_chemistry(state.chemistry))

    if state.mineralogy is not None:
        elements.add(_mineralogy(state.mineralogy))

    if state.measurements:
        elements.add(
            _collection(
                "Measurements",
                {
                    _measurement(measurement, index=index)
                    for index, measurement in enumerate(state.measurements, start=1)
                },
            )
        )

    return model.Submodel(
        id_=submodel_id,
        id_short="MaterialState",
        submodel_element=elements,
    )


def build_material_sample_aas(
    state: MaterialState,
    *,
    namespace: str = "https://brixta.org/aas",
) -> MaterialStateAas:
    """Create a standalone AAS for a material sample and its current MaterialState."""

    base = _namespace_base(namespace)
    sample_segment = _id_segment(state.sample_id, "sample_id")

    asset_id = f"{base}/assets/materials/{sample_segment}"
    aas_id = f"{base}/shells/materials/{sample_segment}"

    material_state = build_material_state_submodel(state, namespace=namespace)

    aas = model.AssetAdministrationShell(
        id_=aas_id,
        id_short="MaterialSample",
        asset_information=model.AssetInformation(
            asset_kind=model.AssetKind.INSTANCE,
            global_asset_id=asset_id,
        ),
        submodel={model.ModelReference.from_referable(material_state)},
    )

    store: model.DictIdentifiableStore[model.Identifiable] = model.DictIdentifiableStore()
    store.add(material_state)
    store.add(aas)

    return MaterialStateAas(
        object_store=store,
        aas=aas,
        material_state=material_state,
        aas_id=aas_id,
        material_state_id=material_state.id,
    )
