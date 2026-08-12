# brixta-cement-rawmix

`brixta-cement-rawmix` is BRIXTA's integration-first raw-meal optimization layer.

- **Pyomo** owns the algebraic optimization model.
- **HiGHS** owns the LP solve.
- **BRIXTA** owns cement-domain contracts, LSF/SM/AM constraints, material/oxide bounds, orchestration, validation, and normalized results.

No custom optimizer or solver is implemented here.

## 0.1.0 scope

Inputs: raw-material oxide analyses, material percentage bounds, optional cost, LSF/SM/AM target ranges, and optional oxide bounds.

Outputs: optimized material fractions, resulting oxide composition, LSF/SM/AM, objective value, and solver provenance.

Fractions use a `0..1` mass-fraction basis.

The initial formulation is linear. Modulus ratio bounds are expressed as equivalent linear inequalities, avoiding nonlinear division inside the optimization model.

Raw-material chemistry must come from plant/lab data, manual tables, CSV/database imports, or a future XRF adapter.
