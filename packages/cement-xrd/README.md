# brixta-cement-xrd

`brixta-cement-xrd` is the BRIXTA Cement adapter for an external GSAS-II installation.

The package does **not** redistribute GSAS-II, GSAS-II native binaries, CIF reference data, instrument parameter files, or refinement recipes. Those remain external scientific/runtime assets.

## Scope of 0.1.0

Version `0.1.0` establishes the integration boundary:

- discover GSAS-II through `BRIXTA_GSASII_PATH`;
- import the GSAS-II scripting runtime;
- verify the compiled `pyspg` and `pypowder` binary modules are available;
- expose structured engine/runtime metadata;
- provide a `brixta-xrd doctor` diagnostic command.

It does **not** yet run cement Rietveld refinements or calculate phase mass fractions. Those workflows will be added after the engine boundary is stable and validated against real cement/clinker XRD inputs.

## Runtime layout

A typical local layout is:

```text
~/brixta-engines/
├── GSASII/
└── GSASII-bin/
    └── mac_arm_p3.13_n2.2/
```

Point BRIXTA to the directory that contains `GSASII/`:

```bash
export BRIXTA_GSASII_PATH="$HOME/brixta-engines"
```

The adapter also accepts the `GSASII/` directory itself and normalizes it to its parent installation root.

## Install

```bash
python -m pip install brixta-cement-xrd
```

GSAS-II must be installed separately using the upstream project and an appropriate binary bundle for the host platform, Python version, and NumPy version.

## Check the engine

```bash
brixta-xrd doctor
```

Or from Python:

```python
from brixta_cement_xrd import Gsas2Engine

engine = Gsas2Engine()

print(engine.available())
print(engine.info())
```

A successful `EngineInfo` contains the engine name, GSAS-II version, BRIXTA adapter version, source path, binary path, Python version, and NumPy version.

## Explicit path

```python
from brixta_cement_xrd import Gsas2Engine

engine = Gsas2Engine("~/brixta-engines")
info = engine.require_available()
```

## Ownership boundary

GSAS-II owns diffraction/crystallographic computation. BRIXTA owns the integration contract, cement workflow orchestration, validation, normalized results, provenance, and downstream Cement Twin integration.

GSAS-II and its assets are governed by their own upstream terms. This package does not relicense or redistribute them.
