from __future__ import annotations

import hashlib
from pathlib import Path
from types import ModuleType
from typing import Any

from .environment import (
    ThermoEngineInfo,
    configured_system_path,
    import_xgems,
    inspect_environment,
)
from .errors import ThermoConfigurationError, ThermoError
from .model import ThermoPhase, ThermoResult, ThermoSpecies, ThermoStateInput


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class GemsEngine:
    def __init__(
        self,
        *,
        adapter_version: str,
        system_path: str | Path | None = None,
        module: ModuleType | Any | None = None,
    ) -> None:
        self._adapter_version = adapter_version
        self._system_path = None if system_path is None else Path(system_path)
        self._module = module

    def available(self) -> bool:
        try:
            self.info()
        except RuntimeError:
            return False
        return True

    def info(self) -> ThermoEngineInfo:
        return inspect_environment(adapter_version=self._adapter_version)

    def require_available(self) -> ThermoEngineInfo:
        return self.info()

    def _xgems(self) -> ModuleType | Any:
        return self._module if self._module is not None else import_xgems()

    def _resolved_system_path(self) -> Path:
        if self._system_path is not None:
            path = self._system_path.expanduser().resolve()
            if not path.exists():
                raise ThermoConfigurationError(f"thermodynamic system does not exist: {path}")
            return path

        path = configured_system_path()
        if path is None:
            raise ThermoConfigurationError(
                "No thermodynamic system configured. Set BRIXTA_GEMS_SYSTEM or "
                "pass system_path=... to GemsEngine."
            )
        return path

    def load_system(self) -> Any:
        path = self._resolved_system_path()
        factory = getattr(self._xgems(), "ChemicalEngine", None)
        if factory is None or not callable(factory):
            raise ThermoConfigurationError(
                "xGEMS module does not expose a callable ChemicalEngine."
            )
        return factory(str(path))

    def equilibrate(self, request: ThermoStateInput) -> ThermoResult:
        path = self._resolved_system_path()
        engine = self.load_system()

        temperature = (
            float(request.temperature_k)
            if request.temperature_k is not None
            else float(engine.temperature())
        )
        pressure = (
            float(request.pressure_pa)
            if request.pressure_pa is not None
            else float(engine.pressure())
        )

        elements = engine.elementAmounts().copy()
        if request.element_amounts_mol:
            if not request.preserve_unspecified_elements:
                elements[:] = 0.0

            indexes = {
                str(engine.elementName(index)): index
                for index in range(int(engine.numElements()))
            }
            unknown = sorted(set(request.element_amounts_mol) - set(indexes))
            if unknown:
                raise ThermoConfigurationError(
                    "Thermodynamic system does not contain requested elements: "
                    + ", ".join(unknown)
                )
            for name, amount in request.element_amounts_mol.items():
                elements[indexes[name]] = float(amount)

        status_code = int(engine.equilibrate(temperature, pressure, elements))
        if not bool(engine.converged()):
            raise ThermoError(
                "GEMS equilibrium calculation did not converge "
                f"(status_code={status_code}, iterations={engine.numIterations()})."
            )

        phase_amounts = engine.phaseAmounts()
        phase_masses = engine.phaseMasses()
        phase_volumes = engine.phaseVolumes()
        phase_densities = engine.phaseDensities()
        phase_sat_indices = engine.phaseSatIndices()
        phases = []
        for index in range(int(engine.numPhases())):
            amount = float(phase_amounts[index])
            if abs(amount) < request.min_phase_amount_mol:
                continue
            phases.append(
                ThermoPhase(
                    name=str(engine.phaseName(index)),
                    amount_mol=amount,
                    mass_kg=float(phase_masses[index]),
                    volume_m3=float(phase_volumes[index]),
                    density_kg_m3=float(phase_densities[index]),
                    saturation_index=float(phase_sat_indices[index]),
                )
            )

        species_amounts = engine.speciesAmounts()
        species = []
        for index in range(int(engine.numSpecies())):
            amount = float(species_amounts[index])
            if abs(amount) < request.min_species_amount_mol:
                continue
            phase_index = int(engine.indexPhaseWithSpecies(index))
            species.append(
                ThermoSpecies(
                    name=str(engine.speciesName(index)),
                    phase_name=str(engine.phaseName(phase_index)),
                    amount_mol=amount,
                    charge=float(engine.speciesCharge(index)),
                )
            )

        output_elements = engine.elementAmounts()
        element_amounts = {
            str(engine.elementName(index)): float(output_elements[index])
            for index in range(int(engine.numElements()))
        }

        if self._module is None:
            info = self.info().to_dict()
        else:
            info = {
                "engine": "xGEMS/GEMS3K",
                "engine_version": "test-double",
                "adapter_version": self._adapter_version,
                "python_version": "test",
                "module_path": "test-double",
                "chemical_engine_available": True,
                "system_path": str(path),
            }

        warnings = ()
        if status_code != 0:
            warnings = (
                "xGEMS returned a non-zero status code despite reporting convergence: "
                f"{status_code}.",
            )

        return ThermoResult(
            system_path=str(path),
            system_sha256=_sha256(path),
            engine=info,
            input=request,
            converged=True,
            status_code=status_code,
            iterations=int(engine.numIterations()),
            elapsed_time_s=float(engine.elapsedTime()),
            temperature_k=float(engine.temperature()),
            pressure_pa=float(engine.pressure()),
            element_amounts_mol=element_amounts,
            phases=tuple(phases),
            species=tuple(species),
            ionic_strength_molal=float(engine.ionicStrength()),
            ph=float(engine.pH()),
            pe=float(engine.pe()),
            eh_v=float(engine.Eh()),
            system_mass_kg=float(engine.systemMass()),
            system_volume_m3=float(engine.systemVolume()),
            system_gibbs_energy=float(engine.systemGibbsEnergy()),
            system_enthalpy=float(engine.systemEnthalpy()),
            system_entropy=float(engine.systemEntropy()),
            system_heat_capacity_const_p=float(engine.systemHeatCapacityConstP()),
            warnings=warnings,
        )
