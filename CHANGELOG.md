# Changelog

## Unreleased

### Added

- `brixta-cement-aas` Phase 1A implementation.
- Reference precalciner pyro-line AAS composition.
- BaSyx-backed JSON and AASX serialization.
- `brixta-cement-xrd` external GSAS-II runtime discovery and diagnostics.
- Quantitative powder-XRD workflow using GSAS-II `G2Project`, explicit phase models,
  versioned refinement recipes and `ComputeMassFracs()`.
- Normalized `XrdResult` with phase mass fractions, uncertainties, residuals, SHA-256
  provenance, warnings, `.gpx` and JSON artifacts.
- `brixta-xrd analyze` command for explicit data/instrument/phase/recipe-driven runs.
- Tests, CI and PyPI trusted-publishing workflows.
- Upstream architecture and release documentation.
