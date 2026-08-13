# BRIXTA Cement thermodynamics

## v0.1

Runtime discovery, doctor, xGEMS/GEMS3K availability, configured standalone system,
and real CemGEMS smoke test.

## v0.2

```text
ThermoStateInput
        ↓
GemsEngine.equilibrate()
        ↓
xGEMS / GEMS3K
        ↓
ThermoResult
```

Structured phase/species/system output is now a stable BRIXTA contract.

## Next

```text
CementState
+ water/cement ratio
        ↓
oxide mass -> element moles
        ↓
ThermoStateInput
        ↓
CemGEMS
        ↓
HydrationState
```
