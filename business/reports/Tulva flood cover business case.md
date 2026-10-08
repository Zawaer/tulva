# The business case for Tulva: a parametric spring-flood index cover for Finnish insurers

Prepared 8 October 2026 for Vaishnav (business plan and 3-minute pitch), Quantum x Finance 2026. The deck is due Saturday 10 October at 09:30.

**How to use this report.** It brings together six research notes (Finnish market, regulation, parametric market, customers and competitors, climate, quantum and jury) and checks them against the team's `CLAIMS.md`. Two kinds of number appear below:

- **Code outputs** come from the team's own scripts and are already logged in `CLAIMS.md` (for example "Ostrobothnia ≥2 trigger: 2.56 %, premium €346k").
- **External figures** come from public sources (for example "Finnish non-life premiums €5.6bn in 2024"). They are **not** code outputs. Under the team's rule, any external figure that goes in the deck must be logged in `CLAIMS.md` with the tag `source` and its citation, and the slide should show the source.

A few numbers are my own back-of-envelope arithmetic. They are marked "illustrative arithmetic" and should not go in the deck unless Toivo reproduces them in code. Section 10 lists them.

---

## 1. The short answer

Tulva has a real but narrow business case. It is strongest when pitched as **a tool for insurers to measure and transfer accumulated spring-flood risk** that is about to become visible under Solvency II. It is weakest when pitched as a big new insurance market.

What is strong:

