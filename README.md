# Tulva

**Tulva prices Finland's spring floods as a joint risk.** This winter's snowpack and decades of SYKE river data
show which areas flood *together*; a quantum amplitude-estimation engine turns that into the price of a
parametric flood cover for insurers.

Built at the Quantum x Finance hackathon (Hanken × Ultrahack, 8–10 Oct 2026) by team STUHI (#21).

## Layout
- `src/tulva/`: data pipeline, joint flood model, index pricing, quantum circuits
- `scripts/`: runnable steps (fetch data, fit model, run circuits)
- `notebooks/`: LUMI / Q20 notebooks
- `out/`: generated results and charts (every number in the deck comes from here)

## Running the hardware batch
```bash
python scripts/run_hw.py --backend sim-noisy        # rehearsal on a noisy simulator
python scripts/analyse_run.py out/runs/<file>.json  # raw vs noise-aware vs exact vs Monte Carlo
```
On LUMI (Aalto Q20): open Jupyter with reservation `QxF2026`, project `project_462001763`, partition `small`,
and the launch script `module load Local-quantum; module load fiqci-vtt-qiskit; export DEVICES=("radiance20");
source $RUN_SETUP`. Then, in a terminal in the repo:
```bash
python scripts/run_hw.py --backend q20               # raw
python scripts/run_hw.py --backend q20 --ems 2       # FiQCI error mitigation
```
Job ids are written to `out/runs/` before waiting for results, and `backend.retrieve_job(id)` recovers a lost run.
Check fiqci.fi/status first.
