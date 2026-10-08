#!/bin/bash
# Friday-morning hardware batch. Run each block on the machine that has access; every run saves its
# job ids to out/runs/ before waiting, and is analysed right after.
#
#   bash scripts/hardware_day.sh iqm      # IQM Resonance (needs IQM_TOKEN; uses .venv-iqm)
#   bash scripts/hardware_day.sh ibm      # IBM (saved QiskitRuntimeService account; uses .venv)
#   bash scripts/hardware_day.sh lumi     # Q50 / Q20 (run on LUMI with fiqci-vtt-qiskit loaded)
#   bash scripts/hardware_day.sh rehearse # fake backends, no hardware needed
set -euo pipefail
cd "$(dirname "$0")/.."
# secrets (IBM_QUANTUM_TOKEN, IBM_QUANTUM_INSTANCE, IQM_TOKEN) live in .env, which git ignores
if [ -f .env ]; then set -a; . ./.env; set +a; fi
latest() { ls -t out/runs/"$1"*.json | grep -v analysis | head -1; }
analyse() { .venv/bin/python scripts/analyse_run.py "$(latest "$1")"; }

case "${1:-rehearse}" in
  iqm)
    : "${IQM_TOKEN:?set IQM_TOKEN (IQM Resonance API token)}"
    # 20-qubit Garnet: k = 0..2 (deeper circuits drown in noise on IQM), 3 repeats
    .venv-iqm/bin/python scripts/run_hw.py --backend iqm --iqm-name "${IQM_DEVICE:-garnet}" --ks 0,1,2 --shots 2000 --repeats 3
    analyse iqm ;;
  ibm)
    # 10 min budget: 25 side-by-side copies, k = 0..3, one repeat (25× the shots for free)
    .venv/bin/python scripts/run_hw.py --backend ibm --ibm-name "${IBM_DEVICE:-ibm_kingston}" --ks 0,1,2,3 --shots 2000 --copies 25
    analyse ibm ;;
  lumi)
    # on LUMI: python is the module's; raw and FiQCI-EMS mitigated
    dev="${LUMI_DEVICE:-q50}"
    python scripts/run_hw.py --backend "$dev" --ks 0,1,2 --shots 2000 --repeats 3
    python scripts/run_hw.py --backend "$dev" --ks 0,1,2 --shots 2000 --repeats 3 --ems 2 || echo "EMS run failed: check fiqci-ems API (help(fiqci.ems))"
    python scripts/analyse_run.py "$(latest "$dev")" ;;
  rehearse)
    .venv-iqm/bin/python scripts/run_hw.py --backend iqm-fake --ks 0,1,2 --shots 2000
    analyse iqm-fake
    .venv/bin/python scripts/run_hw.py --backend ibm-fake --ks 0,1,2,3 --shots 2000
    analyse ibm-fake ;;
  *) echo "usage: $0 iqm|ibm|lumi|rehearse"; exit 2 ;;
esac
.venv/bin/python scripts/export_web.py >/dev/null 2>&1 || true
