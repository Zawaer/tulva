# Quantum computing for insurance/finance risk pricing (QAE) and the Quantum x Finance 2026 jury organisations

Research date: 8 October 2026. Sources were found by web search and fetch in this session unless they are marked **[recalled, not re-fetched]**. Those are well-known papers cited from prior knowledge with their arXiv IDs, and the report writer should spot-check them before final citation. Vendor roadmap claims are labelled as targets, not achievements.

## 1. State of the art of QAE for risk analysis, option pricing and insurance, and a realistic advantage timeline

### Takeaway
QAE gives a provable quadratic reduction in oracle queries compared with classical Monte Carlo (error about 1/N instead of 1/sqrt(N)). The best published end-to-end resource estimate for a practically relevant derivative is still about 8,000 logical qubits, a T-depth of about 54 million and a logical clock rate around 10–50 MHz (Chakrabarti et al., Quantum 2021). No hardware on any public roadmap delivers that before the 2030s, so practical advantage for Monte Carlo pricing belongs to the fault-tolerant era. Insurance-specific QAE work is very recent (2022–2026), is mostly simulator-based, and itself reports that strong classical baselines win today.

### Cited findings

**Foundational algorithms**
- Montanaro (2015) showed a quadratic quantum speedup for Monte Carlo estimation of expectations. This is the theoretical basis that all QAE pricing papers cite. **[recalled]** [arXiv:1504.06987](https://arxiv.org/abs/1504.06987)
- Woerner & Egger, "Quantum risk analysis" (npj Quantum Information 5, 2019), applied amplitude estimation to expected value, VaR and CVaR of a portfolio. They reported a quadratic speedup over Monte Carlo and ran a small T-bill example on IBM quantum hardware. **[recalled]** [arXiv:1806.06893](https://arxiv.org/abs/1806.06893)
- Stamatopoulos et al., "Option pricing using quantum computers" (Quantum 4, 291, 2020). Pricing of European, basket, barrier and Asian options with QAE, with log-normal distributions loaded into qubits. **[recalled]** [arXiv:1905.02666](https://arxiv.org/abs/1905.02666)
- Suzuki et al. (2020), "Amplitude estimation without phase estimation". This is maximum-likelihood AE (MLAE): it runs Grover powers Q^{m_k} with no QFT or phase-estimation register and combines the results by maximum likelihood. It is the method Tulva uses. **[recalled]** [arXiv:1904.10246](https://arxiv.org/abs/1904.10246)
- Grinko, Gacon, Zoufal & Woerner (IBM), Iterative QAE (npj Quantum Information 2021):
  - It drops QPE and uses only Grover iterations, which lowers qubit and gate counts.
  - It is proven quadratic up to a double-log factor.
  - Empirically it needs fewer samples than other QPE-free variants.
  - It is implemented in Qiskit.
  - Sources: [arXiv:1912.05559](https://arxiv.org/pdf/1912.05559); [DOAJ/npj QI](https://doaj.org/article/ebd041b0f6944415a70bbe6459648696); [Qiskit source](https://qiskit.org/ecosystem/algorithms/_modules/qiskit_algorithms/amplitude_estimators/iae.html)
- Giurgica-Tiron et al., "Low depth algorithms for quantum amplitude estimation" (Quantum 6, 745, published 27 Jun 2022):
  - The algorithms interpolate between classical sampling and full QAE. Total oracle calls × sequential depth scales as 1/ε², so you trade speedup for circuit depth.
  - "Power-law AE" uses power-law schedules inside the Suzuki MLAE framework.
  - Sources: [Quantum journal](https://quantum-journal.org/papers/q-2022-06-27-745/); [arXiv:2012.03348](https://arxiv.org/abs/2012.03348v1)
- Low-depth AE was demonstrated on IonQ trapped-ion hardware in 2021 (arXiv:2109.09685):
  - The MLE variant reached a mean additive error of about 10⁻² on toy inner-product problems.
  - Accuracy improved with deeper circuits, including ones with more than 90 two-qubit gates.
  - Source: [ar5iv 2109.09685](https://ar5iv.labs.arxiv.org/html/2109.09685)

**Resource estimates and timeline (the "threshold")**
- Chakrabarti et al., "A Threshold for Quantum Advantage in Derivative Pricing" (Quantum, 2021, DOI 10.22331/q-2021-06-01-463; Goldman Sachs and IBM):
  - Benchmarks were an autocallable and a TARF.
  - The estimate is about 8k logical qubits and a T-depth of about 54M.
  - Advantage requires running this in about one second.
  - The earlier arXiv v2 said 7.5k qubits and 46M T-depth with about a 10 MHz logical clock. Cite the journal numbers.
  - The paper's contribution is a "re-parameterization" method combining pre-trained variational circuits with fault-tolerant QAE.
  - Sources: [arXiv 2012.03819](https://arxiv.org/abs/2012.03819v2); [QCrypt 2021 abstract](https://qcrypt2021.quics.umd.edu/node/2731); [Microsoft Quantum blog](https://cloudblogs.microsoft.com/quantum/?p=11030). The Microsoft blog gives the autocallable total T-depth as about 5.4×10⁷, with the Grover operator Q contributing about 9.5k.
- Follow-up work by Stamatopoulos, Mazzola, Woerner & Zeng (2021) applied quantum gradient algorithms to market risk (Greeks):
  - Their work cites a requirement of about a 50 MHz logical clock to match one-second classical MC pricing of the autocallable.
  - A secondary assessment cites contemporary estimates of feasible logical clock rates around 10 kHz, which is three to four orders of magnitude short.
  - Sources: [arXiv 2111.12509](https://arxiv.org/pdf/2111.12509); [PostQuantum Utility Map](https://postquantum.com/quantum-utility-map/quantum-computing-finance-wall-street/)
- Stamatopoulos & Zeng, "Derivative pricing using quantum signal processing" (Quantum 2024) reportedly lowered the threshold to about 4.7k logical qubits and about 45 MHz. **[recalled, numbers not re-verified]** [arXiv:2307.14310](https://arxiv.org/abs/2307.14310)
- Skeptical framing: Babbush et al., "Focus beyond quadratic speedups for error-corrected quantum advantage" (PRX Quantum 2021) argue that quadratic speedups such as QAE are unlikely to beat classical computing on early fault-tolerant machines because of error-correction overheads. **[recalled]** [arXiv:2011.04149](https://arxiv.org/abs/2011.04149)
- State-loading caveat: Herbert (2021) showed that Grover–Rudolph-style distribution loading can erase the QMCI speedup. **[recalled]** [arXiv:2101.02240](https://arxiv.org/abs/2101.02240)

**Hardware roadmaps (targets, not delivered facts)**
- IBM roadmap (announced 10 Jun 2025):
  - Starling, about 200 logical qubits and 100M operations, targeted for 2029 at Poughkeepsie.
  - It uses qLDPC codes, which IBM says need up to 90% fewer physical qubits.
  - Intermediate steps: Loon (2025), Kookaburra (2026), Cockatoo (2027). Blue Jay (about 2,000 logical qubits, 1B operations) is targeted for about 2033.
  - Commentators note skepticism about the timeline.
  - Sources: [The Quantum Insider](https://thequantuminsider.com/2025/06/10/ibm-offers-roadmap-toward-large-scale-fault-tolerant-quantum-computer/); [DCD](https://www.datacenterdynamics.com/en/news/ibm-updates-quantum-computing-roadmap-to-deliver-starling-system-by-2029/)
- IBM Nighthawk and Loon (Nov 2025 QDC):
  - Nighthawk is a 120-qubit square lattice with 218 tunable couplers. IBM targets up to 7,500 gates by end-2026 and 10,000 in 2027.
  - IBM said it expects community-verified quantum advantage by the end of 2026 and launched an advantage tracker.
  - I found no 2026 confirmation that this has been achieved.
  - Sources: [Next Platform, 12 Nov 2025](https://www.nextplatform.com/2025/11/12/ibm-lets-fly-nighthawk-and-loon-qpus-on-the-way-to-quantum-advantage/); [Constellation Research](https://www.constellationr.com/insights/news/ibm-launches-ibm-quantum-nighthawk-processor)
- IQM Halocene (announced 13 Nov 2025):
  - The first system is a 150-qubit, error-correction-oriented machine built on the Radiance line.
  - It targets 99.7% two-qubit fidelity and supports research on up to 5 logical qubits with Clifford gates.
  - Availability is targeted for end-2026.
  - Later Halocene releases are planned to exceed 1,000 qubits, "aligning with IQM's roadmap to achieve fault-tolerant quantum computing by 2030."
  - Sources: [The Quantum Insider](https://thequantuminsider.com/2025/11/13/iqm-launches-a-new-quantum-computer-product-line-for-error-correction/); [Quantum Computing Report](https://quantumcomputingreport.com/iqm-launches-halocene-product-line-to-scale-quantum-error-correction-research/)

**Insurance-specific QAE**
- Kirke (arXiv:2603.15664, submitted 10 Mar 2026, stat.AP, not peer reviewed), "Quantum Amplitude Estimation for Catastrophe Insurance Tail-Risk Pricing: Empirical Convergence and NISQ Noise Analysis":
  - Lognormal cat-loss distributions are amplitude-encoded and amplified with up to k=16 Grover iterations.
  - Data: NOAA Storm Events (58,028 records) plus synthetic data. Runs were on the Qiskit Aer simulator only.
  - Findings: there is a speedup in the oracle model, but strong classical baselines outperform QAE when analytical access exists, and "discretisation, not estimation, is the current bottleneck."
  - This is the closest prior art to Tulva and supports Tulva's honest-benchmark framing.
  - Source: [arXiv abs](https://arxiv.org/abs/2603.15664)
- Adam (2022, AXA with Fraunhofer ITWM), "Potential Applications of Quantum Computing for the Insurance Industry":
  - It explains AE in detail and gives two circuits for insurance payoff features, including dynamic lapse.
  - The lapse circuit was evaluated on a simulator and on real hardware.
  - Source: [arXiv:2210.06172](https://arxiv.org/pdf/2210.06172)
- Amjad (2025, British Actuarial Journal) asks whether the QAE quadratic speedup can be realised for industrial-scale Solvency II internal models at a medium-sized insurer. Source: [IDEAS/RePEc](https://ideas.repec.org/a/cup/bracjl/v30y2025ip-_1.html)
- A literature review on quantum computing in insurance (Zeitschrift für die gesamte Versicherungswissenschaft, online 12 Feb 2026) has co-authors from Hochschule München and a PwC Deutschland actuarial partner. Source: [Duncker & Humblot](https://elibrary.duncker-humblot.com/article/76791/quantum-computing-in-the-insurance-industry-insights-from-the-literature)

### Inferences
- Tulva's design matches the academic best practice for the NISQ era:
  - It uses MLAE with Grover powers, so there is no QPE.
  - It applies QAE to a low-dimensional joint-trigger probability, where the state can be prepared cheaply and exactly.
  - It benchmarks against exact values and classical MC.
- A parametric binary trigger is a good QAE target. The payoff is an indicator, so the "objective qubit" is just a comparator, with no piecewise-linear payoff rotation. That avoids one of the main approximation-error sources in option-pricing QAE.
- Kirke 2026 shows that the "discretisation bottleneck" is the honest weakness to name. A defensible quantum-advantage claim needs a model where the distribution can be loaded in polylog depth, for example a model generated by a quantum circuit, or the quadratic gain disappears (Herbert 2021).
- Realistic timeline wording: "Practical advantage for Monte Carlo-type pricing requires on the order of thousands of logical qubits at MHz logical clock rates. Vendor roadmaps target the first ~100–200 logical-qubit machines around 2029–2030 (IBM Starling, IQM FT roadmap), so pricing advantage is plausibly a 2030s question, not a 2026 one."

### Gaps
- The exact Stamatopoulos & Zeng 2024 QSP numbers and the Babbush et al. conclusions were not re-fetched this session.
- I did not find the full Kirke paper's NISQ noise-analysis results, only the abstract.
- I found no peer-reviewed QAE paper on parametric or flood insurance specifically. Tulva appears to be novel in that framing (absence of evidence, not proof).
- I found no 2026 confirmation of whether IBM Kookaburra shipped, IBM's advantage claim was verified, or IQM's first Halocene shipped.

## 2. Industry activity: OP, PwC, IBM finance members, IQM hardware, VTT, the Finnish strategy and insurers

### Takeaway
Finland is a hardware-producing quantum nation:
- IQM is domestic and announced an IPO in Feb 2026.
- VTT has 5, 20 and 50-qubit IQM machines, with 150 qubits due mid-2026 and 300 in late 2027.
- Aalto has its own 20-qubit system.
- There is a 2025–2035 national strategy.

OP is the most active Finnish financial institution in quantum. Its activity includes a July 2026 joint quantum and AI unit with Qutwo (about 60 specialists by mid-2027), co-hosting quantum hackathons with IQM, and internal training. Global finance players (HSBC, JPMorgan) have run hardware experiments but explicitly claim no quantum advantage.

### Cited findings

**OP Financial Group (OP Pohjola)**
- OP Pohjola and Qutwo Oy announced a joint quantum computing and AI research unit in Helsinki on 23 Jul 2026:
  - It aims at "quantum-ready AI" for banking and insurance, with stated focus areas of fraud detection, risk management and investment optimisation.
  - The plan is about 60 specialists by mid-2027, a figure attributed to OP CEO Timo Ritakallio.
  - Qutwo is led by Peter Sarlin (formerly of Silo AI); its founders are described as pioneers behind IQM and Silo AI.
  - Sources: [Global Finance](https://gfmag.com/technology/op-and-qutwo-debut-quantum-computing-partnership/); [Windsor Drake tracker](https://windsordrake.com/market-intelligence/strategic-partnerships/op-pohjola-strategic-partnership-2026-07-23)
- OP has a quantum and AI research centre led by Juha Vesanto. Activities include an OP Quantum Computing Summer Camp and a follow-up "QC Base Camp". Vesanto's LinkedIn lists OP Pohjola as a Quantum x Finance Hackathon partner (kick-off 17 Sep, Hanken). Source: [Juha Vesanto LinkedIn](https://fi.linkedin.com/in/juha-vesanto-8495a)
- A secondary source reports that "Quantum Hack 2026" in Otaniemi (5–7 Jun 2026) had challenges from OP Pohjola, IQM and QMill. Source: [tech-insider.org (secondary)](https://tech-insider.org/fi/suomen-kvanttitietokone-50-kubittia-iqm-2026/)
- At a Finnish Quantum Days 2026 pre-event co-organised by OP, IQM and CSC, OP's Ilmo Salmenperä presented how OP is "exploring the path towards quantum advantage in real-world financial use cases". This comes via search summary of a LinkedIn source. Source: [Satu Salminen LinkedIn](https://fi.linkedin.com/in/salminensatu)
- A LinkedIn post lists OP Pohjola and IQM as partners in a Finnish quantum hackathon whose topics included "simulation of financial and climate risks". The date is unconfirmed. Source: [Satu Salminen LinkedIn](https://fi.linkedin.com/in/salminensatu)

**IBM Quantum and finance**
- HSBC and IBM, 25 Sep 2025:
  - They called it the "first known quantum-enabled algorithmic bond trading" trial, run on IBM Heron.
  - The result was up to a 34% improvement in predicting fill probability, using production-scale European corporate bond data.
  - It did not involve live trading. The paper notes that hardware noise may have contributed, and the authors did not claim quantum advantage.
  - Sources: [The Quantum Insider](https://thequantuminsider.com/2025/09/25/hsbc-demonstrates-quantum-enabled-algorithmic-trading-with-ibm/); [PostQuantum critique](https://postquantum.com/quantum-research/hsbc-ibm-quantum-advantage/)
- JPMorganChase with Quantinuum, Argonne, ORNL and UT Austin published certified randomness in Nature on 26 Mar 2025. It used a 56-qubit Quantinuum H2 (trapped ion, not IBM) and produced 71,313 bits of certified entropy. Source: [JPMorgan](https://www.jpmorgan.com/technology/news/certified-randomness)
- IBM co-authored the Chakrabarti threshold paper with Goldman Sachs and co-developed IQAE (see section 1).

**IQM hardware and cloud**
- IQM is headquartered in Espoo and builds superconducting full-stack systems. It announced an IPO on 23 Feb 2026 at an estimated $1.8B valuation (per Wikipedia, so check the primary source). Source: [Wikipedia](https://en.wikipedia.org/wiki/IQM_Quantum_Computers)
- IQM Resonance launched in Mar 2024. It is a cloud service sold in time-slot subscriptions and hosted in Espoo and Munich. Garnet became available on Amazon Braket in May 2024. Sources: [The Quantum Insider](https://thequantuminsider.com/2024/03/19/iqm-quantum-computers-launches-iqm-resonance-a-cloud-service-to-advance-quantum-exploration-and-research/); [Open Quantum aggregator](https://www.openquantum.com/providers/iqm)
- Device figures from an aggregator, not IQM's own spec sheet: Garnet has 20 qubits and Emerald 54 qubits, with median CZ fidelity about 99.5%. Source: [Open Quantum](https://www.openquantum.com/providers/iqm)
- IQM product lines are Spark (small, education), Radiance (NISQ, 54/150 qubits), Halocene (QEC, 150 qubits targeted for end-2026) and the Crystal processor family (see section 1). Source: [The Quantum Insider on Halocene](https://thequantuminsider.com/2025/11/13/iqm-launches-a-new-quantum-computer-product-line-for-error-correction/)
- At MIT iQuHACK 2026, IQM sponsored a challenge on its 56-qubit computer. IQM's Madrid hackathon (Dec 2025) gave awards for "Best Quantum Innovation, Best Technical Implementation, Crowd Favorite", with a 3-minute demo plus Q&A. Sources: [Brown Engineering](https://engineering.brown.edu/news/2026-02-19/2026-mit-iquhack); [IQM Madrid event](https://meetiqm.com/?p=14052)

**VTT and Aalto**
- IQM previously delivered 5, 20 and 50-qubit machines to VTT. In May 2025 IQM won VTT's tender for a 150-qubit system (due mid-2026) and a 300-qubit system (late 2027, two 150-qubit QPUs), both on the Radiance platform:
  - The 300-qubit system is purpose-built for QEC experiments.
  - Funding is a €70M special government grant (2024).
  - The machines will be integrated with Finnish HPC and include a cloud platform for businesses and researchers.
  - Sources: [BusinessWire, 19/20 May 2025](https://www.businesswire.com/news/home/20250519294177/en/IQM-to-Deliver-World-leading-300-qubit-Quantum-Computer-to-Finland); [The Quantum Insider](https://thequantuminsider.com/2025/05/20/iqm-quantum-computers-to-supply-finland-with-a-superconducting-300-qubit-quantum-computer/)
- Aalto Q20 is a 20-qubit IQM superconducting machine owned by Aalto and funded by the Research Council of Finland (2022–2026):
  - Aalto is working with CSC to integrate it with the LUMI supercomputer for EU research access.
  - It is described as operational by Mar 2026. I could not confirm that it is "Radiance"-branded or part of LUMI-Q; LUMI-Q's IQM machine is a separate Radiance 24-qubit system in Ostrava.
  - Sources: [Aalto news](https://www.aalto.fi/en/news/aalto-university-unveils-aaltoq20-a-state-of-the-art-quantum-computer-for-educating-quantum-talent); [Quantum Computing Report](https://quantumcomputingreport.com/iqm-deploys-20-qubit-quantum-computer-at-aalto-university/amp/)

**Finland's national strategy**
- "Finland's Quantum Technology Strategy 2025–2035" (Ministry of Economic Affairs and Employment, published 24 Apr 2025, Publication 2025:18):
  - It was prepared by a working group chaired by VTT CEO Antti Vasara.
  - It proposes eight measures, including a network-style quantum competence centre and access to quantum computers combined with AI and HPC.
  - It notes that Finland is one of the few countries able to produce entire quantum computers.
  - A secondary summary cites targets of €3B in turnover and 10,000 jobs by 2035 (unverified against the PDF).
  - Sources: [Finnish Government](https://valtioneuvosto.fi/en/-/1410877/strategy-quantum-technology-is-finland-s-new-driver-of-growth-and-builder-of-a-sustainable-future); [The Quantum Insider](https://thequantuminsider.com/2025/04/25/finlands-quantum-strategy-published-outlines-eight-measures-to-strengthen-nations-leadership-position-in-quantum/)

**Insurers**
- AXA started exploring quantum technologies in 2020 (Roland Scharrer, group chief data and emerging technology officer). Munich Re set up a Quantum Technology & Application Consortium with nine German companies and spoke on optimising reinsurance (Andreas Nawroth). Source: [Physics World conference report (undated)](https://physicsworld.com/a/commercializing-quantum-technologies-the-risks-and-opportunities/)
- Allianz invested in 1QBit via Allianz X, as cited in the 2026 insurance literature review. Source: [Duncker & Humblot](https://elibrary.duncker-humblot.com/article/76791/quantum-computing-in-the-insurance-industry-insights-from-the-literature)
- Hogan Lovells (2026) frames quantum for insurers mainly as a cryptographic and operational-resilience risk. UK and EU regulators are not mandating quantum-safe measures yet but expect forward-looking governance. Source: [Hogan Lovells](https://hlc.com/en/publications/emerging-risks-in-2026-preparing-for-the-legal-and-regulatory-implications-of-quantum)

**Market sizing (treat with caution)**
- McKinsey Quantum Technology Monitor 2026 (late Apr 2026) says quantum computing could create up to $2.7T of economic value by 2035 across industries. Source: [McKinsey](https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/mckinsey-quantum-technology-monitor-2026-a-commercial-tipping-point)
- The financial-services figure of $400–600B by 2035 is attributed to McKinsey (apparently from the June 2025 Monitor). An independent analyst argues that the slide's arithmetic cannot be reproduced and that it blends quantum and AI impact. A separate figure of $622B (WEF/McKinsey) also circulates. Sources: [PostQuantum critique](https://postquantum.com/quantum-computing/mckinsey-quantum-finance-600b/); [Business Today on WEF $622B](https://www.businesstoday.in/amp/technology/news/story/wef-quantum-technologys-622-bn-opportunity-could-transform-banking-and-finance-484832-2025-07-16)

### Inferences
- OP's public quantum vocabulary is "quantum-ready", "path towards quantum advantage" and "real-world financial use cases". Tulva's "quantum-ready pricing engine benchmarked honestly" mirrors that framing closely. OP also does insurance through its Pohjola Insurance arm, so a parametric flood cover is in OP's own product domain.
- Showing results on Finnish hardware (IQM via Resonance, Aalto Q20 via LUMI or CSC) lines up with the national strategy measure on access to quantum computing combined with HPC, which matters to VTT and IQM.
- The 2026 challenge text explicitly asks for "risk modelling" plus ESG. Flood climate-adaptation cover fits both.

### Gaps
- I found no OP primary press release on OP–IQM or on the Qutwo unit (only Global Finance and a tracker).
- I found no specific PwC Finland quantum offering, and nothing connecting Gholamreza Anbarjafari to PwC or quantum. Searches returned only PwC Italy, Germany and Acceleration Center material: [PwC DE newsletter](https://www.pwc.de/de/newsletter/quantum-computing.html).
- I found no Zurich-specific insurer quantum activity.
- I found no IBM Quantum Network finance member list page; the HSBC and JPMorgan items stand alone.
- The VTT 150-qubit mid-2026 delivery status is unconfirmed.
- I did not open the McKinsey 2025 Monitor primary PDF.

## 3. Qrisp: what it is, QAE/QMCI features and IQM backend support

### Takeaway
Qrisp is a high-level Python quantum programming framework with built-in Iterative QAE and Quantum Monte Carlo Integration primitives. IQM maintains an official `iqm.qrisp_iqm` backend that transpiles Qrisp circuits to IQM native gates. Running Tulva in Qrisp on IQM is therefore a supported path, which explains the IQM contact's recommendation.

### Cited findings
- Qrisp 0.6 added Quantum Monte Carlo Integration built on Iterative QAE. The release notes position it for integrals without analytic solutions in chemistry, many-body physics and finance. Source: [Qrisp 0.6 changelog](https://qrisp.eu/general/changelog/0.6.html)
- The QMCI tutorial integrates f(x)=x² over [0,1]. It encodes "points under the curve" in an oracle and estimates their ratio with AE. Source: [Qrisp QMCI tutorial](https://qrisp.eu/general/tutorial/QMCItutorial.html)
- The IQAE primitive targets accuracy ε and confidence α, and the docs claim it uses a fraction of the resources of canonical QAE. Sources: [Qrisp IQAE reference](https://qrisp.eu/reference/Primitives/IQAE.html); [source](https://qrisp.eu/_modules/qrisp/alg_primitives/iterative_qae.html)
- IQM backend: `iqm.qrisp_iqm.IQMBackend`:
  - `run()` transpiles standard Qrisp gates to IQM's native gate set, handles layout and SWAP routing, and submits via the IQM Client API. `run_async()` is also available.
  - Devices are selected like `IQMBackend(device_instance="garnet")`.
  - Sources: [IQM docs, Qrisp on IQM user guide](https://docs.iqm.tech/iqm-client/user_guide_qrisp/index.html); [qrisp_iqm API](https://docs.iqm.tech/iqm-client/_sources/qrisp_iqm_api.rst)
- Qrisp origin: it was developed at Fraunhofer FOKUS (Berlin) and is now an Eclipse Foundation project ("Eclipse Qrisp"). **[recalled; a related talk is at [LRZ ZKI 2025 slides](https://zki2025-herbsttagung.lrz.de/pdf/slides/meier.pdf), not opened]**

### Inferences
- I found no documented example of IQAE or QMCI running on IQM hardware, so Tulva running MLAE Grover powers on IQM via Qrisp would be a genuine, demonstrable contribution.
- Expect deep Grover powers (m ≥ 2–4) to decohere on 20–54-qubit NISQ devices. The low-depth / power-law AE literature (Giurgica-Tiron) is the citation for choosing a shallow Grover schedule.
- Qrisp's built-in IQAE is not MLAE. If Tulva uses MLAE with a custom Grover schedule, the team implements the likelihood step itself, which is worth stating as a technical contribution.

### Gaps
- I did not verify Qrisp's Eclipse governance date or current version, or whether `qrisp_iqm` supports Resonance-hosted Emerald or Radiance specifically.

## 4. What the jury organisations publicly emphasise, and hackathon criteria

### Takeaway
No public jury list or judging criteria for the 2026 Quantum x Finance hackathon could be retrieved. The Ultrahack page did not render, and the Hanken page omits them. Prior Hanken hackathons (2023, with Ultrahack, IBM, IQM and VTT among the partners) were won by a business- and ESG-oriented concept, which suggests that business case and impact weigh heavily alongside the technical work.

### Cited findings
- 2026 event: 8–10 Oct 2026 (16:00 8 Oct to 14:00 10 Oct) at Hanken, Arkadiankatu 22. The kick-off was 17 Sep 2026, registration was via Ultrahack, and the deadline was 27 Sep:
  - Challenge: "Explore how quantum computing can be applied to financial systems while integrating AI and ESG considerations. Place quantum methods at the core, rethinking optimisation, risk modelling, and data integration."
  - Accepted formats: concept, prototype, application or quantum model.
  - Source: [Hanken calendar](https://www.hanken.fi/en/calendar/quantum-x-ai-hackathon-shape-future-finance-0)
- 2023 precedent: the fourth Hanken Quantum Hackathon, 24–26 Nov 2023, had 14 teams and was arranged by Hanken Quantum Lab and Ultrahack with VTT, KPMG, IBM, Bluefors, IQM, Hartwall and Business Finland:
  - The winner, "Sustainify", built an ESG reporting platform for Finnish SMEs. Quantum appeared only as a long-term vision.
  - The prize was €2,000 and a pitch to KPMG.
  - Source: [Hanken news, 5 Dec 2023](https://hanken.fi/en/news/hanken-quantum-hackathon-winners-want-help-businesses-grappling-esg-reporting)
- Comparable criteria elsewhere:
  - IBM co-run NTU hackathon (2025): complexity of quantum technology, originality, teamwork and presentation, and benefit to society. Source: [NTU-IBM Quantum Hub](https://quantum.ntu.edu.tw/?p=9805)
  - IQM Madrid (Dec 2025): Best Quantum Innovation, Best Technical Implementation and Crowd Favorite, with a 3-minute demo plus Q&A. Source: [IQM](https://meetiqm.com/?p=14052)
- IBM's public emphasis is "verified quantum advantage" via a public tracker that compares against the best classical methods, plus utility-scale hardware such as Nighthawk. Source: [Next Platform](https://www.nextplatform.com/2025/11/12/ibm-lets-fly-nighthawk-and-loon-qpus-on-the-way-to-quantum-advantage/)
- OP's emphasis is "quantum-ready AI" for cutting costs and competitiveness in banking and insurance, and "path towards quantum advantage in real-world financial use cases". Sources: [Global Finance](https://gfmag.com/technology/op-and-qutwo-debut-quantum-computing-partnership/); [LinkedIn](https://fi.linkedin.com/in/salminensatu)
- VTT and the government emphasise Finnish sovereignty and capability across the full stack, and access combined with HPC and AI. Source: [Finnish Government](https://valtioneuvosto.fi/en/-/1410877/strategy-quantum-technology-is-finland-s-new-driver-of-growth-and-builder-of-a-sustainable-future)

### Inferences (pitch mapping, judgement not sourced fact)
- **OP (Toikka):** customer value (affordable parametric flood cover for Finnish households and SMEs or municipalities), fit with Pohjola Insurance, and the "quantum-ready" language from OP's own Qutwo announcement.
- **IQM (Steinmann):** real IQM hardware runs via Qrisp (their recommended stack), honest noise characterisation, and the Halocene and FT-2030 path as the scaling story.
- **IBM (Seesto):** a Qiskit or IBM Heron/Nighthawk comparison, and an honest classical baseline in the spirit of IBM's advantage tracker. Do not claim advantage.
- **VTT (Mehtola):** Finnish ecosystem (VTT Q50/150, Aalto Q20 via LUMI or CSC), HPC+QC hybrid, and climate-risk relevance.
- **PwC (Anbarjafari):** business case, regulatory angle (Solvency II internal models, EIOPA, transparency of parametric triggers), and governance or explainability of model risk.

- **Team-internal source (project CLAUDE.md, not public web):**
  - The 2026 criteria given to the team are Impact, Business plan, Team progress during the event, Innovativeness, and Methodological capability (demo or simulation; quantum in practice or theory).
  - The pitch is 3 minutes plus 3 minutes of Q&A.
  - The project config names the Aalto Q20 backend `radiance20` (IQM, 20 qubits, CZ + PRX native gates) with a two-qubit gate budget of about 50. This suggests Q20 is a Radiance-class device, though I found no public IQM or Aalto source saying so.
  - For calibration, the IonQ low-depth AE demo saw accuracy keep improving at more than 90 two-qubit gates ([ar5iv](https://ar5iv.labs.arxiv.org/html/2109.09685)). That was trapped-ion hardware, so it is not directly comparable to the Q20.

### Gaps
- I could not retrieve the 2026 jury list, criteria or prizes from public sources; the Ultrahack page did not render. The criteria above come from the team's own brief.
- I found no public statements by the individual jurors (Toikka, Anbarjafari, Steinmann, Seesto, Mehtola). Their names and titles are unverified in this research.
- I found no record of 2024 or 2025 Hanken hackathon winners or criteria.

## 5. Business positioning: defensible "quantum-ready" claims vs hype

### Takeaway
Defensible today:
- A correct QAE formulation of a real insurance pricing quantity.
- Validation against exact and classical MC values.
- Hardware-executed circuits with measured error.
- Resource estimates that extrapolate to fault-tolerant machines.
- A modular engine that can swap in better AE variants or hardware.

Not defensible: any claim of current speed or cost advantage, or of "exponential" speedup. Even the field's flagship industry studies (HSBC/IBM, Chakrabarti) explicitly avoid claiming advantage.

### Cited findings
- The QAE speedup is quadratic in oracle calls only. Practical advantage needs about 8k logical qubits and 54M T-depth at MHz-scale clocks for realistic derivatives. Source: [Chakrabarti et al.](https://arxiv.org/abs/2012.03819v2)
- Quadratic speedups may not pay off on early fault-tolerant hardware. **[recalled]** [Babbush et al. 2021](https://arxiv.org/abs/2011.04149)
- For catastrophe insurance specifically, classical methods beat QAE when analytic access exists, and discretisation is the bottleneck. Source: [Kirke 2026](https://arxiv.org/abs/2603.15664)
- HSBC/IBM avoided claiming advantage and noted that noise may explain some of the gains. Source: [PostQuantum](https://postquantum.com/quantum-research/hsbc-ibm-quantum-advantage/)
- McKinsey's finance value estimates are contested and blend quantum with AI. Source: [PostQuantum](https://postquantum.com/quantum-computing/mckinsey-quantum-finance-600b/)
- Roadmap timing (IBM Starling 2029, IQM FT by 2030) consists of vendor targets. Sources: [The Quantum Insider/IBM](https://thequantuminsider.com/2025/06/10/ibm-offers-roadmap-toward-large-scale-fault-tolerant-quantum-computer/); [The Quantum Insider/IQM](https://thequantuminsider.com/2025/11/13/iqm-launches-a-new-quantum-computer-product-line-for-error-correction/)

### Inferences (suggested claim ladder)
1. **Safe:** "We built a working QAE (MLAE) estimator for a parametric flood-trigger probability, validated against the exact value and classical Monte Carlo, and executed on IQM and IBM hardware with measured error."
2. **Safe:** "Query complexity: the error scales as about 1/N oracle calls vs 1/sqrt(N) for MC in the ideal model. Here is our measured curve on the simulator and how noise bends it on hardware."
3. **Safe, with numbers:** a resource extrapolation of qubits, Grover depth and T-count needed for a realistic multi-region, multi-variable cover, compared with the Chakrabarti threshold.
4. **Hedged:** "Quantum-ready: the pricing engine's interface is hardware-agnostic, so when fault-tolerant machines arrive (vendor targets 2029–2030) the same model plugs in."
5. **Avoid:** "faster or cheaper than classical today", "exponential speedup", or "quantum advantage achieved".
- The near-term business value of Tulva rests on the classical product (parametric flood cover, transparent trigger, fast payout). Quantum is an R&D option on future pricing and capital-modelling efficiency, which mirrors how OP frames its Qutwo unit.

### Gaps
- I found no published cost-per-query comparison of IQM Resonance or IBM pricing vs cloud CPU for MC, so any cost-advantage claim is unsupported.
- I found no regulator (EIOPA, FIN-FSA) statement on the use of quantum methods in pricing or internal models.
