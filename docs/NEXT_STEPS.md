# Next steps (not built during the hackathon)

Ideas for after the event. Nothing here is implemented or tested yet.

## Better snow warning
- **Weekly snow tracking (Jan–Apr) instead of one 1 March reading.** SYKE estimates the snowpack through the winter.
  A risk number that updates every week, like a forecast: early readings give more time to react but less certainty,
  later readings more certainty but less time. Test which dates give the most useful warning.
- **Add the spring weather forecast.** How fast the snow melts depends on April–May temperatures and rain (FMI).
  A fast warm-up turns a big snowpack into a flood; a slow one doesn't.
- **Add ground frost and soil moisture.** Frozen or wet ground can't absorb meltwater.
- **Re-base the snow flag to recent winters.** Snowpacks shrank after 2000, so a cut-off fitted on 1961–2000 fired
  only twice in 2001–2025 (out/OOS_SNOW_TEST.md). Use a rolling or recent-years cut-off and re-estimate flood levels.
- **Out-of-sample checks on every addition** (fit on older years, test on newer ones), so improvements are real.

## Product and data
- **Pilot with one insurer's flood claims** to measure basis risk (index payouts vs real losses).
- **More rivers and regions:** all Finnish flood-risk areas, then Sweden and Norway (shared snowmelt rivers).
- **Water level instead of flow** where gauges allow, to match how home insurance terms define exceptional floods.

## Quantum
- Larger models (all Nordic basins, weekly updates) are where fewer simulation runs would matter. Revisit amplitude
  estimation when error-corrected hardware is available; keep classical Monte Carlo as the reference.
- Q50: more shots on calibration circuits, best-qubit layout, FiQCI error mitigation, then repeat runs.
