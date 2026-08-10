from pathlib import Path

from brixta_cement_aas import build_reference_pyro_line, write_aasx, write_json

bundle = build_reference_pyro_line("plant-001", "pyro-01")
out = Path("artifacts")
write_json(bundle, out / "pyro-line.json")
write_aasx(bundle, out / "pyro-line.aasx")

print(out / "pyro-line.json")
print(out / "pyro-line.aasx")
