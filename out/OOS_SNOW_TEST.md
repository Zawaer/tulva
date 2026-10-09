# Out-of-sample test of the March snow warning

Produced by `scripts/oos_snow_test.py` → `out/oos_snow_test.json` (exact counts and quadrature; intervals are
Clopper-Pearson or a 4,000-draw year bootstrap, both 90 %).

**What was frozen.** Everything that is fitted was fitted on the training springs only, then held fixed:
each gauge's GEV 1-in-10 level, the normal-score transforms, the copula loadings, the snow skill, and the
top-15 % snow cut-off. **Trigger** means at least 2 of a cluster's gauges went over the frozen 1-in-10 level.
**Flag** means the cluster's 1 March snow index was at or above the frozen cut-off. There are two splits, and
both are reported.

## Main split: fit 1961–2000, test 2001–2025

**Does March snow still rank the flood years?** Mostly yes. Spearman correlation between snow and the cluster
flood index:

| Cluster | Fit years | Test years (90 % CI) |
|---|---|---|
| Ostrobothnia | 0.65 | **0.69** (0.42–0.84) |
| North | 0.24 | **0.75** (0.53–0.87) |
| Satakunta–SE | 0.62 | 0.33 (−0.05–0.65) |

**Does the flag work?** This split cannot tell us. Since 2000 the snowpack is smaller, so the 1961–2000 cut-off
was reached only **twice in 75 cluster-years**:

- Ostrobothnia, 2024: no payout.
- North, 2020: payout.
- Satakunta–SE: never flagged.

Ostrobothnia and Satakunta–SE also never triggered after 2000. In Ostrobothnia the gauges passed their old
1-in-10 level in only 0.7 % of gauge-years, against 10 % expected. The North triggered 8 times.

Pooled over the three clusters:

- Flagged springs: **1 of 2 paid** (90 % CI 3–98 %).
- Unflagged springs: **7 of 73 paid** (10 %, 5–17 %).
- Fisher one-sided p = 0.20.

So the result is neither confirmed nor refuted.

The model, frozen on 1961–2000, expected 0.7 payouts in flagged years and 5.6 in unflagged years. The observed
1 and 7 are consistent with that in total. By cluster they are not: the model expected 2.7 payouts in
Ostrobothnia and saw none, and expected 2.8 in the North and saw 8.

**Predicted ratios from the 1961–2000 fit.** Payout risk in flagged vs unflagged years: Ostrobothnia 5.2×,
North 2.1×, Satakunta–SE 7.8×. The North fit gives a snow skill of only 0.31 (0.47 on all years), so the deck's
North "triples" quantity (1-in-50 cover, snowy vs normal March) comes out at **2.3×**, against 3.3× from the
full-record fit.

## Reverse split: fit 1986–2025, test 1961–1985

This is the robustness check. The early springs had more snow, so the frozen cut-off flagged 24 of 75
cluster-years.

Pooled over the three clusters:

- Flagged springs: **12 of 24 paid** (50 %, 32–68 %).
- Unflagged springs: **4 of 51 paid** (8 %, 3–17 %).
- Ratio 6.4×, Fisher p = 0.0001.
- The model expected 8.1 and 3.6 payouts.

By cluster:

- **Ostrobothnia:** 8/10 vs 3/15 (4.0×, bootstrap 1.9–15×, p = 0.005), Spearman 0.59.
- **Satakunta–SE:** 4/11 vs 0/14 (p = 0.026), Spearman 0.77.
- **North fails:** 0 of 3 flagged springs paid, and Spearman is −0.14. The North snow skill fitted on 1986–2025
  is 0.70; on 1961–2000 it is 0.31.

## Sensitivity (not the main test)

This variant uses a cut-off from the preceding 30 springs, which is known on 1 March. It is reported whatever
the result.

- Main test: 2 of 11 flagged vs 6 of 64 unflagged springs paid (p = 0.33).
- Reverse test: 9 of 20 vs 7 of 55 (p = 0.005). In the reverse test the trailing window is short in the early
  years.

## What this can and cannot show

- **Can:** the link between March snow and joint flooding is not just an artefact of fitting. It holds on unseen
  years in 4 of 6 cluster tests, and pooled in the reverse split. More snow ranks bigger joint floods.
- **Cannot:** confirm the size of the effect, "risk triples", on recent years. With 25 test springs and 0–1
  flags per cluster, any ratio has an interval spanning roughly 0× to infinity.
- **Cluster-level skill is unstable.** The North swings between 0.31 and 0.70 depending on the fit years.
  Satakunta–SE is weak after 2000.
- **The fixed snow cut-off is not stationary.** Snow and floods both shifted after 2000 (Ostrobothnia snow index
  −0.42 and flood index −0.42 on the old scale). An operational flag would need a re-based cut-off, and the
  1-in-10 levels need re-estimating too.
- **Pooled numbers are not independent.** The clusters share years, so pooled p-values are optimistic.
