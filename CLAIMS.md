# Claims

Every number in the deck: value · what produced it (exact / monte-carlo / qae-sim / qae-q20 / qae-ibm / source)
· script and commit.

## Numbers

### Joint flood data (spring Mar–Jun peaks, 14 areas, 1961–2025) · commit 60bebb0
- Areas over own 1-in-10 together, pairs within a cluster: **2.8×** independence (Ostrobothnia 3.2×, North 2.9×, Satakunta–SE 1.3×); between clusters **1.4×** · exact (counts) · scripts/fit_dependence.py → out/dependence.json
- Mean Spearman of spring peaks: **0.55 within cluster, 0.19 between** · exact · scripts/fit_dependence.py
- **≥4 of 14 areas over 1-in-10 in the same year: 10 of 65 years (15%)**; fitted model **12.2%**; independence (EIOPA 0%) **3.9%** (same gauge-years) · observed exact; model exact (quadrature), MC 200k agrees (full-14: 13.1% vs 13.0%) · scripts/fit_dependence.py → out/joint_counts.json
- ≥5 areas: observed 5 of 65 years (7.7%), model 7.4%, independence 0.8% · same
- Years with ≥4 areas: 1966, 1971, 1977, 1981, 1984, 1988, 2000, 2005, 2018, 2024; max 6 areas (1966) · exact
- Factor loadings (3 product clusters, one national loading): national **0.44** (90% bootstrap 0.31–0.54); cluster Ostrobothnia **0.64**, North **0.60**, Satakunta–SE **0.46** · least-squares fit + 400 year-bootstraps · out/model_params.json
- 1-in-50 level, all 14 areas, model vs independence: P(≥2) 6.0% vs 3.1%; **P(≥3) 2.5% vs 0.25% (10×)**; P(≥4) 1.1% vs 0.014% · exact (quadrature), model extrapolation · out/joint_counts.json
- Product trigger "≥2 gauges in cluster over 1-in-50": Ostrobothnia 2.6% vs 0.57% indep; North 2.0% vs 0.38%; Satakunta–SE 0.62% vs 0.12% · exact · out/model_params.json
- 1 March snow (SYKE areal SWE) vs cluster spring flood index, Spearman: Ostrobothnia **0.69**, North **0.39**, Satakunta–SE 0.53 · exact · out/snow_skill.json
- P(≥2 cluster areas over 1-in-10) in top-15% snow years vs other years: Ostrobothnia **60% vs 11%**, North **40% vs 7%**, Satakunta–SE 30% vs 0% (10 top years each) · exact (counts, in-sample) · out/snow_skill.json
- Outlook skill (corr of March SWE with the cluster's latent factor): Ostrobothnia 0.74, North 0.47, Satakunta–SE 0.68 · derived · out/snow_skill.json

## Simplified or assumed
- Flood = spring (Mar–Jun) peak daily discharge over the gauge's own empirical top-10% (1-in-10) / GEV 1-in-50; discharge is not damage; ice-jam/frazil floods (Pori in winter) are missed.
- Joint tail beyond observed (k≥6, 1-in-50 levels) is Gaussian-copula extrapolation (no tail dependence); at k≥6 the model is above observed (slightly conservative).
- Snow skill is in-sample on 10 top-snow years per cluster; wide uncertainty.
