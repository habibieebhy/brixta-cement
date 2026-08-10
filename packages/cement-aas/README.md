# BRIXTA Cement

BRIXTA Cement is an open-source, integration-first digital twin stack
for cement manufacturing.

The project composes established industrial standards, open-source
scientific engines, simulation systems, and optimization frameworks
rather than reimplementing their underlying science.

## Architecture principle

Integrate first. Compose second. Invent last.

BRIXTA-owned code should primarily provide:

- cement-specific compositions and semantics
- adapters to upstream scientific engines
- mappings between industrial standards and cement workflows
- model orchestration
- provenance and reproducibility
- application APIs and user experience

## Initial packages

### `brixta-cement-aas`

Cement-specific Asset Administration Shell compositions built on the
Eclipse BaSyx / AAS ecosystem.

Future packages will cover scientific integrations such as XRD,
thermodynamics, simulation, and optimization as their upstream
interfaces are validated.

## Status

Early development / experimental.

The public APIs are not yet stable.