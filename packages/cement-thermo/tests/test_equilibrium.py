from __future__ import annotations

from types import ModuleType

import pytest

from brixta_cement_thermo import GemsEngine, ThermoConfigurationError, ThermoStateInput


class FakeVector(list):
    def copy(self):
        return FakeVector(self)

    def __setitem__(self, key, value):
        if isinstance(key, slice) and not isinstance(value, list | tuple):
            value = [value] * len(self)
        super().__setitem__(key, value)


class FakeChemicalEngine:
    def __init__(self, filename):
        self.filename = filename
        self._elements = ["Ca", "Si", "O", "H"]
        self._b = FakeVector([1.0, 1.0, 3.0, 2.0])
        self._t = 298.15
        self._p = 100000.0

    def numElements(self):
        return 4

    def numSpecies(self):
        return 3

    def numPhases(self):
        return 2

    def elementName(self, index):
        return self._elements[index]

    def speciesName(self, index):
        return ["Ca+2", "H2O@", "C-S-H"][index]

    def phaseName(self, index):
        return ["aq_gen", "CSHQ"][index]

    def indexPhaseWithSpecies(self, index):
        return [0, 0, 1][index]

    def speciesCharge(self, index):
        return [2.0, 0.0, 0.0][index]

    def temperature(self):
        return self._t

    def pressure(self):
        return self._p

    def elementAmounts(self):
        return self._b.copy()

    def equilibrate(self, temperature, pressure, elements):
        self._t = float(temperature)
        self._p = float(pressure)
        self._b = FakeVector(elements)
        return 0

    def converged(self):
        return True

    def numIterations(self):
        return 12

    def elapsedTime(self):
        return 0.02

    def phaseAmounts(self):
        return [55.0, 0.25]

    def phaseMasses(self):
        return [1.0, 0.05]

    def phaseVolumes(self):
        return [0.001, 0.00002]

    def phaseDensities(self):
        return [1000.0, 2500.0]

    def phaseSatIndices(self):
        return [0.0, 0.0]

    def speciesAmounts(self):
        return [0.01, 55.0, 0.25]

    def ionicStrength(self):
        return 0.31

    def pH(self):
        return 13.5

    def pe(self):
        return 2.8

    def Eh(self):
        return 0.16

    def systemMass(self):
        return 1.05

    def systemVolume(self):
        return 0.00102

    def systemGibbsEnergy(self):
        return -1000.0

    def systemEnthalpy(self):
        return -2000.0

    def systemEntropy(self):
        return 10.0

    def systemHeatCapacityConstP(self):
        return 50.0


def fake_module():
    module = ModuleType("fake_xgems")
    module.ChemicalEngine = FakeChemicalEngine
    return module


def test_structured_equilibrium_result(tmp_path):
    system = tmp_path / "CemHyds-dat.lst"
    system.write_text("fake", encoding="utf-8")
    result = GemsEngine(
        adapter_version="0.2.0",
        system_path=system,
        module=fake_module(),
    ).equilibrate(
        ThermoStateInput(
            temperature_k=293.15,
            element_amounts_mol={"Ca": 1.2, "Si": 0.3, "O": 4.0, "H": 5.0},
        )
    )
    assert result.converged is True
    assert result.ph == pytest.approx(13.5)
    assert result.phase("CSHQ").amount_mol == pytest.approx(0.25)
    assert result.species_by_name("Ca+2")[0].phase_name == "aq_gen"
    assert result.element_amounts_mol["Ca"] == pytest.approx(1.2)


def test_unknown_element_is_rejected(tmp_path):
    system = tmp_path / "CemHyds-dat.lst"
    system.write_text("fake", encoding="utf-8")
    engine = GemsEngine(
        adapter_version="0.2.0",
        system_path=system,
        module=fake_module(),
    )
    with pytest.raises(ThermoConfigurationError, match="does not contain requested elements"):
        engine.equilibrate(ThermoStateInput(element_amounts_mol={"U": 1.0}))


def test_loaded_system_composition_can_run_unchanged(tmp_path):
    system = tmp_path / "CemHyds-dat.lst"
    system.write_text("fake", encoding="utf-8")
    result = GemsEngine(
        adapter_version="0.2.0",
        system_path=system,
        module=fake_module(),
    ).equilibrate(ThermoStateInput())
    assert result.element_amounts_mol["Ca"] == pytest.approx(1.0)
