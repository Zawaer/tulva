# Solvency II treatment of flood catastrophe risk: Finland and the Nordics

Research notes for the Tulva pitch (parametric spring-flood index cover for Finnish insurers). Current as of 8 October 2026.

**Headline verdict on the pitch claim "EIOPA: 0 % Nordic flood correlation":** It is broadly right, but the framing is wrong in two ways that matter. Fix both before the pitch.

1. **Today (until 29 Jan 2027) Finland has no flood parameter at all. It does not have a 0 % one.** Finland is not a flood region in Annex VII of Delegated Regulation (EU) 2015/35. As an EU Member State it is also excluded from the premium-based "other regions" flood charge, so Finnish flood risk currently attracts **zero** standard-formula flood capital.
2. **From 30 Jan 2027, Delegated Regulation (EU) 2026/269 adds Finland to flood.** The flood risk factor is 0.04 % and there are 19 risk zones. The **country-to-country flood correlation between Finland and every other country, including SE, NO and DK, is 0.00**. EIOPA explicitly considered 25 % for shared rivers and snowmelt floods and rejected it (EIOPA-BoS-24/462, para 4.70). **Within Finland, however, the zone-to-zone correlations are not zero.** They range from 0 to 1.00 (mean off-diagonal about 0.27, and about one third are 0.50 or more).

Suggested accurate wording: *"Solvency II's new Finnish flood module (applies from Jan 2027) sets Finland–Sweden/Norway/Denmark flood correlation at 0 %. EIOPA considered 25 % for snowmelt floods and rejected it (EIOPA Opinion BoS-24/462 §4.70; Del. Reg. 2026/269, Annex IV). Until then, Finnish flood carries no standard-formula capital at all."*

---

## Q1. Standard formula flood sub-module: does it cover Finland, which countries, what correlations?

### Takeaway
Under the rules in force today (2015/35 as amended to 2020), Finland has a windstorm factor (0.04 %) but no flood factor. Because Finland is in Annex XIII, it also escapes the premium-based "other regions" flood charge, so Finnish flood risk is simply absent from the standard formula. Delegated Regulation (EU) 2026/269 replaces Annex VII from 30 Jan 2027. It adds FI (0.04 %), SE (0.045 %), NO (0.05 %), DK (0.04 %), NL (0.035 %), IE (0.17 %) and LU (0.13 %), with a flood country-correlation of 0.00 between Finland and every other country.

### Cited findings

