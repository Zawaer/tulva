"""Pack the files needed on LUMI into one self-extracting script (lumi/tulva_lumi.py).

On LUMI (Jupyter terminal, after the module lines from the QuickStart):
    python tulva_lumi.py            # unpacks into ./tulva_lumi/
    cd tulva_lumi && bash run_lumi.sh q50     # or q20
"""
import base64, io, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ["src/tulva/__init__.py", "src/tulva/factor.py", "src/tulva/quantum.py", "scripts/run_hw.py",
         "scripts/run_loader_hw.py", "scripts/analyse_run.py", "out/model_params.json", "out/joint_counts.json"]
RUN = """#!/bin/bash
# bash run_lumi.sh q50|q20   (run inside the LUMI Jupyter terminal; modules loaded, DEVICES exported, $RUN_SETUP sourced)
set -u
DEV=${1:-q50}
python -c "import scipy" 2>/dev/null || pip install --user -q scipy
mkdir -p out/runs
echo "== 3-qubit QAE batch on $DEV (raw)"
python scripts/run_hw.py --backend $DEV --instances A3_kittila_ivalo_both --ks 0,1,2 --shots 4000 --copies 4 --best-qubits \\
  && python scripts/analyse_run.py $(ls -t out/runs/$DEV*.json | grep -v analysis | head -1)
echo "== 14-area loader on $DEV"
python scripts/run_loader_hw.py --backend $DEV --shots 8000
echo "== pack results"
tar czf tulva_results_$DEV.tgz out/runs && echo "Download tulva_results_$DEV.tgz (right-click in the Jupyter file browser)"
"""
buf = io.BytesIO()
with tarfile.open(fileobj=buf, mode="w:gz") as t:
    for f in FILES:
        t.add(ROOT / f, arcname=f)
    data = RUN.encode()
    ti = tarfile.TarInfo("run_lumi.sh"); ti.size = len(data); ti.mode = 0o755
    t.addfile(ti, io.BytesIO(data))
payload = base64.b64encode(buf.getvalue()).decode()
out = ROOT / "lumi" / "tulva_lumi.py"
out.write_text(f'''"""Tulva files for LUMI (self-extracting). Run: python tulva_lumi.py"""
import base64, io, tarfile
DATA = "{payload}"
tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)), mode="r:gz").extractall("tulva_lumi")
print("unpacked into ./tulva_lumi  →  cd tulva_lumi && bash run_lumi.sh q50   (or q20)")
''')
print(out, out.stat().st_size, "bytes")