1. **Finnish insurers really do carry this risk, and they carry it together.** Since 2014 the state no longer pays for flood damage. Home and property policies pay instead, and only for "exceptional" floods: in practice, ones rarer than 1-in-50 years. That is the same threshold Tulva's trigger uses ([vesi.fi](https://www.vesi.fi/vesitieto/tulvavahinkojen-korvaaminen/); [OP](https://www.op.fi/en/-/tulvat-ja-vakuutusten-korvattavuus)). Four groups write over 91 % of Finnish non-life premium ([Finance Finland 2024](https://www.finanssiala.fi/wp-content/uploads/2025/05/finnish-insurance-in-2024.pdf)). So the buyer list is short and well defined.
2. **Regulation creates a deadline.** Finnish flood has carried **no** standard-formula capital so far. From **30 January 2027** a Finnish flood module applies for the first time (Delegated Regulation (EU) 2026/269). That gives insurers a new reason to understand their joint flood exposure ([2026/269](https://lawplayer.com/eu/act/32026R0269)).
3. **The team's data result is genuinely interesting.** Within a cluster, gauges cross their 1-in-50 level together about 4–5 times more often than independence predicts. March snowpack shifts the odds a lot (code outputs, `CLAIMS.md`). Finnish authorities already publish March–April peak outlooks, but nobody turns them into a priced joint-loss distribution.
4. **There is white space.** No Finnish or Nordic regional parametric river-flood cover and no Nordic insurer-sponsored flood cat bond were found. The closest product, Swiss Re's FLOW, sells river-gauge covers to companies, not to insurers ([Swiss Re](https://corporatesolutions.swissre.com/insights/news/flow_new_parametric_water_level_insurance.html)).

What is weak, and will come up in Q&A:

1. **The market is small.** Historical spring-flood building losses are in the single-digit to low-double-digit € millions per event, and the 2005 Lapland flood was about €5–17M depending on definition. A €10M payout is as big as the largest historical event, so it may be larger than any single insurer's loss.
2. **The 35 % risk load is far below market pricing.** Comparable catastrophe layers trade at about **2.4–3.7× expected loss**, not 1.35×.
3. **Capital credit is not automatic.** Under the standard formula, a parametric cover with *material* basis risk gets **no** capital credit (EIOPA Q&A 1597). Even with full credit, the Finnish flood charge is small.
4. **The "EIOPA 0 %" claim, in its current form, is inaccurate.** EIOPA's 0 % is the correlation **between Finland and other countries**. *Within* Finland the new rules already assume strong correlation between zones.
5. **Climate is shifting the risk.** Spring floods are projected to shrink and move earlier, fastest in the south and west, including Ostrobothnia. Lapland stays roughly stable until about 2050.
6. **Quantum gives no speed or cost advantage today.** The defensible claim is a correct, honestly benchmarked, hardware-tested QAE engine that is ready for future machines.

**Recommended positioning in one sentence:** *"Tulva is a joint spring-flood risk engine and parametric index for Finnish insurers. It shows the flood accumulation that the 2027 Solvency II flood module captures only coarsely, prices it from this winter's snowpack, and runs on a quantum-ready estimator we have benchmarked honestly against classical methods."*

---

## 2. The Finnish flood insurance market and loss history

### How flood cover works since 2014

- **The state stepped back.** The state flood-compensation act (284/1983) lapsed on 1 January 2014. Since then, flood damage to buildings and contents is covered only by voluntary private home and property insurance. Almost all insurers bundled flood cover into those policies ([HE 143/2013](https://www.edilex.fi/he/20130143); [Taloustaito](https://www.taloustaito.fi/koti/rankkasateet-voivat-voimistua--korvaako-vakuutus/)).
- **Only "exceptional" floods are covered.** For river floods, the policy pays only if the flood is exceptional, generally one with a return period of 1-in-50 years or rarer. SYKE's Flood Centre (Tulvakeskus) certifies this case by case, which can take weeks. Nothing is paid until it does ([vesi.fi](https://www.vesi.fi/vesitieto/tulvavahinkojen-korvaaminen/)).
- **Why this matters for Tulva:**
  - The policy threshold and Tulva's trigger are the same 1-in-50 level. When several gauges in a region cross 1-in-50, many policies start paying at the same time. That is exactly the accumulation Tulva measures.
  - Floods between 1-in-10 and 1-in-49 are not insured, so insurer losses are concentrated in the rare tail years.

### Who the insurers are

Finnish non-life insurance was a **€5.55bn** premium market in 2024. "Fire and other damage to property", the class that holds home and property flood cover, was **€1.28bn** ([Finance Finland, *Finnish insurance in 2024*](https://www.finanssiala.fi/wp-content/uploads/2025/05/finnish-insurance-in-2024.pdf)).

| Insurer (2024) | Share of domestic non-life | Fire & property premium | Combined ratio |
|---|---|---|---|
| Pohjola Insurance (OP) | 32.6 % | €383M | 98.3 % |
| LocalTapiola group | 28.3 % | €398M | 99.0 % |
| If P&C (Sampo) | 21.9 % | €338M | 87.1 % |
| Fennia | 8.4 % | €84M | 111.3 % |
| Turva | 2.9 % | €35M | 105.9 % |
| Pohjantähti | 2.4 % | €30M | 108.4 % |

Source: Finance Finland 2024 (above). A combined ratio above 100 % means the insurer lost money on underwriting.

What this means for Tulva:

- **The top four groups are the market.** OP alone is about a third of it, and one of the jurors is from OP.
- **The smaller and regional players may be the earliest buyers.** LocalTapiola is a federation of regional mutuals (for example LähiTapiola Lappi and Pohjanmaa) with concentrated regional exposure. Fennia, Turva and Pohjantähti all lost money on underwriting in 2024. A regional cover suits them, but this is an inference, not something they have said.

### Reinsurance

No public detail was found on Finnish insurers' catastrophe reinsurance (retentions, limits, or whether flood is included). If P&C sits inside Sampo's Nordic group, and Sampo uses an approved partial internal model ([Sampo](https://www.sampo.com/media/releases-and-news/2024/sampo-has-received-approval-for-its-group-partial-internal-model/)). The practical next step is to read each insurer's Solvency and Financial Condition Report (SFCR), the sections on reinsurance and risk mitigation.

### Loss history: small in euros, concentrated in a few years

| Event | What happened | Loss |
|---|---|---|
| Spring 1966, south | Snowpack about double normal; return periods above 100 years in several basins | "Order of €10M" ([Helminen, FMI](https://sciencepolicy.colorado.edu/research_areas/sparc/research/projects/extreme_events/munich_workshop/helminen.pdf)) |
| Spring 2005, Lapland (Ivalo, Kittilä) | Snowpack about double normal; Ounasjoki and Ivalojoki at about 1-in-50 at the same time | About €5M house damage (Helminen); Yle reported about €17M, likely a broader definition |
| Aug 2007, Pori | Cloudburst (urban, not river) | Over €20M total, about €10M insured ([vesi.fi](https://www.vesi.fi/vesitieto/tulvavahinkojen-korvaaminen/)) |
| 2012–2013, Ostrobothnia | River floods | About €20M total; the state paid over €4M (vesi.fi) |
| 2010–2015, all events | Insured flood claims | Just over €5M **in total** (vesi.fi) |
| Spring 2018 and 2020, Lapland | Record snow; Kemijoki above the damage limit at Rovaniemi in 2020 | No € loss figure found |
| Spring 2024 | Worst situation in **Ostrobothnia**; Ivalojoki "clearly smaller than 2005", below the damage limit | No € loss figure found ([STT/SYKE](https://www.sttinfo.fi/tiedote/70135434/lansirannikolla-tulvii-myos-lappiin-ennakoidaan-kevaan-edetessa-vaikeaa-tulvakauttapublisherId=69819243&lang=fi); [Lapland ELY](https://www.sttinfo.fi/tiedote/70212999/lapin-jokien-tulvahuiput-odotettavissa-viikonvaihteessa-tai-ensi-viikon-aikana?publisherId=69817880&lang=fi)) |
| Springs 2025 and 2026 | Low snow, small peaks; 2026 Rovaniemi peak "possibly the smallest on record" | None ([Lapland flood meeting 16.4.2026](https://elinvoimakeskus.fi/documents/d/elinvoimakeskus/kokouskooste_tulvakokous_lappi_1_16042026-pdf)) |

**Modelled worst cases are much larger than observed losses.** A national 1-in-250 flood was estimated at about **€550M** in damage, but that figure comes from a 2000 study, so treat it as dated ([Raportteja 102/2013](https://www.doria.fi/bitstream/10024/93358/2/Raportteja_102_2013.pdf)). Potential damage in the Saimaa lake system is about **€430M** ([ELY/SYKE 24/2023](https://vesi.fi/aineistopankki/wp-content/uploads/2024/05/Raportteja_24_2023.pdf)). Pori (Kokemäenjoki) and Rovaniemi (Kemijoki) are the largest river-flood risk concentrations ([Valtioneuvosto, 19 Dec 2024](https://valtioneuvosto.fi/-/1410837/suomen-merkittavat-tulvariskialueet-on-nimetty)).

**No industry-wide record exists.** Finance Finland has not tracked flood compensation since 2015 ([Taloustaito](https://www.taloustaito.fi/koti/rankkasateet-voivat-voimistua--korvaako-vakuutus/)). That gap is a pain point Tulva can name: insurers have no shared, transparent view of joint flood loss.

### The flood-risk areas

On 19 December 2024 the Ministry of Agriculture and Forestry designated **18 significant flood-risk areas for 2025–2030: 14 river areas and 4 coastal**. Four earlier areas were dropped: Loviisa coast, Riihimäki, Lapua and Kemijärvi ([Valtioneuvosto](https://valtioneuvosto.fi/-/1410837/suomen-merkittavat-tulvariskialueet-on-nimetty)).

The research did not retrieve the full official list of the 14 river areas. The team's 14 (Ostrobothnia 6, North 5, Satakunta–SE 3) should be checked against the ministry's decision annex. In particular, check:

- Tornio, which may be counted as coastal;
- Huittinen, named in the 2011 round;
- Kymijoki.

### Is there a protection gap?

Not much. EIOPA scores Finland's nat-cat protection gap at **4**, one of the lowest in Europe (the EEA average is 5.5 and Germany's is 8). Finland is not on EIOPA's flood watch-list ([EIOPA dashboard 2025](https://www.eiopa.europa.eu/document/download/bbdc653b-e335-41f0-8293-0d8280a09855_en?filename=EIOPA-BoS-24-473_Dashboard+on+insurance+protection+gap+for+natural+catastrophes+in+a+nutshell+-+2024+version.pdf)). An academic study puts Finnish flood insurance penetration above 75 % ([Bellia et al. 2025](https://onlinelibrary.wiley.com/doi/full/10.1111/rmir.70001)). One secondary source claims less than half of Finns have flood cover, which conflicts with this. Do not build the pitch on it.

**So do not pitch Tulva as "closing Finland's flood protection gap".** The problem is on the insurer's side: **accumulation of one correlated peril** in a few balance sheets.

---

## 3. Regulation: Solvency II, EIOPA, ORSA and capital credit

### What the rules say today and from 2027

**Until 29 January 2027,** the Solvency II standard formula has **no flood parameter for Finland** (Delegated Regulation 2015/35, Annex VII). Finland is also exempt from the premium-based flood charge, because it is listed in Annex XIII. **Finnish flood risk therefore attracts zero standard-formula capital today** ([Art. 123 and Annex XIII](https://www.legislation.gov.uk/eur/2015/35/annex/XIII/2020-01-31?view=plain)).

**From 30 January 2027,** Delegated Regulation **(EU) 2026/269** adds Finland to the flood module ([2026/269](https://lawplayer.com/eu/act/32026R0269)):

- **Country factor:** 0.04 %. Sweden is 0.045 %, Norway 0.05 % and Denmark 0.04 %.
- **Zones:** 19 Finnish zones, each with its own risk weight. The weights run from 0.3 to 8.9, so where in Finland the exposure sits matters far more than the national factor.
- **Correlation between countries:** **0.00** between Finland and every other country, including Sweden, Norway and Denmark.
- **Correlation within Finland:** a 19 × 19 zone matrix that is **not** zero. In the research parse, the values run from 0 to 1.00 with a mean of about 0.27. About a third of zone pairs are at 0.50 or above, and there are clusters of zones correlated at 0.75–1.00.

**Where the 0 % comes from.** EIOPA's Opinion (EIOPA-BoS-24/462, 30 January 2025, para 4.70) proposed 0 % between Finland and all other countries. It said a 25 % correlation for shared rivers with Sweden and for "snowmelt induced fluvial flood" was discussed and rejected. The reasons given were that the shared rivers run through very sparsely populated areas, that the snowmelt flood "is not considered significant", and that one model vendor's results supported this ([EIOPA Opinion](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf)). Finland's 0.04 % factor was set at the low end of a vendor range of 0.039–0.064 %. EIOPA's reason was Finnish flood controls such as lake regulation.

**What this means for the pitch:**

- **The accurate story is better than the inaccurate one.** EIOPA *did* look at snowmelt flood correlation, called it insignificant, and relied on a single vendor model. That makes Tulva's snowmelt-based joint-risk evidence a direct, relevant input to the next recalibration, roughly 2027–2029. EIOPA reviews nat-cat parameters every 3–5 years ([Milliman](https://www.milliman.com/en/insight/2023-2024-reassessment-natural-catastrophe-risk-standard-formula)).
- **The cross-border 0 % matters most to Nordic groups.** For If/Sampo, writing business in Finland, Sweden and Norway, Finnish flood is treated as fully independent of Swedish and Norwegian flood. If one snowpack drives both, group flood capital is understated.
- **Do not say "regulators assume Finnish areas are independent".** Within Finland they do not. The fair criticism is that Finland's internal correlation comes from **one vendor model on coarse postal-code zones**, and is **not conditioned on the season's snowpack**.

### ORSA: the strongest regulatory hook

Every insurer must run an Own Risk and Solvency Assessment (ORSA). It must cover all material risks, including where the insurer's real risk profile differs from the standard-formula assumptions, and it must include climate scenarios ([EIOPA climate ORSA opinion, 2021](https://www.eiopa.europa.eu/eiopa-issues-opinion-supervision-use-climate-change-risk-scenarios-orsa-2021-04-19_en)). The Solvency II review directive (EU) 2025/2 applies from 30 January 2027 ([FIN-FSA](https://www.finanssivalvonta.fi/en/regulation/regulatory-framework/solvency-ii/)).

FIN-FSA itself argued at EIOPA that flood may be material for Finland. Its published climate work so far has covered investments, not underwriting flood ([FIN-FSA Annual Report 2023](https://www.finanssivalvonta.fi/en/publications-and-press-releases/annual-reports/annual-report-2023/themes/fin-fsas-thematic-reviews-examined-the-current-state-of-climate-and-environmental-risk-management-in-the-banking-and-insurance-sectors/)).

**Inference:** after 2027, supervisors are likely to ask insurers how they assess Finnish flood accumulation. A snowpack-conditioned joint-risk view is a natural ORSA input, **even where the cover buys little capital relief**.

### Capital credit for an index cover: possible, but not automatic

- **The basis-risk rule.** Article 210(2) of 2015/35 says a risk-mitigation arrangement must not leave **material basis risk**, unless that basis risk is reflected in the capital calculation ([Art. 210](https://www.legislation.gov.uk/eur/2015/35/article/210/2020-01-31?view=plain)). Basis risk is the gap between what the index pays and what the insurer actually loses.
- **No haircut in the standard formula.** EIOPA Q&A 1597 says basis risk **cannot** be handled in the standard formula by scaling down the cover's effect. For example, you cannot count a €100 cover as €80 because €20 is basis risk. Such covers can be recognised under an internal model ([EIOPA Q&A 1597](https://www.eiopa.europa.eu/qa-regulation/questions-and-answers-database/1597_en)).
- **Consequence:** for a **standard-formula** insurer, a pure gauge index is likely to get **zero** capital credit unless its basis risk is shown to be immaterial. For an **internal-model** insurer such as If/Sampo, it can be credited net of modelled basis risk. That makes internal-model users the most natural first buyers of a pure index.
- **Other conditions:**
  - It must be written as reinsurance with an eligible counterparty, or through a special purpose vehicle (Art. 211).
  - A cover in force for less than 12 months is recognised only pro rata (Art. 209(2)), so write it as an **annual contract**, not a March-to-June contract.
- **Accounting.** Under IFRS 17, a pure index contract with no link to the holder's own loss may be classed as a **derivative** rather than insurance ([BDO](https://bdo.nz/en-nz/blogs/financial-reporting-insights/for-the-purposes-of-ifrs-17,-what-is-an-insurance-contract)). A **dual trigger** fixes this: pay only if the index triggers *and* the insurer's own flood loss exceeds a small amount.
- **Even full credit is small.** Finnish flood capital is zero today and modest from 2027. The cover's value is mostly **earnings protection, ORSA and economic capital, rating-agency capital, and fast cash after a flood**. It is not mostly Solvency II relief.

---

## 4. The parametric market, pricing practice and basis risk

### Market size

- **Parametric insurance: estimates disagree by about six times.** They range from **about $3.5bn** for 2025 on a narrow definition ([Mordor](https://www.mordorintelligence.ar/industry-reports/parametric-insurance-market)) to **about $18–21bn** on broad ones ([GMI](https://www.gminsights.com/industry-analysis/parametric-insurance-market); [Carrier Management](https://www.carriermanagement.com/features/2026/09/17/292049.htm)). Growth estimates cluster at **12–14 % a year**. Quote a range, never a single number.
- **Cat bonds and insurance-linked securities (ILS) are measured more reliably.** About **$61bn** of cat bonds were outstanding at end-2025 ([Artemis](https://www.artemis.bm/news/catastrophe-bond-market-records-that-were-broken-in-2025/)). Alternative reinsurance capital was **$136bn** ([Aon via Artemis](https://www.artemis.bm/news/alternative-ils-reinsurance-capital-grew-18-to-136bn-in-2025-aon/)).
- **Capital is plentiful and prices are falling.** Property-cat reinsurance rates fell 14.7 % at 1 January 2026 ([Howden Re via Artemis](https://www.artemis.bm/news/ilw-rates-fall-10-20-at-jan-renewals-growth-to-normalise-in-2026-howden-re/)). That helps a new product find capacity.
- **Most flood loss is uninsured.** About 80 % of flood losses worldwide are uninsured ([Swiss Re](https://corporatesolutions.swissre.com/alternative-risk-transfer/parametric-solutions/flood.html)). This is a global point. Finland's own gap is small (Section 2).

### Real examples

| Type | Example | Relevance to Tulva |
|---|---|---|
| River-gauge index, for companies | **Swiss Re FLOW**: pays per day a river gauge is above or below a level; covers gauges in **the Nordic countries** and elsewhere in Europe; terms up to 3 years | Closest product. Tulva differs by targeting **insurers**, being **multi-gauge and regional**, and being **conditioned on snowmelt** |
| Property-level sensor | FloodFlash (UK), which paid a Storm Bert claim in about 10 hours; Descartes Flood-at-Location (US, up to $70m) | Shows how fast parametric cover pays out, and that basis risk is real: some FloodFlash clients got nothing ([Artemis](https://www.artemis.bm/news/floodflash-uk-floods-hit-parametric-triggers-for-some-policies/)) |
| Sovereign | CCRIF excess-rainfall cover: US$21.1M to Jamaica after Hurricane Melissa (2025) | Public-sector precedent |
| Public-sector Europe | Italian bishops' conference church flood cover (Generali, Swiss Re, Floodbase data): €180m over 3 years | Largest parametric cover in Europe ([Swiss Re](https://www.swissre.com/our-business/public-sector-solutions/case-studies/protecting-religious-cultural-heritage.html)) |
| Flood cat bond | **Flood Re Vision 2039** (UK, 2025): £140m; 2.8 % chance of being hit; expected loss 1.7 %; priced at 5.0–5.75 % | **Best pricing benchmark**: hit probability close to Tulva's ~2–2.6 % trigger ([Artemis](https://www.artemis.bm/news/flood-re-secures-40-upsized-140m-vision-2039-cat-bond-at-top-end-pricing/)) |

No Finnish or Nordic parametric river-flood cover and no Nordic insurer flood cat bond were found. Before claiming "the first" in the deck, check the Artemis deal directory by sponsor name.

### Pricing practice: the 35 % load is too low

The market prices cat layers as a **multiple of expected loss**. Expected loss is the average yearly payout: probability times limit.

- **Cat bonds overall:** the weighted average multiple was 3.71× in 2024, 3.0× in 2025, and about 2.4–2.5× in 2026 so far, in a very soft market ([AM Best via Artemis, 25 Sep 2026](https://www.artemis.bm/news/as-cat-bond-loss-multiples-tighten-am-best-urges-investors-towards-greater-selectivity/)).
- **Flood cat bonds:** about **2.9–3.4×** for Vision 2039 and about **3.0–3.2×** for FloodSmart Re 2023-1 ([Artemis](https://www.artemis.bm/deal-directory/floodsmart-re-ltd-series-2023-1/)).
- **Remote layers cost more.** Layers that are rarely hit carry *higher* multiples ([Variance](https://variancejournal.org/article/120790-an-analysis-of-the-market-price-of-cat-bonds)).

Tulva currently prices at **expected payout × 1.35** (`CLAIMS.md` lists this under "Simplified or assumed"). For the Ostrobothnia "≥2" trigger the code gives a probability of 2.56 % and a premium of €346k.

*Illustrative arithmetic, not code output:*

| | Multiple of expected loss | Premium | Price as % of the €10M limit |
|---|---|---|---|
| Tulva today | 1.35× | €346k | 3.5 % |
| Market range | 2.5–4× | about €640k–€1.0M | 6.4–10 % |
| Vision 2039, for comparison | about 3.4× | n/a | 5.0–5.75 % |

A capital-cost check points the same way:

- A €10M binary cover that is fully backed by collateral ties up about €10M.
- At a 6–8 % required return, that capital costs about €0.6–0.8M a year, on top of an expected loss of about €0.2–0.26M.
- At 1.35×, the premium does not cover the cost of capital.

Model uncertainty adds to this. A 1-in-50 joint event estimated from 65 years of data is an extrapolation. The team's own t-copula check says the price could be 5–60 % higher for "≥2" (`CLAIMS.md`). All of this argues for a load at or above the market average, not below it.

**What to do:**

- Call the 35 % figure a **"technical price"**: expected loss plus a risk margin, before capital cost, expenses and reinsurer margin.
- Show a **market price** next to it at about 2.5–3.5× expected loss. Ask Toivo to add a load sensitivity to `price_index.py` so the market-price numbers become code outputs.
- The *relative* result (Tulva's price versus the independence price) does not depend on the load. That is the message to lead with.

### Basis risk: the main buyer objection

Basis risk is the gap between what the index pays and what the insurer actually loses ([Descartes](https://descartesunderwriting.com/insights/what-basis-risk-parametric-insurance-practical-explanation); [PwC Switzerland 2024](https://www.pwc.ch/en/publications/2024/Basis_risk_in_parametric_insurance_challenges_and_mitigation_strategies.pdf)). A PwC juror is on the panel, and PwC has published on exactly this topic.

Tulva's "≥2 gauges" rule has a trade-off:

- **It cuts false payouts.** A single faulty gauge or a local ice jam will not trigger it.
- **It adds misses.** A loss concentrated near one gauge will not trigger it either.

There is also a size problem. A €10M payout against historical event losses of about €5–20M **in total across all insurers** may exceed one insurer's loss. Over-compensation is itself basis risk, and it can cause trouble under IFRS 17 and for supervisors.

Ways to reduce basis risk:

1. **Stepped payout.** For example, 50 % when 2 gauges trigger and 100 % when 3 or more do, or scale the payout by how far the level is exceeded.
2. **Weight the index by the insurer's own exposure** in the 19 Solvency II zones.
3. **Dual trigger:** pay only if the index triggers and the insurer's own loss is at least €X.
4. **Size the limit to the insurer's modelled 1-in-50 flood loss**, not a fixed €10M.
5. **Back-test against real claims.** Measure false and missed payouts against Finance Finland or insurer claims data.

### Adverse selection: the snowpack cuts both ways

Finnish spring floods are predictable from about February–March. If insurers can buy *after* seeing the snowpack, they will buy only in big-snow years. This is well documented in crop insurance ([RePEc](https://ideas.repec.org/a/oup/revage/v16y1994i3p441-451..html)). The insurer buyers will run their own snow models, so this risk is real.

The team's own numbers show how large the effect is. After a high-snow March outlook, the Ostrobothnia "≥2" price rises to **€1.74M, five times the climatological price** (code output).

Standard fixes:

1. **Sell before the snow is known.** Set a purchase deadline of around 1 November–1 December, with an annual term.
2. **Write multi-year contracts** (2–3 years, as FLOW does).
3. **Make the price depend on the snowpack** for late buyers.
4. **Pay part of the cover early.** In the forecast-based-financing style used by the Red Cross ([PrepareCenter](https://preparecenter.org/wp-content/sites/default/files/forecast_based_financing.pdf)), an "anticipatory tranche" pays out on a strong March outlook so insurers can fund defences and claims staff before the flood.

**Pitch framing:** the March conditioning is (a) an **early-warning and capital signal** for insurers, and (b) how Tulva **prices fairly and protects itself** against late buyers. It is not a way to sell cover in March at the climatological price.

---

## 5. Customers, business model, go-to-market and competitors

### Who would buy

1. **Primary insurers: the main customers.** OP/Pohjola, LocalTapiola and its regional mutuals, If, Fennia, Turva and Pohjantähti. Their pain points:
   - Post-2014 flood exposure that is concentrated in tail years.
   - A new Solvency II flood line from 2027.
   - ORSA climate requirements.
   - No industry flood-loss statistics since 2015.
   - Vendor models that treat Finland inside pan-European rainfall-driven frameworks.
2. **Reinsurers: capacity partners first, customers second.** Swiss Re, Munich Re, Hannover Re and others would carry the risk behind a Tulva cover. Some already own flood models, such as Swiss Re's Fathom ([Reinsurance News](https://www.reinsurancene.ws/swiss-re-acquires-flood-risk-modeller-fathom/)).
3. **Secondary buyers, weaker cases.**
   - Municipalities such as Kittilä, Pori and Inari bear uninsured emergency costs, but have small budgets.
   - Hydropower companies (Kemijoki Oy, Fortum) want inflow forecasts more than loss cover.
   - Banks with mortgage books want climate stress-test data.

   These buyers are inferred; none were confirmed by a source.

### Business model options

| Model | How it earns | Size, illustrative | Fit for a new team |
|---|---|---|---|
| **A. License the analytics** (joint-risk engine and index) | Annual licence per insurer or reinsurer | About €30–100k a year per client (inferred from dated cat-model licence prices, [Risk.net](https://risk.net/node/1503527)); 5 Finnish insurers plus a few reinsurers gives low single-digit €M a year at most | **Best first step** |
| **B. Design the index and take a fee** | Structuring or data fee; a reinsurer or established parametric insurer carries the risk | Fee per deal | **Good second step** |
| **C. Become an underwriting agency (MGA)** | 10–25 % commission on premium | On a €0.4–0.8M premium, about €40–200k per contract (illustrative) | Slow. Needs FIN-FSA authorisation and capacity |
| **D. Public-sector research projects** | Grants | Business Finland R2B: 80 % grant, typical projects €400–800k ([Business Finland](https://www.businessfinland.fi/en/services/funding/calls/2026/r2b-funding-call-2-2026/)) | Good for non-dilutive funding with a university, SYKE or FMI |

Precedents:

- **Descartes** began in 2018 as an underwriting agency, became a full insurer in 2022, and targets $500m of premium ([The Insurer](https://theinsurer.com/ti/interview/descartes-targets-500-million-premium-with-30-annual-growth-as-ai-and-rapid-2025-10-13)).
- **FloodFlash** was bought by NormanMax in 2025 ([Reinsurance News](https://www.reinsurancene.ws/normanmax-to-acquire-floodflash/)).
- **Retail parametric agencies have closed.** Selling to insurers and reinsurers is safer than selling to households.

**Recommended sequence for the business plan:**

1. A paid pilot with one insurer (OP or LocalTapiola) or one reinsurer's Nordic team, in **autumn, ahead of the 1 January reinsurance renewals**.
2. License the engine and index.
3. Put the cover on a reinsurer's balance sheet and take a structuring or data fee.
4. Expand to Sweden and Norway, which have snowmelt rivers and, from 2027, new flood factors of their own. This step is needed for scale.

### Competitors

- **Verisk (AIR) Inland Flood Model for Central Europe** explicitly covers Finland, Sweden and Norway. It is precipitation-driven, and its documentation does not mention snowmelt ([Verisk docs](https://docs.risksolutions.verisk.com/Touchstone/11.0/ts-tsre_all/help_ts_loss-analysis_flood-zones.html)).
- **Moody's RMS Europe Inland Flood HD** says it models snowmelt. Whether it covers Finland is not confirmed.
- **Others:** JBA (global maps), Fathom (Swiss Re), Floodbase (index data), SCALGO (Nordic flood mapping for planners, not insurance), Swiss Re FLOW, Descartes.
- **SYKE and FMI** are data sources and partners, not competitors.

**Differentiation must be specific.** It is *not* "nobody covers Finland". It is: **(1) conditioned on this winter's snowpack, (2) joint risk calibrated to Finnish gauges, (3) a ready-to-trade parametric index, and (4) a transparent, auditable method.** Back it with back-tests on 1966, 1984, 2000, 2005 and 2018, the years the team's code flags.

### Market sizing, honestly

- **Analytics TAM:** global catastrophe-modelling software is about $2–3bn (low-transparency market-research publishers, [TrendX](https://trendxinsights.com/syndicated-market-research-reports/catastrophe-modeling-market/)).
- **Finnish SAM:** a handful of insurers. The fire and property premium pool is €1.28bn (Finance Finland).
- **SOM in year 3, illustrative:** 3–6 licences at €30–100k, so about €0.1–0.6M a year, plus structuring fees.
- **Be upfront that Finland is the beachhead and the Nordics are the business.**

---

## 6. Climate outlook for Finnish spring floods

**In one line: the risk is shifting, not simply shrinking.** It is moving from spring to winter, and spring-flood risk is falling fastest in the south and west.

- **Long-run projections.** SYKE's work since 2010 projects that spring 100-year floods fall by **15–40 %** by 2070–2099, while floods in other seasons rise by 12–40 %. The largest decreases are around **65–66°N** ([Veijalainen et al. 2010](https://en.vedur.is/media/ces/Journal_of_Hydrology_Veijalainen_etal.pdf)).
- **The 2026 update** (SYKE report 30/2026, using the latest generation of climate models) agrees ([SYKE 30/2026](https://www.kemijoki.fi/wp-content/uploads/2026/08/sykera2026-30veijalainenkemijoki.pdf)):
  - Snowmelt floods decrease, "particularly from the mid-century onward".
  - For Kemijoki (Rovaniemi and Kittilä), floods "may still remain at current magnitude and large spring floods are still common" in 2020–2049.
  - The flood peak moves earlier, from late May or June to May or even April.
  - Autumn and early-winter floods increase in every scenario.
- **Observed trend.** Since 1911, high flows have come earlier and got smaller, "notably in the coastal region and less so in the north" ([Lintunen et al. 2024](https://research.utu.fi/converis/portal/detail/Publication/387506879?lang=en_US)).
- **Pori and Kymijoki are different.** Their floods grow, driven by winter rain, lake volume, and frazil ice. Frazil is slushy ice that forms in turbulent water and can jam rivers. A March snowpack variable explains little of this risk.

**What this means for each Tulva cluster** (inference):

- **North (Lapland):** the most durable market. Risk is stable to about 2050, and snowpack conditioning adds the most value here.
- **Ostrobothnia:** this cluster has the highest code-output price and the best snow skill, but it sits in the band where spring-flood risk is falling fastest.
  - The team's own back-test shows this (code output): Ostrobothnia's 1-in-10 paying years are 1965, 1966, 1971, 1972, 1974, 1977, 1984 and 2000, so **none since 2000**.
  - Pricing on 1961–2025 as if the climate were unchanged may *overstate* today's Ostrobothnia risk.
  - Expect a juror to ask. Answer with "we re-estimate each year on a recent-window baseline" and, if time allows, a code run on post-1990 data only.
- **Satakunta–SE:** needs a winter, frazil and ice peril to be useful. `CLAIMS.md` already notes that Pori's winter floods are missed.

**Forecast skill.** SYKE's national forecasting model (WSFS) covers all of Finland and uses satellite snow data. Short-range forecasts are reliable for 3–5 days ([WMO](https://public.wmo.int/sites/default/files/2023-12/Operational_flood_forecasting_and_warnings_141223.pdf)). Authorities publish probabilistic peak outlooks from mid-March to April. No published skill scores were found. Tulva's edge is **turning outlooks into a priced joint-loss distribution**, not the forecast itself.

**Climate as a selling point:** the shift is an argument *for* Tulva. Static return periods go out of date, and insurers need a model that is re-estimated every year and conditioned on the season. It is also the ESG angle that the hackathon challenge text asks for.

---

## 7. Quantum computing in finance and insurance, and what the jury cares about

### What quantum amplitude estimation (QAE) can honestly claim

- **The theory.** QAE needs about **1/N** queries to reach an error that classical Monte Carlo reaches with **1/√N**. That is a quadratic saving in the number of queries ([Montanaro 2015](https://arxiv.org/abs/1504.06987); [Woerner & Egger 2019](https://arxiv.org/abs/1806.06893)).
- **Tulva's method.** Tulva uses maximum-likelihood amplitude estimation, a variant without the extra phase-estimation circuitry. That keeps circuits shallow, which is best practice for today's noisy hardware ([Suzuki et al. 2020](https://arxiv.org/abs/1904.10246); [Giurgica-Tiron et al. 2022](https://quantum-journal.org/papers/q-2022-06-27-745/)).
- **The binary trigger is a good fit.** The payout is "yes or no", so the circuit needs only a simple comparator, not an approximation of a payoff curve.
- **When would there be a practical advantage?** The best estimate, for a realistic derivative, is about **8,000 error-corrected qubits** running at MHz speeds ([Chakrabarti et al., Quantum 2021](https://arxiv.org/abs/2012.03819v2)). Vendor *targets* are IBM Starling at about 200 logical qubits in 2029 ([IBM roadmap](https://thequantuminsider.com/2025/06/10/ibm-offers-roadmap-toward-large-scale-fault-tolerant-quantum-computer/)) and IQM fault tolerance by 2030 ([IQM Halocene](https://thequantuminsider.com/2025/11/13/iqm-launches-a-new-quantum-computer-product-line-for-error-correction/)). **Advantage is a 2030s question.**
- **Two known caveats:**
  - Quadratic speed-ups may not pay off on early error-corrected machines ([Babbush et al. 2021](https://arxiv.org/abs/2011.04149)).
  - Loading the probability distribution into the circuit can cancel out the speed-up ([Herbert 2021](https://arxiv.org/abs/2101.02240)).
- **Closest prior work.** A March 2026 paper applies QAE to catastrophe-insurance tail pricing, on a simulator only. It finds that **strong classical baselines win today** and that discretisation is the bottleneck ([Kirke, arXiv:2603.15664](https://arxiv.org/abs/2603.15664)). No QAE paper on parametric or flood insurance was found, so Tulva's framing appears new.

**The team's result** (code output): for P(Kittilä and Ivalo both over 1-in-50) = 0.125 %, the ideal-simulator QAE gave **±0.011 pp** against **±0.027 pp** for Monte Carlo with the same 16,000 queries. That is the safe headline. Hardware results from IQM Q20 and IBM must go into `CLAIMS.md` (tags `qae-q20` and `qae-ibm`) before they appear on a slide.

**Claims ladder: use these.**

1. "We built a working QAE estimator for a real parametric-flood trigger probability, validated against the exact value and Monte Carlo."
2. "In the ideal model, error falls as 1/N against 1/√N. Here is our measured curve, and here is how noise bends it on IQM and IBM hardware."
3. "Quantum-ready: the same model plugs into fault-tolerant machines when they arrive. Vendors target about 2029–2030."

**Never say:** "faster", "cheaper", "quantum advantage", or "exponential".

### What each juror's organisation is likely to care about

This mapping is inferred from each organisation's public messaging. The jurors' own views were not found.

| Juror (org) | What they likely want to hear | Tulva's answer |
|---|---|---|
| Toikka (**OP**) | Real customer value for Pohjola Insurance. OP's own language is "quantum-ready" and "path towards quantum advantage in real-world financial use cases" (OP–Qutwo unit, July 2026, [Global Finance](https://gfmag.com/technology/op-and-qutwo-debut-quantum-computing-partnership/)) | OP is the largest Finnish non-life writer, and Tulva measures OP's own flood accumulation. Use the phrase "quantum-ready" |
| Anbarjafari (**PwC**) | Business plan, regulation, basis risk, model governance and explainability (affiliation and focus unverified) | The accurate EIOPA story, Q&A 1597, dual trigger, back-tests, and every number traceable in `CLAIMS.md` |
| Steinmann (**IQM**) | Real runs on IQM hardware, honest noise analysis, the scaling path | Q20 runs with measured error; the shallow-circuit design; Qrisp has an official IQM backend ([IQM docs](https://docs.iqm.tech/iqm-client/user_guide_qrisp/index.html)); the Halocene path to fault tolerance |
| Seesto (**IBM**) | An honest classical baseline, in the spirit of IBM's public advantage tracker | Exact and Monte Carlo reference values, the IBM backend comparison, no advantage claim |
| Mehtola (**VTT**) | Finnish ecosystem capability; quantum combined with supercomputers; climate relevance | Aalto Q20 via LUMI; Finland's Quantum Technology Strategy 2025–2035 ([Valtioneuvosto](https://valtioneuvosto.fi/en/-/1410877/strategy-quantum-technology-is-finland-s-new-driver-of-growth-and-builder-of-a-sustainable-future)); SYKE and FMI data |

The judging criteria are Impact, Business plan, Team progress, Innovativeness and Methodological capability. In 2023 the Hanken hackathon was won by a **business- and ESG-led** concept in which quantum was only a long-term vision ([Hanken](https://hanken.fi/en/news/hanken-quantum-hackathon-winners-want-help-businesses-grappling-esg-reporting)). The business plan carries real weight.

---

## 8. Recommendations for the business plan and pitch

### Positioning

1. **Lead with the insurer's problem, not with quantum.** Suggested opening: "When several Finnish rivers pass their 1-in-50 level in the same spring, every home policy pays at once. Insurers have no shared, snowpack-aware view of that accumulation, and from January 2027 Solvency II charges capital for Finnish flood for the first time."
2. **The headline result is a ratio, and it does not depend on the load.** Joint pricing gives about **4.5–5×** the independence price for "≥2 in cluster" (code output). Also show that for "≥1 of cluster", independence **over-prices** (0.67–0.90×, code output). This proves the point is *getting the shape of the risk right*, not "everything is riskier". It is a strong, credible message for OP and PwC.
3. **Make March snowpack the "why now, every year" signal.** High-snow outlooks multiply the price by 3–5×. In the back-test, no payout ever followed a bottom-15 % snow year. Both are code outputs and in-sample, so say so.
4. **Frame quantum as the estimation engine**, honestly benchmarked and hardware-tested, with a quantum-ready roadmap. Use one slide or a 20-second demo segment, not the whole pitch.

### Product design: state these in the business plan

5. **Annual contract sold before the snow season**, with a purchase deadline around 1 December. Multi-year option. March outlook used for price adjustment and as an early-warning service. Annual also avoids pro-rata capital recognition.
6. **Reduce basis risk:**
   - a stepped payout (2 gauges = partial, 3 or more = full);
   - an optional dual trigger tied to the insurer's own loss;
   - the limit sized to the insurer's modelled 1-in-50 loss, with €10M as the illustrative unit.
7. **Structure it as reinsurance** with a rated reinsurer as the risk carrier. Tulva supplies the index, the calculation agent and the analytics.
8. **Scope honestly.** Lapland (North) is the core market. Ostrobothnia is shrinking. Satakunta–SE needs a winter and frazil module, which goes on the roadmap.

### Business model and go-to-market

9. **Revenue order:** (a) analytics and index licence to insurers and reinsurers; (b) structuring or data fee on placed covers; (c) grants (Business Finland R2B with a university and SYKE or FMI). Do not lead with "we become an underwriting agency".
10. **First customers:** OP/Pohjola and LocalTapiola (regional mutuals in Lapland and Ostrobothnia) for a pilot; If/Sampo as the internal-model buyer that can credit a pure index; one reinsurer's Nordic team as capacity partner.
11. **Timeline:** pilot in autumn ahead of the 1 January renewals. Launch narrative around the **30 January 2027** Solvency II flood module.
12. **Expansion:** Sweden and Norway, which have snowmelt rivers and new 2027 flood factors. Feed evidence into EIOPA's next recalibration (about 2027–2029).

### Pricing slide

13. Show **two prices**:
    - the "technical price" (expected loss × 1.35, current code);
    - a "market price" at about 2.5–3.5× expected loss, benchmarked to Flood Re Vision 2039 at about 3.4×.

    Ask Toivo **tonight** to add the 2.5×/3.5× load to `price_index.py` so the market price becomes a code output.
14. Mention model uncertainty: the bootstrap interval and the t-copula up-shift of 5–60 % are already in `CLAIMS.md`.

### Suggested 3-minute structure

| Time | Content |
|---|---|
| 0:00–0:30 | The problem: correlated spring floods, insurers pay together, a new Solvency II flood module in 2027 |
| 0:30–1:10 | The insight: shared snowpack. Cluster gauges cross 1-in-50 together about 4–5× more often than independence predicts; March snow shifts the odds (code outputs) |
| 1:10–1:40 | The product: Tulva Index, ≥2 gauges in a cluster, sold before winter, priced on joint risk and the snow outlook; a back-test year (for example North 2005) |
| 1:40–2:15 | The engine: QAE versus Monte Carlo at equal queries; IQM Q20 and IBM runs with measured error; no advantage claim |
| 2:15–2:45 | The business: licence, then structured cover with a reinsurer; OP/LocalTapiola pilot; the Nordics next |
| 2:45–3:00 | The ask: a pilot partner and data access |

### Prepare for these Q&A questions

- "EIOPA already has a Finnish correlation matrix, so why do we need you?"
- "Your load is far below market."
- "€10M is more than our loss."
- "What about basis risk?"
- "Won't insurers just buy in snowy years?"
- "Isn't spring flood risk disappearing?"
- "What did the hardware actually give you?"

Every answer is in Sections 3–7.

---

## 9. Claims in the current framing that need correcting

| # | Current framing | Problem | Corrected version |
|---|---|---|---|
| 1 | "Regulators assume independence (EIOPA: 0 % Nordic flood correlation)" (CLAUDE.md). Also "independence (EIOPA 0 %)" as the baseline label throughout `CLAIMS.md` | EIOPA's 0 % is the correlation **between Finland and other countries**. Within Finland, 2026/269 sets a 19-zone matrix with mean about 0.27 and many pairs at 0.75–1.00. The 0 % applies only **from 30 January 2027**; today Finnish flood has **no** flood parameter at all, not a 0 % one | "Solvency II's new Finnish flood module (from January 2027) sets Finland–Sweden/Norway/Denmark flood correlation at 0 %. EIOPA considered 25 % for snowmelt floods and rejected it (EIOPA-BoS-24/462 §4.70; Del. Reg. 2026/269 Annex IV). Within Finland it uses one vendor's static zone correlations, with no snowpack conditioning. Until then, Finnish flood carries no standard-formula capital." **Relabel the baseline "independence"**, not "EIOPA 0 %" |
| 2 | "14 river flood-risk areas" with no context | Officially there are **18 significant flood-risk areas for 2025–2030: 14 river + 4 coastal** (MMM, 19 December 2024). The team's list of 14 was not confirmed against the official annex | "the 14 river areas among Finland's 18 significant flood-risk areas (2025–2030)". Check Tornio, Huittinen and Kymijoki against the decision annex |
| 3 | Premium = expected payout × (1 + 35 % risk load) presented as *the* price | Market cat pricing is about **2.4–3.7× expected loss** (cat bonds 2024–26); flood deals about 2.9–3.4×. 1.35× is about a half to a third of market and does not cover the cost of capital | Call it the "technical price" and add a market price at 2.5–3.5× (code output once added). Keep the *ratio to independence*, which does not depend on the load, as the headline |
| 4 | "2024 Lapland flood" | No damaging 2024 Lapland spring flood was found in external sources. In 2024 the worst situation was **Ostrobothnia**; Ivalojoki was "clearly smaller than 2005" and below the damage limit. The **code** does flag 2024 as a North-cluster "≥2 over 1-in-10 discharge" year. That is a code output about **discharge**, not damage | Say "2024: North cluster had ≥2 gauges over their 1-in-10 discharge level (code output)". Never call it a damaging flood. For a damaging Lapland example, use **2005**, sourced externally |
| 5 | "SYKE's national totals implicitly assume everything floods at once" (CLAUDE.md) | Not checked by this research. National damage figures, such as the 1-in-250 scenario at €550M from a 2000 study, are scenario totals, and the method behind them was not reviewed | Drop it, or soften to "national damage scenarios add up area totals without a model of which areas flood together". Verify before use |
| 6 | Implicit "closing Finland's flood protection gap" (if used) | Finland's EIOPA protection-gap score is 4, among Europe's lowest; penetration is above 75 % per one study | Frame Tulva as an **insurer accumulation and capital** tool, not a consumer-gap tool |
| 7 | Implicit "an index cover gives Solvency II capital relief" (if used) | Under the standard formula, material basis risk means **zero** credit (EIOPA Q&A 1597). Relief is small even with full credit | "Recognisable as risk mitigation if basis risk is shown to be immaterial (or via an internal model); main value is earnings protection, ORSA and fast cash" |
| 8 | Implicit "nobody models Finnish flood" (if used) | Verisk's Central Europe flood model lists Finland. RMS says it models snowmelt (Finland coverage unconfirmed) | "Existing vendor models are pan-European and rainfall-driven. None prices *this season's* snowpack into joint Finnish flood risk" |
| 9 | Any wording such as "faster", "advantage" or "exponential" for QAE | Not defensible (Chakrabarti et al.; Kirke 2026) | Use the claims ladder in Section 7 |
| 10 | A €10M payout presented as matching insurer losses | The largest historical spring-flood events cost about €5–20M **in total across the market**. Insured flood claims in 2010–2015 were just over €5M **in total** | Present €10M as an illustrative unit; size real limits to each insurer's modelled 1-in-50 loss |

---

## 10. External figures that are safe to cite (log them in `CLAIMS.md` as `source`)

These are **not code outputs**. If any appears in the deck, add a `CLAIMS.md` line tagged `source` with the citation, and show the source on the slide.

| Figure | Source |
|---|---|
| Finnish non-life premiums €5.55bn (2024); fire and property €1.28bn | [Finance Finland 2024](https://www.finanssiala.fi/wp-content/uploads/2025/05/finnish-insurance-in-2024.pdf) |
| OP 32.6 %, LocalTapiola 28.3 %, If 21.9 %, Fennia 8.4 % of non-life (2024) | Finance Finland 2024 |
| State flood compensation ended 1 January 2014; home insurance pays for floods of 1-in-50 or rarer | [vesi.fi](https://www.vesi.fi/vesitieto/tulvavahinkojen-korvaaminen/); [HE 143/2013](https://www.edilex.fi/he/20130143) |
| 18 significant flood-risk areas (14 river + 4 coastal), 2025–2030 | [Valtioneuvosto 19 Dec 2024](https://valtioneuvosto.fi/-/1410837/suomen-merkittavat-tulvariskialueet-on-nimetty) |
| Finnish flood factor 0.04 %; Finland–Nordic flood correlation 0 %; applies from 30 January 2027 | [Del. Reg. 2026/269](https://lawplayer.com/eu/act/32026R0269); [EIOPA-BoS-24/462 §4.70](https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf) |
| 2005 Lapland flood about €5M house damage; snowpack about double normal | [Helminen (FMI)](https://sciencepolicy.colorado.edu/research_areas/sparc/research/projects/extreme_events/munich_workshop/helminen.pdf) |
| Cat bond loss multiples: 3.71× (2024), 3.0× (2025), about 2.4× (2026 to date) | [Artemis / AM Best, 25 Sep 2026](https://www.artemis.bm/news/as-cat-bond-loss-multiples-tighten-am-best-urges-investors-towards-greater-selectivity/) |
| Flood Re Vision 2039: 2.8 % attachment probability, 1.7 % expected loss, 5.0–5.75 % price | [Artemis](https://www.artemis.bm/news/flood-re-secures-40-upsized-140m-vision-2039-cat-bond-at-top-end-pricing/) |
| Cat bonds outstanding about $61bn (end-2025) | [Artemis](https://www.artemis.bm/news/catastrophe-bond-market-records-that-were-broken-in-2025/) |
| Spring 100-year floods −15 to −40 % by 2070–2099 | [Veijalainen et al. 2010](https://en.vedur.is/media/ces/Journal_of_Hydrology_Veijalainen_etal.pdf) |
| Kemijoki: "large spring floods are still common" in 2020–2049 | [SYKE 30/2026](https://www.kemijoki.fi/wp-content/uploads/2026/08/sykera2026-30veijalainenkemijoki.pdf) |
| About 8k logical qubits needed for a practical derivative-pricing advantage | [Chakrabarti et al. 2021](https://arxiv.org/abs/2012.03819v2) |

**Not safe without code or a stronger source:**

- my illustrative premiums at 2.5–4×;
- the capital-cost arithmetic;
- licence-price and revenue estimates;
- parametric market-size point estimates (quote only the range);
- the McKinsey quantum-finance value figures, which are contested ([PostQuantum](https://postquantum.com/quantum-computing/mckinsey-quantum-finance-600b/)).

---

## 11. Open gaps worth closing if time allows

- **The official list of the 14 river areas** (MMM decision annex). It affects the "14" claim and the cluster membership.
- **Insured losses for 2018, 2020 and 2024.** None were found. Finance Finland or an insurer contact could provide them.
- **Insurer reinsurance programmes and capital method** (standard formula or internal model). Read the SFCRs.
- **Where the Finnish Solvency II zones are.** Map zones 1–19 to regions (Annex IX) and check whether the high-weight zones 3, 7, 11 and 18 are Ostrobothnia, Lapland or the Lakeland. That would let the team compare Tulva's clusters with EIOPA's zone correlations directly. This would make a strong slide.
- **Prior art.** Check the Artemis deal directory for any Nordic flood cat bond before claiming "first".
- **The jury.** The 2026 jurors' titles and the PwC juror's focus were not verified.

---

## Sources (main)

- Finance Finland, *Finnish insurance in 2024*: https://www.finanssiala.fi/wp-content/uploads/2025/05/finnish-insurance-in-2024.pdf
- vesi.fi, Tulvavahinkojen korvaaminen: https://www.vesi.fi/vesitieto/tulvavahinkojen-korvaaminen/
- HE 143/2013: https://www.edilex.fi/he/20130143
- Valtioneuvosto, significant flood-risk areas (19 Dec 2024): https://valtioneuvosto.fi/-/1410837/suomen-merkittavat-tulvariskialueet-on-nimetty
- Delegated Regulation (EU) 2026/269: https://lawplayer.com/eu/act/32026R0269
- EIOPA Opinion BoS-24/462 (nat-cat reassessment): https://www.eiopa.europa.eu/document/download/13ce6bf5-44ce-41b1-bbb5-5ddddf81b6ac_en?filename=Opinion%20on%20the%202023%202024%20Reassessment%20exercise%20of%20the%20nat%20cat%20standard%20formula.pdf
- Delegated Regulation 2015/35, Arts. 123, 209–211, Annex XIII: https://www.legislation.gov.uk/eur/2015/35/
- EIOPA Q&A 1597: https://www.eiopa.europa.eu/qa-regulation/questions-and-answers-database/1597_en
- EIOPA protection-gap dashboard 2025: https://www.eiopa.europa.eu/tools-and-data/dashboard-insurance-protection-gap-natural-catastrophes_en
- Artemis (cat bond market, loss multiples, Flood Re Vision 2039, FloodSmart Re): https://www.artemis.bm
- Swiss Re FLOW: https://corporatesolutions.swissre.com/insights/news/flow_new_parametric_water_level_insurance.html
- PwC Switzerland, basis risk in parametric insurance (2024): https://www.pwc.ch/en/publications/2024/Basis_risk_in_parametric_insurance_challenges_and_mitigation_strategies.pdf
- Verisk Inland Flood Model coverage: https://docs.risksolutions.verisk.com/Touchstone/11.0/ts-tsre_all/help_ts_loss-analysis_flood-zones.html
- Business Finland R2B: https://www.businessfinland.fi/en/services/funding/calls/2026/r2b-funding-call-2-2026/
- Veijalainen et al. 2010: https://en.vedur.is/media/ces/Journal_of_Hydrology_Veijalainen_etal.pdf
- SYKE raportteja 30/2026: https://www.kemijoki.fi/wp-content/uploads/2026/08/sykera2026-30veijalainenkemijoki.pdf
- Lintunen et al. 2024: https://research.utu.fi/converis/portal/detail/Publication/387506879?lang=en_US
- Chakrabarti et al. 2021: https://arxiv.org/abs/2012.03819v2
- Kirke 2026: https://arxiv.org/abs/2603.15664
- OP–Qutwo (Global Finance): https://gfmag.com/technology/op-and-qutwo-debut-quantum-computing-partnership/
- IQM Qrisp backend: https://docs.iqm.tech/iqm-client/user_guide_qrisp/index.html
- Finland's Quantum Technology Strategy 2025–2035: https://valtioneuvosto.fi/en/-/1410877/strategy-quantum-technology-is-finland-s-new-driver-of-growth-and-builder-of-a-sustainable-future

Full source lists are in the six research notes in `business/research_notes/Tulva flood cover business case/`.