**Legal architecture (Delegated Regulation (EU) 2015/35)**
- Art. 120(1): the natural catastrophe risk sub-module consists of windstorm, earthquake, flood, hail and subsidence sub-modules. — [Art. 120, legislation.gov.uk (EU text as at 31 Jan 2020)](https://www.legislation.gov.uk/eur/2015/35/article/120/2020-01-31?view=plain)
- Art. 123(1) aggregates the flood capital over "all possible combinations (r, s) of the regions set out in Annex VII" using CorrFL(r,s) "as set out in Annex VII", plus SCR(flood,other) for regions outside Annex XIII. — [Art. 123](https://www.legislation.gov.uk/eur/2015/35/article/123/2020-01-31?view=plain)
- Art. 123(2)–(4) takes the capital per region as the larger of two scenarios:
  - Scenario A: an instantaneous loss of 65 % of the specified flood loss, followed by a second loss of 45 %.
  - Scenario B: 100 % followed by 10 %.
  - In both cases the amounts are gross ("without deduction of the amounts recoverable from reinsurance contracts and special purpose vehicles"), and the capital is the resulting loss in basic own funds. — [Art. 123](https://www.legislation.gov.uk/eur/2015/35/article/123/2020-01-31?view=plain)
- Art. 123(5): specified flood loss = sqrt(Σ_i Σ_j Corr(flood,r,i,j) · WSI_i · WSI_j). The zones come from Annex IX and the zone correlations from **Annex XXIV**. — [Art. 123](https://www.legislation.gov.uk/eur/2015/35/article/123/2020-01-31?view=plain)
- Art. 123(6): WSI(flood,r,i) = Q(flood,r) · W(flood,r,i) · SI(flood,r,i). Q is the country factor (Annex VII) and W is the zone risk weight (Annex X). An undertaking may instead use a "lower amount" equal to the sum of potential losses after policy limits. — [Art. 123](https://www.legislation.gov.uk/eur/2015/35/article/123/2020-01-31?view=plain)
- Art. 123(8)–(9): flood risk "where the risk is not situated in one of the regions set out in Annex XIII" is charged on a premium basis. — [Art. 123](https://www.legislation.gov.uk/eur/2015/35/article/123/2020-01-31?view=plain)
- **Annex XIII** ("List of regions for which natural catastrophe risk is not calculated based on premiums") lists "Member States of the European Union", Andorra, Iceland, Liechtenstein, Monaco, Norway, San Marino, Switzerland and Vatican City. Finland, as an EU Member State, therefore gets no premium-based flood charge either. — [Annex XIII](https://www.legislation.gov.uk/eur/2015/35/annex/XIII/2020-01-31?view=plain)
- Art. 126(1)(a): the two consecutive events in the scenarios are assumed independent. Art. 126(2): reinstatements must be modelled as realistic management actions. — [Art. 126](https://www.legislation.gov.uk/eur/2015/35/article/126/2020-01-31?view=plain)
- Annex numbering confirmed from 2026/269: Annex V = windstorm, Annex VII = "Parameters for the flood risk sub-module", Annex IX = risk-zone mapping, Annex X = risk weights, Annex XXIV = flood zone correlations. — [Delegated Reg. (EU) 2026/269, compiled text (LawPlayer, from EUR-Lex)](https://lawplayer.com/eu/act/32026R0269); [EUR-Lex entry](https://eur-lex.europa.eu/legal-content/EN/PIN/?uri=oj%3AL_202600269)

**Flood countries before and after 2027**
- Before (2015/35 as amended by 2019/981 and 2020/442): flood factors existed for AT, BE, BG, CZ, CH/LI, DE, FR, HU, IT, PL, RO, SI, SK and UK. No Nordic country had one. — [EIOPA Opinion BoS-24/462, para 4.24–4.25 and Nordic section ("The peril flood is not currently included in the SF for the Nordics")](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- After: **Delegated Regulation (EU) 2026/269 of 29 Oct 2025**, Art. 1(134), replaces Annex VII with the text in its Annex IV. The new "Regions and flood risk factors" table is:

  | Country | Factor | Country | Factor | Country | Factor |
  |---|---|---|---|---|---|
  | AT | 0.13 % | BE | 0.12 % | BG | 0.15 % |
  | CZ | 0.25 % | CH/LI | 0.30 % | DE | 0.20 % |
  | FR | 0.12 % | HU | 0.25 % | IT | 0.15 % |
  | PL | 0.16 % | RO | 0.13 % | SI | 0.30 % |
  | SK | 0.35 % | UK | 0.12 % | **LU** | **0.13 %** |
  | **IE** | **0.17 %** | **NL** | **0.035 %** | **NO** | **0.05 %** |
  | **SE** | **0.045 %** | **FI** | **0.04 %** | **DK** | **0.04 %** |

  New entries are in bold. — [2026/269 compiled text](https://lawplayer.com/eu/act/32026R0269)
- 2026/269, Art. 2: "It shall apply from 30 January 2027." — [2026/269](https://lawplayer.com/eu/act/32026R0269). Secondary sources give OJ publication as 18 Feb 2026. — [Fenion](https://fenion.com/en/blog/solvency-ii-inkrafttreten-der-delegierten-verordnung-eu-2026-269/)
- 2026/269 also inserts Art. 120(1a), a legal definition of flood. It covers riverine/fluvial, pluvial/surface-water and flash floods; "flood does not include storm surge". Snowmelt-driven river flooding is covered as fluvial flooding. — [2026/269](https://lawplayer.com/eu/act/32026R0269)
- 2026/269 Art. 1(31) changes the sum insured in Art. 123(7) to SI(property) + SI(onshore-property) + **1.5** × SI(motor). — [2026/269](https://lawplayer.com/eu/act/32026R0269)

**Country correlation matrix for flood (new Annex VII, from 30 Jan 2027)**
- The FI row is 0.00 against every column (AT, BE, BG, CH, CZ, DE, FR, HU, IT, PL, RO, SI, SK, UK, LU, IE, NL, NO, SE, DK) and 1.00 on the diagonal. The SE, NO and DK rows are likewise all 0.00 off-diagonal. — [2026/269, Annex IV "Flood risk correlation coefficients for regions"](https://lawplayer.com/eu/act/32026R0269)
- The only non-zero correlations involving new countries are NL–BE 0.25, NL–DE 0.25, LU–BE/DE/FR 0.25 and IE–UK 0.25. Among the older countries, values reach 0.75 (e.g. AT–DE, CZ–PL, CZ–SK, DE–PL). — [2026/269](https://lawplayer.com/eu/act/32026R0269)

**EIOPA's rationale for 0 % (the primary source for the pitch claim)**
- Para 4.70 (Finland): "A country correlation of 0 % with all existing countries ... is proposed for Finland." The reason given is that "there are no shared boarders [sic] of any significance or any shared rivers." The 0 % also applies to "all the countries added during this exercise including the other Nordic countries." — [EIOPA Opinion EIOPA-BoS-24/462, 30 Jan 2025, pp. 36–37](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- The same paragraph records that the subgroup discussed "the shared rivers with SE or a snowmelt induced fluvial flood could imply a correlation of 25 %." It rejected this because the shared rivers are in very unpopulated areas and "the snowmelt induced fluvial flood is not considered significant by the subgroup". It added that "the model vendor results support this." Near-identical text appears for Norway (4.61), Sweden (4.66) and Denmark (4.87). — [EIOPA Opinion BoS-24/462](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)

**Finnish zone structure, weights and intra-Finland correlation (from 2027)**
- EIOPA para 4.68: Finnish flood zones reuse the existing windstorm national conversion table in Annex IX. It is based on the earlier NUTS3 mapping to 2-digit postal-code areas. CRESTA zones (about 100) were rejected as "too accurate" for windstorm and not accurate enough for flood in the north. Para 4.69: zones and zonal correlations "are based on one model vendor". — [EIOPA Opinion BoS-24/462, p. 36](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- 2026/269 inserts "Correlation coefficients for flood risk in the Republic of Finland", a 19 × 19 matrix, into Annex XXIV. I parsed it (361 cells; 342 off-diagonal):
  - min 0.00, max 1.00, mean 0.27, median 0.00;
  - 56.7 % of off-diagonal pairs are 0.00 and 33.3 % are ≥ 0.50.
  - There are clear clusters. Zones 3/5/13/15/16 are mutually 0.75–1.00, and zones 6/7/8/9/12 are mutually 0.75–1.00. Zones 1 and 11 are uncorrelated with everything. — [2026/269](https://lawplayer.com/eu/act/32026R0269)
- Finnish flood risk weights in the new Annex X (2026/269 Annex VIII), zones 1–19:

  | Zone | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | Weight | 0.5 | 0.7 | **7.7** | 1.5 | 1.3 | 0.9 | **5.9** | 1.9 | 2.8 | 2.0 |

  | Zone | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
  |---|---|---|---|---|---|---|---|---|---|
  | Weight | **5.5** | 2.4 | 3.5 | 1.9 | 2.5 | 1.9 | 2.7 | **8.9** | 0.3 |

  Column alignment is inferred from the table layout (see Gaps). — [2026/269](https://lawplayer.com/eu/act/32026R0269)

**How EIOPA calibrated Finland's 0.04 %**
- Para 4.67:
  - Exposure: the single vendor model used proxy exposure from open building data per postal code. This was reconciled with protection-gap exposure data and with an ad hoc questionnaire to the largest undertakings based on QRT S.21.03.
  - Range: the model gave 0.039 %–0.064 %. A "shadow model" gave 0.035 %–0.045 %.
  - Choice: EIOPA took the lower end, 0.040%, because protection records did not capture "Finnish experience-based measures such as controlling of lake reservoirs or use of flood water running upstream of exposed areas".
  - Surface-water flooding was noted as pushing the factor up.
  — [EIOPA Opinion BoS-24/462, p. 36](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- Para 4.52–4.54: the initial Nordic vendor results "overestimated the risk of flood" because they used GDP-based exposure without limits or deductibles. Nordic factors were therefore set by expert judgement, with results rescaled against Germany (0.2 %) and other SF countries. — [EIOPA Opinion BoS-24/462, pp. 33–34](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- Footnote 18: "Finland had also considered to modify the current zoning from own mapping to CRESTA zones but the number of CRESTA zones for Finland is too high." — [EIOPA Opinion BoS-24/462](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)

**Windstorm (where Finland is already included)**
- Finland was added to windstorm in the 2017/2018 recalibration at 0.04 %. — [EIOPA Opinion BoS-24/462, para 4.11](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- 2026/269 Annex II keeps FI windstorm at 0.04 %. The other Nordic factors are DK 0.25 %, NO 0.08 % and SE 0.085 %. — [2026/269](https://lawplayer.com/eu/act/32026R0269)
- The Annex V windstorm correlation matrix (as amended by 2019/981) gives **FI–NO 0.25, FI–SE 0.25** and FI–DK 0.00. It also gives NO–SE 0.50, DK–SE 0.50 and DK–NO 0.50. So Solvency II does correlate Finland with its neighbours for windstorm, but not for flood. — [Annex V table 2, legislation.gov.uk](https://www.legislation.gov.uk/eur/2015/35/annex/V/table/2/group/1/2020-01-31)

### Inferences
- "Regulators assume independence" is accurate only **between countries**. Within Finland the standard formula, built from a vendor model, already assumes strong positive zone correlation. Up to 100 % links many zones, which looks consistent with shared lake–river systems. Tulva's "joint risk" story should therefore say that the SF imposes **0 % cross-border** dependence and only **coarse, single-vendor** intra-Finland dependence, rather than claiming that EIOPA ignores correlation.
- The cross-border 0 % matters mainly to **Nordic groups** writing in FI + SE + NO (e.g. If/Sampo, Fennia's partner networks, Gjensidige/Tryg if present). For them the flood SCR from different countries diversifies as fully independent. If spring floods are in fact co-driven by Nordic snowpack, the SF understates group flood capital, which is a legitimate ORSA "deviation from SF assumptions" topic (see Q3).
- Scale of the charge (illustrative arithmetic, not sourced):
  - Example: €10 bn of flood-covered sums insured concentrated in zone 18 (weight 8.9) gives WSI ≈ 0.0004 × 8.9 × €10 bn ≈ €35.6 m. The gross scenario loss is then about 110 % of that (both scenarios total 110 %), ≈ €39 m before reinsurance.
  - The same exposure in zone 19 (weight 0.3) gives ≈ €1.3 m.
  - So location within Finland drives the charge far more than the national factor.
- Because both scenarios total 110 %, the A (65 % + 45 %) versus B (100 % + 10 %) split matters mainly for **reinsurance recoveries**. A cover with a reinstatement or aggregate feature (two events) can affect which scenario binds.

### Gaps
- The FI column alignment in the Annex X weights table was inferred from row lengths in a compiled HTML version (DK has 11 zones, FI has 19). Verify against the official EUR-Lex PDF of 2026/269 Annex VIII.
- Not verified: the mapping of Finnish zones 1–19 to postal-code areas or regions (Annex IX, introduced by 2019/981 for windstorm). Needed to tell whether the high-weight zones 3, 7, 11 and 18 are e.g. Ostrobothnia, Lapland or Lakeland.
- The rendered Art. 120(2) formula (aggregation across perils) did not display in the text extraction. I could not confirm whether flood and windstorm are aggregated as independent (sum of squares).
- Not checked in full: whether 2026/269 also changed the Annex V windstorm correlation matrix. Its Annex II visibly replaces only the factor table.

---

## Q2. EIOPA nat-cat reassessments 2021–2025 and the Finland flood proposal

### Takeaway
EIOPA consulted in April 2024 and issued its final Opinion (EIOPA-BoS-24/462) on 30 Jan 2025. The Opinion proposed adding flood for FI, SE, NO, DK, NL, IE and LU. The Commission adopted these values unchanged in Delegated Regulation (EU) 2026/269 (29 Oct 2025), which applies from 30 Jan 2027.

### Cited findings
- 3 Apr 2024: EIOPA consulted on reassessed nat-cat parameters. Nine countries, including NL, IE and FI, were proposed for flood addition. Comments were due 20 Jun 2024 and an opinion to the Commission was due by end-2024. — [EIOPA consultation](https://www.eiopa.europa.eu/eiopa-consults-natural-catastrophe-risk-reassessments-standard-formula-2024-04-03_en); [Milliman summary](https://www.milliman.com/en/insight/2023-2024-reassessment-natural-catastrophe-risk-standard-formula)
- Milliman's consultation table: FI 0.04 % "considers flood control measures and expert judgement", DK 0.04 %, SE 0.045 %, NO 0.05 %, NL 0.035 %, IE 0.17 % and LU 0.13 %. Milliman notes a typo in the consultation's main document, which gave Sweden as 0.45 %. — [Milliman](https://www.milliman.com/en/insight/2023-2024-reassessment-natural-catastrophe-risk-standard-formula)
- 30 Jan 2025: final Opinion. It covers flood (3 countries recalibrated, 7 added), hail (DE, BE, LU raised), windstorm (Iceland and French overseas territories raised) and subsidence (FR raised, BE added). Wildfire, coastal flood and drought remain under monitoring. Risk weights were last updated in 2018. — [EIOPA press release](https://www.eiopa.europa.eu/eiopa-recommends-new-risk-factors-flood-windstorm-and-hail-risk-insurers-standard-formula-capital-2025-01-30_en); [Opinion page](https://www.eiopa.europa.eu/publications/opinion-20232024-reassessment-nat-cat-standard-formula_en)
- Opinion summary table (b) for flood:
  - Recalibrated: RO 0.13 / 0.3, BE 0.12 / 0.1, CZ 0.25 / 0.3.
  - Added: LU 0.13, IE 0.17, NO 0.05, FI 0.04, NL 0.035, DK 0.04, SE 0.045.
  - Assessed but not added: MT (not material) and PT.
  - FI, NO, NL, DK, SE and IE all received new aggregation matrices, risk zones and correlations. — [EIOPA Opinion BoS-24/462, pp. 2–4](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- During the Call for Evidence, the NCAs of FI, DK and SE argued that flood "might be material based on observations about impact of climate change, past loss experience and the results of undertakings internal models". — [EIOPA Opinion BoS-24/462, Nordic section](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- On 14 Mar 2025 EIOPA published a zonal calibration XLSX ("2023-2024 Reassessment Exercise of natcat risks Zonal Calibration"). — [Opinion page](https://www.eiopa.europa.eu/publications/opinion-20232024-reassessment-nat-cat-standard-formula_en)
- The Commission's July 2025 draft review of the Delegated Regulation led to 2026/269. It was adopted 29 Oct 2025 and applies from 30 Jan 2027, with recalibrated nat-cat capital requirements as a stated objective. — [Commission consultation news](https://finance.ec.europa.eu/news/commission-seeks-feedback-review-solvency-ii-delegated-regulation-2025-07-18_en); [2026/269](https://lawplayer.com/eu/act/32026R0269)
- EIOPA advises updating nat-cat parameters every 3–5 years. The SII review mandates periodic reassessment and recalibration where discrepancies are significant. — [Milliman](https://www.milliman.com/en/insight/2023-2024-reassessment-natural-catastrophe-risk-standard-formula)

### Inferences
- The next reassessment cycle (roughly 2027–2029) is the realistic window for Finnish stakeholders to argue for a non-zero FI–SE/NO spring-flood correlation, or for finer Finnish zoning. Tulva's joint-risk analytics could be pitched as evidence for that discussion.

### Gaps
- I did not read the zonal calibration XLSX. I found no published stakeholder comments specifically challenging the Nordic 0 %.

---

## Q3. How Finnish insurers compute nat-cat SCR, and ORSA obligations for risks outside the standard formula

### Takeaway
Sampo/If uses an approved (group) partial internal model. I could not verify the approach of OP Vakuutus, LähiTapiola, Fennia or Pohjola from primary sources. ORSA must cover all material risks, including climate scenarios. Directive (EU) 2025/2 tightens this from 30 Jan 2027.

### Cited findings
- Sampo applied in June 2023 for a Group Partial Internal Model (PIM), estimated to cut group SCR by up to EUR 0.3 bn. It builds on If's existing PIM. If and Topdanmark already used PIMs, while group SCR had been standard formula only. — [Sampo release Jun 2023](https://www.sampo.com/media/releases-and-news/2023/sampo-has-submitted-a-group-partial-internal-model-application/); [Inderes](https://www.inderes.fi/en/articles/what-partial-internal-model)
- The group supervisor changed to the Swedish FSA from 1 Oct 2023. That FSA approved the Group PIM, which has been used since Q2 2024 (first reported in the H1 2024 report). — [Sampo approval release 2024](https://www.sampo.com/media/releases-and-news/2024/sampo-has-received-approval-for-its-group-partial-internal-model/); [Sampo application to Swedish FSA](https://www.sampo.com/media/releases-and-news/2023/sampo-has-filed-a-group-partial-internal-model-application-to-the-swedish-fsa/)
- EIOPA's Opinion records that Nordic NCAs cited "results of undertakings internal models" as evidence of flood materiality. Some Nordic insurers' internal models therefore already capture flood. — [EIOPA Opinion BoS-24/462](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- EIOPA's April 2021 Opinion on climate change risk scenarios in ORSA (EIOPA-BoS-21-127) sets these expectations:
  - Climate risks should be integrated into governance, risk management and ORSA like other risks.
  - Undertakings should assess the materiality of their climate exposures.
  - Material risks should be tested under at least two long-term scenarios, one keeping warming below 2°C (preferably 1.5°C).
  — [EIOPA press release 19 Apr 2021](https://www.eiopa.europa.eu/eiopa-issues-opinion-supervision-use-climate-change-risk-scenarios-orsa-2021-04-19_en); [CMS summary](https://cms.law/en/int/regulatory-news/eiopa-opinion-on-the-supervision-of-the-use-of-climate-change-risk-scenarios-in-orsa)
- The 2 Aug 2022 Application Guidance on climate change materiality assessments and scenarios in ORSA gives worked non-life and life examples. It is non-binding. — [EIOPA](https://www.eiopa.europa.eu/media/news/eiopa-publishes-application-guidance-how-reflect-climate-change-orsa); [Arendt](https://www.arendt.com/news-insights/news/esg-in-the-insurance-sector-update-on-climate-change-materiality-assessments-and-climate-change-scenarios-in-the-orsa/)
- EIOPA's July 2025 monitoring exercise found that most in-scope insurers now include climate risk (physical and transition) in ORSA. It flagged data granularity and time-horizon limits. — [EIOPA, 23 Jul 2025](https://www.eiopa.europa.eu/eiopa-monitoring-exercise-marks-progress-integration-climate-change-considerations-insurers-risk-2025-07-23_sl)
- Directive (EU) 2025/2 (Solvency II review) must be transposed by 29 Jan 2027 and applied from 30 Jan 2027. — [FIN-FSA Solvency II page](https://www.finanssivalvonta.fi/en/regulation/regulatory-framework/solvency-ii/); [KPMG DE](https://klardenker.kpmg.de/financialservices-hub/regulatory-update/ueberarbeitete-solvency-ii-richtlinie-im-eu-amtsblatt-veroeffentlicht/); [Directive 2025/2](https://eur-lex.europa.eu/eli/dir/2025/2/oj/eng). Secondary sources say it embeds climate-change scenario analysis in ORSA. — [actuary.info](https://actuary.info/insights/solvency-ii-review-us-orsa-benchmark)

### Inferences
- Under the ORSA duty (Art. 45 of the Directive) insurers must assess how their risk profile deviates from SF assumptions. For a standard-formula Finnish insurer, a single-vendor 0.04 % factor plus 0 % cross-border correlation is an obvious deviation to evaluate in ORSA. Tulva's correlated spring-flood analytics fits naturally as an **ORSA / economic-capital input**, even where it buys little SF relief.
- PIM users like If can model flood dependence internally. For them the SF 0 % is irrelevant, and an index cover is valued on its internal-model effect, including basis-risk modelling (see Q4).

### Gaps
- No primary source found on whether OP Vakuutus, LähiTapiola, Fennia or Turva use the standard formula or an internal model for non-life nat cat, or whether If's PIM covers nat cat. Check each insurer's latest SFCR, section E.2/E.4.
- The "Article 45a" numbering for the climate-scenario requirement in Directive 2025/2 is not verified against the official text.

---

## Q4. Is parametric / index-based cover recognised as risk mitigation (Art. 209–215)?

### Takeaway
Only if its basis risk is **not material**. In the standard formula, material basis risk cannot be handled by haircutting the benefit (EIOPA Q&A 1597). A pure index cover therefore risks getting **zero** SCR credit for a standard-formula insurer. Under an internal model it can be recognised with basis risk modelled.

### Cited findings
- Art. 209(1): risk-mitigation techniques count only if they meet these criteria:
  - legally effective and enforceable;
  - monitorable;
  - the undertaking has a direct claim on the counterparty on default;
  - no double counting.
- Art. 209(2): cover in force for less than 12 months is recognised only pro rata, unless the Art. 209(3) rollover conditions are met. — [Art. 209](https://www.legislation.gov.uk/eur/2015/35/article/209/2020-01-31?view=plain)
- Art. 210(1): the cover and risk transfer must be "clearly defined and incontrovertible". **Art. 210(2): the arrangement "shall not result in material basis risk ... unless this is reflected in the calculation of the Solvency Capital requirement."** Art. 210(3): basis risk is material if it misstates the mitigating effect enough to "influence the decision-making or judgement of the intended user ... including the supervisory authorities." Art. 210(5) (added by 2019/981): combined arrangements are assessed together. — [Art. 210](https://www.legislation.gov.uk/eur/2015/35/article/210/2020-01-31?view=plain)
- Art. 211(2): reinsurance counterparties must be one of the following:
  - an SII-compliant (re)insurer;
  - an equivalent-regime reinsurer;
  - a non-equivalent reinsurer at credit quality step 3 or better.

  Art. 214 sets the collateral conditions. — [Art. 211](https://www.legislation.gov.uk/eur/2015/35/article/211/2020-01-31?view=plain); [Art. 214](https://www.legislation.gov.uk/eur/2015/35/article/214/2020-01-31?view=plain)
- EIOPA Q&A 1597 (submitted 10 Jul 2018, final) answers as follows:
  - "Basis risks cannot be reflected in the SF SCR by adjusting the risk mitigating effect of the risk-mitigation technique."
  - Index-based example: with 100 of risk hedged and 20 of residual basis risk, the 100 cannot be scaled down to 80.
  - Such techniques may qualify under a full or partial internal model.
  - Materiality is assessed on the covered proportion (citing Guideline 2, para 1.12, of EIOPA's basis-risk guidelines).
  — [EIOPA Q&A 1597](https://www.eiopa.europa.eu/qa-regulation/questions-and-answers-database/1597_en)
- The nat-cat scenarios are defined gross of "amounts recoverable from reinsurance contracts and special purpose vehicles". The SCR is the net loss in basic own funds, so recoveries are credited only through recognised reinsurance or SPVs. — [Art. 123(3)–(4)](https://www.legislation.gov.uk/eur/2015/35/article/123/2020-01-31?view=plain)

### Inferences
- For a **standard-formula** Finnish insurer, Tulva must be structured so its basis risk relative to the insurer's own Finnish flood loss is demonstrably immaterial. Options include:
  - a modelled-loss or portfolio-weighted index built on the insurer's own zone exposures;
  - zone-level triggers aligned to the 19 Annex IX zones;
  - an indemnity / ultimate-net-loss warranty (dual trigger).

  It should also be written as a reinsurance contract (or via an SPV/cat bond) with an eligible counterparty. Otherwise SF credit is likely nil.
- Even with full recognition, the **SF capital relief is small**. Finnish flood carries 0 SF capital today and 0.04 % × zone weights from 2027. The commercial case should lead with:
  - P&L and earnings-volatility protection;
  - ORSA / economic capital;
  - rating-agency capital;
  - fast liquidity after a spring flood.
- The 2027 introduction of a Finnish flood charge does create a new, measurable SF line that a well-designed cover could reduce. That gives a "regulatory change" hook for timing the launch.
- Internal-model users (If) can credit an index cover net of modelled basis risk. They are probably the most natural early buyers of a pure index product.

### Gaps
- The exact reference number and text of EIOPA's Guidelines on basis risk were not retrieved.
- I found no EIOPA or FIN-FSA statement specifically on parametric nat-cat reinsurance for P&C.
- The legal characterisation of a parametric contract (reinsurance versus derivative) under Finnish law was not researched.

---

## Q5. EIOPA protection-gap dashboard (Finland) and EU public-private reinsurance proposals

### Takeaway
Finland has one of the lowest nat-cat protection gaps in the EEA. Its total score is 4 across five perils in every year 2022–2025, and it is not on the flood watch-lists. The ECB/EIOPA EU-level public-private reinsurance proposal (Dec 2024) is a policy proposal, not law, as far as found.

### Cited findings
- Dashboard 2025 update (EIOPA-BoS-25/564, 10 Nov 2025): Finland's total current protection gap score across windstorm, wildfire, flood, coastal flood and earthquake is **4** in 2022, 2023, 2024 and 2025. For comparison, Estonia and Iceland are 4, Denmark 5, the EEA aggregate 5.5, Germany 8 and Greece 12. — [EIOPA dashboard "in a nutshell" (the file downloaded from this URL is the 2025 version)](https://www.eiopa.europa.eu/document/download/bbdc653b-e335-41f0-8293-0d8280a09855_en?filename=EIOPA-BoS-24-473_Dashboard+on+insurance+protection+gap+for+natural+catastrophes+in+a+nutshell+-+2024+version.pdf)
- For flood* (pluvial and fluvial, excluding coastal), only Romania and Croatia have a protection gap (score ≥ 3). The monitoring list (score 2.5) is AT, BG, CZ, DE, IT, NL, PL and SI. Finland is in neither group. — [same document](https://www.eiopa.europa.eu/document/download/bbdc653b-e335-41f0-8293-0d8280a09855_en?filename=EIOPA-BoS-24-473_Dashboard+on+insurance+protection+gap+for+natural+catastrophes+in+a+nutshell+-+2024+version.pdf); [Dashboard page](https://www.eiopa.europa.eu/tools-and-data/dashboard-insurance-protection-gap-natural-catastrophes_en)
- Across Europe only about a quarter of 1980–2024 nat-cat losses were insured. — [same document](https://www.eiopa.europa.eu/document/download/bbdc653b-e335-41f0-8293-0d8280a09855_en?filename=EIOPA-BoS-24-473_Dashboard+on+insurance+protection+gap+for+natural+catastrophes+in+a+nutshell+-+2024+version.pdf)
- An academic study lists Finland among countries with flood insurance penetration above 75 %. — [Bellia et al. 2025, Risk Management and Insurance Review](https://onlinelibrary.wiley.com/doi/full/10.1111/rmir.70001)
- EIOPA used the dashboard's protection-gap exposure data to build Finland's proxy exposure for the 0.04 % calibration. — [EIOPA Opinion BoS-24/462, para 4.67 fn 43](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)
- ECB–EIOPA joint paper (18 Dec 2024), building on their 2023 discussion paper, proposes:
  - (1) an EU-level public-private reinsurance scheme, funded by risk-based premiums from (re)insurers or national schemes, which complements national schemes and transfers risk to capital markets, possibly via a pan-European cat bond;
  - (2) an EU public disaster financing fund for public reconstruction, conditional on risk-mitigation measures.

  The paper cites about €900 bn of EU nat-cat losses over 1981–2023, with roughly a quarter insured. — [EIOPA publication](https://www.eiopa.europa.eu/publications/eiopa-and-ecb-joint-paper-towards-european-system-natural-catastrophe-risk-management_en); [Banque de France / ECB press release](https://www.banque-france.fr/en/press-release/ecb-and-eiopa-propose-european-approach-reduce-economic-impact-natural-catastrophes); [A&L Goodbody](https://www.algoodbody.com/insights-publications/closing-the-gap-eiopa-and-ecb-announce-proposals-to-close-insurance-protection-gap)

### Inferences
- Finland's low protection gap means the Tulva pitch should **not** be framed as closing a consumer protection gap. Finnish flood is already widely insured via home and property policies. The real problem is **insurer-side accumulation** of a correlated peril that is now entering Solvency II.
- An EU reinsurance scheme, if ever created, would target high-gap countries first. It is unlikely to crowd out a Finnish private index product in the near term.

### Gaps
- The per-peril Finnish flood score (0–4 scale) was not extracted from the interactive dashboard. It is only inferred as ≤ 2 from its absence on the watch-lists.
- I found no 2025–2026 legislative follow-up to the ECB–EIOPA scheme.

---

## Q6. FIN-FSA (Finanssivalvonta) stance on climate and flood risk

### Takeaway
FIN-FSA treats climate risk through ORSA and governance expectations aligned with EIOPA. Its published thematic work has focused on insurers' investment and transition risk, not underwriting flood. I found no flood-specific FIN-FSA guidance. FIN-FSA (as NCA) did push at EIOPA for flood to be added for Finland.

### Cited findings
- FIN-FSA's December 2019 letter to insurers set early climate-risk expectations. — [FIN-FSA letter 10 Dec 2019 (Finnish)](https://prod.finanssivalvonta.fi/globalassets/fi/tiedotteet-ja-julkaisut/valvottavatiedotteet/2019/kirje_vakuutusyhtioille_10122019.pdf)
- FIN-FSA's 2020 findings from non-life and life supervision said ORSA assumptions need special attention. At the initial stage, supervisory expectations concern mainly the identification and qualitative assessment of climate risks. — [FIN-FSA 2020 findings](https://finanssivalvonta.fi/en/publications-and-press-releases/supervision-releases/2020/fin-fsas-findings-from-supervision-of-non-life-and-life-insurance-companies-in-2020)
- The 2023 thematic reviews covered climate and environmental risk in banks and insurers. The insurance review covered investment assets and **transition risk only**, on the grounds that transition risk is simpler to assess and more significant in Finland. Physical risks are defined as "floods, storms" and similar. — [FIN-FSA Annual Report 2023](https://www.finanssivalvonta.fi/en/publications-and-press-releases/annual-reports/annual-report-2023/themes/fin-fsas-thematic-reviews-examined-the-current-state-of-climate-and-environmental-risk-management-in-the-banking-and-insurance-sectors/)
- FIN-FSA stresses that climate scenarios in ORSA are meant to inform long-term business-model and risk-bearing assessments, not just to meet minimum requirements. ORSAs have typically used 3–5 year horizons. — [KPMG Finland](https://kpmg.com/fi/en/insights/risk-and-regulation/climate-and-sustainability-risk-assessment-in-the-insurance-sector.html)
- In EIOPA's Call for Evidence, the Finnish NCA argued flood could be material for Finland. It also supplied the zoning choice (reuse of the windstorm postal-code mapping). — [EIOPA Opinion BoS-24/462, Nordic section and para 4.68](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)

### Inferences
- FIN-FSA's ORSA focus and its own push to bring Finnish flood into the SF suggest that supervisors will ask insurers how they assess Finnish flood accumulation after 2027. Tulva can position itself as a tool that helps meet that expectation.

### Gaps
- No FIN-FSA 2025–2026 supervisory priorities or flood-specific publications were found. Check finanssivalvonta.fi for the "valvonnan painopisteet" pages for 2025 and 2026 and for any national transposition guidance on Directive 2025/2 climate scenarios.
