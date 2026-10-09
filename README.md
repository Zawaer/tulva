# Tulva

**Tulva prices Finland's spring floods as a joint risk.** This winter's snowpack and decades of SYKE river data
show which areas flood *together*; a quantum amplitude-estimation engine turns that into the price of a
parametric flood cover for insurers.

Built at the Quantum x Finance hackathon (Hanken × Ultrahack, 8–10 Oct 2026) by team STUHI (#21).

## Layout
- `src/tulva/`: data pipeline, joint flood model, index pricing, quantum circuits
- `scripts/`: runnable steps (fetch data, fit model, run circuits)
- `out/`: generated results and charts (every number in the deck comes from here)

## Pricing
`scripts/price_index.py` → `out/pricing.json`, `out/index_price.png`: per cluster and trigger, the technical price
(expected payout × 1.35), a market price range (× 2.5 to × 3.5, cat-bond / flood-ILS multiples) and a staged payout
(50 % at ≥2 gauges, 100 % at ≥3), under independence (no co-flooding), the Tulva model and the high / low March snow
outlook.

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

## Demo web app
```bash
python scripts/export_web.py                                   # out/ + data/ -> web/data/*.json (rerun after new results)
python3 -m http.server 3141 --bind 0.0.0.0 --directory web     # static page, no build step
```

## Two Python environments
IBM's runtime needs Qiskit ≥2.3; IQM's Qiskit plugin needs Qiskit <2.2. So:
```bash
uv venv -p 3.11 .venv     && VIRTUAL_ENV=.venv     uv pip install -r requirements.txt qiskit-ibm-runtime
uv venv -p 3.11 .venv-iqm && VIRTUAL_ENV=.venv-iqm uv pip install "iqm-client[qiskit]" numpy scipy pandas matplotlib
```
IQM runs: `IQM_TOKEN=... .venv-iqm/bin/python scripts/run_hw.py --backend iqm --iqm-name garnet`.
Rehearsals without hardware: `--backend iqm-fake` (IQM's 20-qubit noise model) and `--backend ibm-fake` (ibm_kingston).

## Qrisp version
The 3-qubit joint-trigger QAE ("Kittilä and Ivalo both pass their 1-in-50 spring level") is also written in
Qrisp: `src/tulva/qrisp_qae.py`. Hydrology and the two areas are `QuantumBool`s; each area gets `ry` plus a
further `ry` inside `with control(hydrology)`; the oracle is `tag_state({kittila: True, ivalo: True})`; Grover
powers come from `qrisp.amplitude_amplification`, and MLAE over k = 0, 1, 2 gives the estimate. Qrisp's own `IQAE`
runs as a simulator-only reference (it needs dozens of Grover iterates at a ≈ 0.1 %). Gate counts come from IQM's
Qrisp pass manager (`iqm.qrisp_iqm.create_iqm_pass_manager`) on Garnet's coupling map. Qrisp lives in `.venv-iqm`
(`VIRTUAL_ENV=.venv-iqm uv pip install "qrisp[iqm]"`; no conflict with iqm-client 36 / Qiskit 2.1).
```bash
.venv-iqm/bin/python scripts/qae_qrisp.py                         # Qrisp simulator -> out/qrisp_qae.json
.venv-iqm/bin/python scripts/qae_qrisp.py --backend fake-garnet   # Garnet noise model via Qrisp's QiskitBackend
IQM_TOKEN=... .venv-iqm/bin/python scripts/qae_qrisp.py --backend iqm --device garnet   # Qrisp IQMBackend
```
Hardware and fake-device runs go to `out/runs/qrisp_qae_*.json`.
