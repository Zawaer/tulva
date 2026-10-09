# Pitch notes (Vaishnav): additions to the 8-slide deck

The deck as built (deck/Tulva_QxF2026.pptx, 8 slides, script in PITCH.md, ~2:56):
1 hook (2005) · 2 the gap · 3 the product and its price · 4 demo video (60 s) · 5 quantum in practice ·
6 quantum, honestly · 7 business · 8 close. The organisers' workshop (PITCH_WORKSHOP.md) asks for two things the
script does not yet say out loud. Spoken on slides, not in the video. Time comes from slides 5–6 (33 s of quantum).

## A. "How does it differ from what exists?" (slide 3 or 7, ~12 s)
> Cat models such as Verisk and Moody's RMS cover Finland, but they are rain-driven and don't price snowmelt
> floods jointly. No Nordic parametric river-flood cover exists; Swiss Re's FLOW sells gauge covers to companies,
> not to insurers. Tulva is the first joint, snow-conditioned price for Finnish spring floods.

Sources: business/reports/Tulva flood cover business case.md (Verisk and RMS product pages, Swiss Re FLOW).

## B. Hackathon journey and tools (slide 8, ~15 s)
> Nothing existed before Thursday evening. In about 40 hours: 65 years of SYKE and SMHI river data, SYKE snow,
> FMI temperature and rain; a fitted joint model; a priced index cover; a live demo app; and the same circuits run
> on IBM Marrakesh and IQM Garnet and Emerald, in Qiskit and in IQM's Qrisp. It is all in one public GitHub repo,
> commit by commit.

Tools: Python (numpy, scipy, pandas), Qiskit + Aer, Qrisp, IQM Resonance, IBM Quantum, LUMI (Q50/Q20 prepared),
Leaflet web app, Claude Code.

## C. Q&A facts
- **Hardware sweet spot (measured on IQM Emerald and IBM Marrakesh):** circuits of about 3–9 qubits (works up to
  ~15) and under ~50 two-qubit steps give the right answer today, raw or after calibration, for events no rarer
  than about 1-in-10. The 9-qubit snow + temperature + rain → 5 rivers circuit works (16.5 % vs 13.6 % exact).
  Add the 1-in-50 level (14 qubits, 54 steps) or the full 43-qubit model (237 steps) and noise takes over.
- **Snow signal on the chip:** snowy vs low-snow March, exact 2.8×, IQM measured 3.0× (3 qubits, 240,000 shots).
- **Better predictions:** adding April–May rain lifts the North's explained variation from 17 % to 28 %; the
  back-test warning goes from 9 to 12 of 19 payout years (with observed weather, so an upper bound). Roadmap item.

## D. Who pays whom (business Q&A)
- Homeowners and businesses pay home/property insurance to OP, LocalTapiola, If, Fennia. Since 2014 flood damage
  is covered there, but only floods rarer than 1-in-50.
- The insurer's problem: one snowy spring means thousands of claims at once across a region.
- Tulva Index cover: the **insurer** pays a yearly premium (about €0.5–0.7M for the North cover at market price).
  When ≥2 of 5 northern gauges pass 1-in-50, the **insurer receives €10M**.
- Who carries the €10M: a reinsurer or ILS investor (Swiss Re, Munich Re, Hannover Re…), **not Tulva**.
- Tulva is the brain, not the wallet: we licence the pricing and trigger engine, and take a structuring fee when
  a cover is placed. We never pay claims.
