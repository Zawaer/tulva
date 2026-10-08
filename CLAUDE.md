# Tulva: context for every Claude Code session

## The project
Tulva prices Finland's spring floods as a joint risk. Several river flood-risk areas flood in the same spring
(shared snowpack). Regulators assume independence (EIOPA: 0 % Nordic flood correlation); SYKE's national
totals implicitly assume everything floods at once. We estimate the joint risk from SYKE discharge data,
condition it on the March snowpack, and price a parametric index cover ("pays when ≥2 gauges in a cluster pass
their 1-in-50 level"). Quantum amplitude estimation (QAE) estimates the joint-trigger probability; we compare it
honestly with exact values and classical Monte Carlo.

## Event
Quantum x Finance, Hanken (Helsinki), Thu 8 – Sat 10 Oct 2026. Deck (with embedded demo video) due **Sat 09:30**.
Pitch 3 min + 3 min Q&A. Checkpoints: Fri 09:00, Fri 17:00. Pitching training Fri 13:00.
Criteria: Impact · Business plan · Team progress during the event · Innovativeness · Methodological capability
(demo/simulation; quantum in practice or theory).
Jury: Toikka (OP), Anbarjafari (PwC), Steinmann (IQM), Seesto (IBM), Mehtola (VTT).

## Rules for agents
- **All code in this repo is written during the event.** Don't import code from other repos.
- Every number that goes in the deck must be produced by code here and logged in `CLAIMS.md` with what
  produced it: `exact`, `monte-carlo`, `qae-sim`, `qae-q20`, `qae-ibm`.
- Never claim quantum advantage. Classical exact/Monte Carlo is the reference.
- Record decisions affecting others in `DECISIONS.md` before acting on them.
- Hardware: Aalto Q20 via LUMI (`radiance20`, IQM, 20 qubits, CZ + PRX); IBM as backup. Keep circuits small
  (two-qubit gate budget ~50).

## Stack
Python 3.11, numpy/scipy/pandas/matplotlib, qiskit + qiskit-aer. On LUMI: `module load Local-quantum
fiqci-vtt-qiskit`, `IQMProvider(os.getenv("Q20_CORTEX_URL"), quantum_computer="radiance20")`.

## Collaboration
Two people (Toivo: data/model/quantum/web; Vaishnav: deck/, business/). Read COLLABORATION.md: pull --rebase
before every push, only edit your owner's folders, numbers only from CLAIMS.md.
