/* Tulva demo app. All numbers come from web/data/*.json, written by scripts/export_web.py. */
"use strict";

const CLUSTER_COLOR = { "Ostrobothnia": "#2f6fde", "North": "#0f9e94", "Satakunta–SE": "#d4902a" };
const SRC_LABEL = {
  "exact": "exact", "monte-carlo": "Monte Carlo", "qae-sim": "QAE sim", "qae-sim-noisy": "QAE noisy sim",
  "qae-q20": "Q20", "qae-ibm": "IBM", "data": "observed", "placeholder": "placeholder",
};
const SRC_HELP = {
  "exact": "Exact value of the fitted model (quadrature / closed form), no sampling error.",
  "monte-carlo": "Classical Monte Carlo sampling of the same model.",
  "qae-sim": "Quantum amplitude estimation on an ideal (noise-free) simulator.",
  "qae-sim-noisy": "Quantum amplitude estimation on a noisy simulator; rehearsal, not hardware.",
  "qae-q20": "Quantum amplitude estimation run on the Aalto Q20 quantum computer (IQM, via LUMI).",
  "qae-ibm": "Quantum amplitude estimation run on IBM quantum hardware.",
  "data": "Observed data (SYKE / SMHI).",
  "placeholder": "Not a real result yet. Fills in automatically when the pipeline produces it.",
};
const NORTH = "North";

let APP, PRICING, BASEMAP;
// mode: "preset" (key low | clim | high, matching out/pricing.json), "pct" (slider), "latest" (observed March)
const state = { mode: "preset", key: "high", pct: 90 };

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function tag(src, note) {
  const t = (SRC_HELP[src] || "") + (note ? " " + note : "");
  return `<span class="src" data-src="${src}" title="${esc(t)}">${SRC_LABEL[src] || src}</span>`;
}
function pct(p, digits) {
  if (p == null || isNaN(p)) return "–";
  const v = p * 100;
  if (digits != null) return v.toFixed(digits) + " %";
  if (v >= 10) return v.toFixed(0) + " %";
  if (v >= 1) return v.toFixed(1) + " %";
  if (v >= 0.1) return v.toFixed(2) + " %";
  if (v >= 0.01) return v.toFixed(3) + " %";
  return "<0.01 %";
}
function eur(x) {
  if (x == null || isNaN(x)) return "–";
  if (x >= 1e6) return "€" + (x / 1e6).toFixed(2) + "M";
  if (x >= 1e3) return "€" + Math.round(x / 1e3) + "k";
  return "€" + Math.round(x);
}
function ordinal(n) { n = Math.round(n); const s = ["th", "st", "nd", "rd"], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }

/* ---------------------------------------------------------------- probabilities under the outlook */

function pAtPct(cl, p) {
  // log-linear interpolation on the exported 5..95 grid
  const g = cl.p_by_snow_pct.v;
  const x = Math.min(95, Math.max(5, p));
  const lo = Math.floor(x / 5) * 5, hi = Math.min(95, lo + 5);
  const a = g[String(lo)], b = g[String(hi)];
  if (hi === lo) return a;
  const t = (x - lo) / 5;
  return Math.exp(Math.log(a) * (1 - t) + Math.log(b) * t);
}
const PRESET_LABEL = { low: "Low-snow March (bottom 15 %)", clim: "No outlook (climatology)", high: "High-snow March (top 15 %)" };
function flatPrice(cluster, view) {
  return PRICING && PRICING.status === "ready" && PRICING.flat && PRICING.flat[cluster] ? PRICING.flat[cluster][view] : null;
}
// Probability of the >=2-of-n trigger under the current outlook: {v, src, note}
function pNow(name, cl) {
  if (state.mode === "preset") {
    const view = { low: "low", clim: "tulva", high: "high" }[state.key];
    const fp = flatPrice(name, view);
    if (fp && fp.p != null) return { v: fp.p, src: "exact", note: "out/pricing.json. " + fp.note };
    const own = { low: cl.p_low_outlook, clim: cl.p_tulva, high: cl.p_high_outlook }[state.key];
    return own;
  }
  const at = state.mode === "latest" ? cl.latest_march.pct : state.pct;
  return { v: pAtPct(cl, at), src: "exact", note: cl.p_by_snow_pct.note + ` (at the ${ordinal(at)} percentile)` };
}
// Index price under the current outlook: {v, src, note} or null
function priceNow(name, cl) {
  if (state.mode === "preset") return flatPrice(name, { low: "low", clim: "tulva", high: "high" }[state.key]);
  if (!PRICING || PRICING.status !== "ready" || PRICING.risk_load == null) return null;
  const p = pNow(name, cl).v;
  return { v: p * APP.payout_eur * (1 + PRICING.risk_load), src: "exact",
    note: `P × €10M × (1 + ${PRICING.risk_load} risk load), pricing rule from out/pricing.json applied to the slider probability.` };
}
function outlookLabel(cl) {
  if (state.mode === "latest") return `March ${cl.latest_march.year} snow (${ordinal(cl.latest_march.pct)} pct, observed)`;
  if (state.mode === "preset") return PRESET_LABEL[state.key];
  return `Scenario: ${ordinal(state.pct)} percentile March snow`;
}

/* ---------------------------------------------------------------- pricing.json (filled by another agent) */

function priceHTML(p) {
  if (p && p.v != null) return `<b>${eur(p.v)}</b> ${tag(p.src || "exact", p.note || "out/pricing.json")}`;
  return `<b class="ph">awaiting pricing</b> ${tag("placeholder", "Index price (with risk load) comes from out/pricing.json, not produced yet.")}`;
}

/* ---------------------------------------------------------------- 1. map */

const LABEL_DIR = { "Laihia": "left", "Lapväärtti": "left", "Pori": "left", "Tornio": "left", "Kittilä": "left",
  "Ylistaro–Koivulahti": "right", "Ilmajoki–Seinäjoki": "right" };

function baseMap(id) {
  const m = L.map(id, { zoomControl: false, attributionControl: true, scrollWheelZoom: false, dragging: !L.Browser.mobile,
    tap: false, zoomSnap: 0.1, doubleClickZoom: false });
  m.attributionControl.setPrefix(false).addAttribution("Outlines: Natural Earth");
  if (BASEMAP) L.geoJSON(BASEMAP, { interactive: false, style: (f) => f.properties.home
    ? { color: "#8fa6bd", weight: 1, fillColor: "#ffffff", fillOpacity: 1 }
    : { color: "#d3dce5", weight: 0.8, fillColor: "#eef2f6", fillOpacity: 1 } }).addTo(m);
  m.fitBounds([[59.75, 20.6], [70.05, 31.2]], { padding: [14, 14] });
  return m;
}

function drawMap() {
  const m = baseMap("leaf");
  const byName = Object.fromEntries(APP.areas.map((a) => [a.area, a]));
  APP.edges.forEach((e) => {
    const A = byName[e.a], B = byName[e.b];
    const same = A.cluster === B.cluster;
    L.polyline([[A.lat, A.lon], [B.lat, B.lon]], {
      color: same ? CLUSTER_COLOR[A.cluster] : "#7b8797", weight: 1 + (e.rho - 0.55) * 14,
      opacity: same ? 0.55 : 0.4, dashArray: same ? null : "4 4",
    }).bindTooltip(`${e.a} – ${e.b}: Spearman ρ = ${e.rho.toFixed(2)} (spring peaks 1961–2025, exact)`, { sticky: true }).addTo(m);
  });
  APP.areas.forEach((a) => {
    const c = L.circleMarker([a.lat, a.lon], { radius: 8, color: "#fff", weight: 2, fillColor: CLUSTER_COLOR[a.cluster], fillOpacity: 1 }).addTo(m);
    c.bindTooltip(a.area, { permanent: true, direction: LABEL_DIR[a.area] || "right", className: "lbl", offset: [LABEL_DIR[a.area] === "left" ? -6 : 6, 0] });
    c.bindPopup(`<b>${esc(a.area)}</b><br>${esc(a.gauge)} (${esc(a.source)})<br>${a.years} spring peaks · 1-in-10 ${a.q10} m³/s · 1-in-50 ${a.q50} m³/s<br>record ${a.record_max} m³/s (${a.record_max_year})`);
  });
}

function drawIntro() {
  $("#edge-min").textContent = APP.edge_min_spearman.toFixed(1);
  const j = APP.dependence.joint_1in10;
  $("#st-within").textContent = j.within.multiplier.toFixed(1) + "×";
  $("#st-years").textContent = APP.joint_counts.observed_years_ge4.length + " of 65";
  const ul = $("#legend");
  Object.entries(APP.clusters).forEach(([name, cl]) => {
    const mult = j[name] ? j[name].multiplier.toFixed(1) + "× joint floods" : "";
    ul.insertAdjacentHTML("beforeend", `<li><span class="dot" style="background:${CLUSTER_COLOR[name]}"></span>
      <span><b>${esc(name)}</b> · ${cl.n} areas · ${mult} <span class="who">${cl.areas.map(esc).join(", ")}</span></span></li>`);
  });
}

/* ---------------------------------------------------------------- 2. outlook tiles */

function setupOutlook() {
  const presets = [["Low snow (bottom 15 %)", "low"], ["No outlook", "clim"], ["High snow (top 15 %)", "high"],
    ["Observed March " + APP.clusters[NORTH].latest_march.year, "latest"]];
  const box = $("#presets");
  presets.forEach(([label, v]) => {
    const b = document.createElement("button");
    b.textContent = label;
    b.onclick = () => {
      if (v === "latest") state.mode = "latest";
      else { state.mode = "preset"; state.key = v; state.pct = { low: 10, clim: 50, high: 90 }[v]; }
      render();
    };
    b.dataset.v = v;
    box.appendChild(b);
  });
  const sl = $("#snow");
  sl.value = state.pct;
  sl.oninput = () => { state.mode = "pct"; state.pct = +sl.value; render(); };
}

function renderOutlook() {
  const sl = $("#snow");
  if (state.mode !== "latest") sl.value = state.pct;
  document.querySelectorAll("#presets button").forEach((b) => b.classList.toggle("on",
    state.mode === "latest" ? b.dataset.v === "latest" : state.mode === "preset" && b.dataset.v === state.key));
  $("#snow-val").innerHTML = state.mode === "latest"
    ? `Observed 1 March ${APP.clusters[NORTH].latest_march.year} snow, per cluster ${tag("data", APP.clusters[NORTH].latest_march.note)}`
    : state.mode === "preset" ? `Scenario: ${PRESET_LABEL[state.key]} in every cluster`
    : `Scenario: ${ordinal(state.pct)} percentile snowpack in every cluster (50th = typical year)`;
  const max = Math.max(...Object.values(APP.clusters).map((c) => c.p_by_snow_pct.v["95"]));
  const tiles = Object.entries(APP.clusters).map(([name, cl]) => {
    const pn = pNow(name, cl), p = pn.v;
    const rows = [
      ["Independent", cl.p_independent.v, "#9aa6b5", tag("exact", cl.p_independent.note)],
      ["Tulva, no outlook", cl.p_tulva.v, CLUSTER_COLOR[name] + "99", tag("exact", cl.p_tulva.note)],
      ["Tulva + snow", p, CLUSTER_COLOR[name]],
    ];
    const bars = rows.map(([l, v, col]) => `<div class="bar"><span>${l}</span><span class="track"><span class="fill" style="display:block;width:${Math.max(1, v / max * 100)}%;background:${col}"></span></span><span class="num">${pct(v)}</span></div>`).join("");
    return `<div class="tile" style="--cc:${CLUSTER_COLOR[name]}">
      <h3>${esc(name)}</h3><div class="sub">≥2 of ${cl.n} gauges over their 1-in-50 level · ${state.mode === "latest" ? ordinal(cl.latest_march.pct) + " pct snow in " + cl.latest_march.year : ""}</div>
      <div class="big">${pct(p)} <span class="unit">per spring</span> ${tag(pn.src, pn.note)}</div>
      <div class="bars">${bars}</div>
      <div class="price-row"><span>Expected payout on €10M ${tag("exact", "probability × €10M; pure premium before loadings")}</span><b>${eur(p * APP.payout_eur)}</b></div>
      <div class="price-row"><span>Index cover price</span><span>${priceHTML(priceNow(name, cl))}</span></div>
    </div>`;
  });
  $("#tiles").innerHTML = tiles.join("");
}

/* ---------------------------------------------------------------- 3. product card */

function renderCard() {
  const cl = APP.clusters[NORTH];
  const fpI = flatPrice(NORTH, "indep"), fpT = flatPrice(NORTH, "tulva");
  const boot = PRICING && PRICING.flat && PRICING.flat[NORTH] && PRICING.flat[NORTH].tulva_boot90;
  const views = [
    ["Regulator view<br>(independent floods)", cl.p_independent, fpI, false, ""],
    ["Tulva<br>(joint risk, no outlook)", cl.p_tulva, fpT, false,
      boot ? `90 % range ${eur(boot[0])}–${eur(boot[2])} ${tag("exact", "year-bootstrap refit of the loadings, out/pricing.json")}` : ""],
    [`Tulva + this March's snow<br><span style="font-weight:400">${outlookLabel(cl)}</span>`, pNow(NORTH, cl), priceNow(NORTH, cl), true, ""],
  ];
  $("#card").innerHTML = `
    <div class="kicker">Tulva Index · ${NORTH} cluster</div>
    <h2>Pays €10M if ≥2 of ${cl.n} gauges pass their 1-in-50 level</h2>
    <div class="terms">${cl.areas.map(esc).join(" · ")} · spring (Mar–Jun) peak discharge, SYKE / SMHI gauges</div>
    <div class="views">${views.map(([t, p, price, hl, extra]) => `
      <div class="view${hl ? " hl" : ""}">
        <div class="vt">${t}</div>
        <div class="vp">${pct(p.v)}</div>
        <div class="vs">chance per spring ${tag(p.src, p.note)}</div>
        <div class="vpr">Expected payout <b>${eur(p.v * APP.payout_eur)}</b> ${tag("exact", "probability × €10M")}</div>
        <div class="vpr">Index price ${priceHTML(price)}${extra ? `<div class="vs">${extra}</div>` : ""}</div>
      </div>`).join("")}</div>
    <div class="note">Independent view: each gauge 2 %/yr, no correlation (EIOPA standard formula sets Nordic flood correlation to 0).
      Tulva: Gaussian-copula factor model fitted to 1961–2025 spring peaks (×${(cl.p_tulva.v / cl.p_independent.v).toFixed(1)} vs independent).
      Snow view: conditioned on the cluster's 1 March SWE (in-sample skill ${cl.outlook_skill.toFixed(2)}). Move the snow slider above to update.</div>`;
}

/* ---------------------------------------------------------------- 4. under the hood */

function renderHood() {
  const q = APP.qae;
  if (!q) { $("#hood-body").innerHTML = `<p>${tag("placeholder")} out/qae_sim.json not available.</p>`; return; }
  const insts = [["kittila_ivalo_both", "Kittilä and Ivalo both pass 1-in-50"], ["lapland_atleast2of3", "≥2 of 3 Lapland areas pass 1-in-50"]];
  const hwRuns = APP.runs.filter((r) => r.src === "qae-q20" || r.src === "qae-ibm");
  const noisyRuns = APP.runs.filter((r) => r.src === "qae-sim-noisy");
  const panels = insts.map(([key, title]) => {
    const c = q.instances[key + "/climatology"], h = q.instances[key + "/high_march_outlook"];
    if (!c) return "";
    const runFor = (runs) => {
      for (const r of runs.slice().reverse()) {
        const k = Object.keys(r.instances || {}).find((n) => n.includes(key));
        if (k) return { run: r, res: r.instances[k] };
      }
      return null;
    };
    const hw = runFor(hwRuns), noisy = runFor(noisyRuns);
    const hwRow = hw
      ? `<tr><td>QAE on ${hw.run.backend === "q20" || hw.run.src === "qae-q20" ? "Aalto Q20" : esc(hw.run.backend)}${hw.run.ems ? " (EMS " + hw.run.ems + ")" : ""}, noise-aware</td><td class="v">${pct(hw.res.noise_aware_mlae)} ${tag(hw.run.src, `${hw.run.file}; raw MLAE ${pct(hw.res.raw_mlae)}; run's exact reference ${pct(hw.res.exact)}; params: ${hw.run.param_source}`)}</td></tr>`
      : `<tr><td>QAE on Aalto Q20 hardware</td><td class="v"><span class="ph">pending</span> ${tag("placeholder", "Hardware batch not run yet; fills in from out/runs/q20-*.analysis.json.")}</td></tr>`;
    const noisyNote = noisy ? `${noisy.run.file}; params: ${noisy.run.param_source}; run's exact ${pct(noisy.res.exact)}` : "qae_sim.json";
    return `<div class="panel">
      <h3>${title}</h3><div class="sub">Two-level factor model, ${c.qubits} qubits · ${q.trigger}</div>
      <div class="chips">
        <div class="chip"><b>${c.qubits}</b>qubits</div>
        <div class="chip"><b>${c.cz_by_k_grid.join(" / ")}</b>CZ gates for k = 0…${c.cz_by_k_grid.length - 1} Grover steps</div>
        <div class="chip"><b>${c.oracle_queries.toLocaleString("en")}</b>oracle queries</div>
      </div>
      <table class="cmp">
        <tr><th>Method</th><th style="text-align:right">P(trigger)</th></tr>
        <tr class="ref"><td>Exact (classical reference)</td><td class="v">${pct(c.exact, 3)} ${tag("exact", "statevector check, max error " + c.statevector_max_error.toExponential(0))}</td></tr>
        <tr><td>QAE, ideal simulator</td><td class="v">${pct(c.qae_ideal_mean, 3)} ± ${(c.qae_ideal_rmse * 100).toFixed(3)} pp ${tag("qae-sim", "mean ± RMSE over repeats")}</td></tr>
        <tr><td>Monte Carlo, same query budget</td><td class="v">± ${(c.mc_same_queries_rmse * 100).toFixed(3)} pp ${tag("monte-carlo", "RMSE with the same number of model evaluations")}</td></tr>
        <tr><td>QAE, noisy simulator (raw)</td><td class="v">${pct(noisy ? noisy.res.raw_mlae : c.qae_noisy_raw, 3)} ${tag("qae-sim-noisy", noisyNote)}</td></tr>
        ${hwRow}
        <tr><td>If independent</td><td class="v">${pct(c.if_independent, 3)} ${tag("exact")}</td></tr>
        ${h ? `<tr><td>Exact after a high March outlook</td><td class="v">${pct(h.exact, 3)} ${tag("exact", "top-15 % snow year; QAE sim " + pct(h.qae_ideal_mean, 3))}</td></tr>` : ""}
      </table>
    </div>`;
  });
  $("#hood-body").innerHTML = `<div class="hood-grid">${panels.join("")}</div>
    <p class="fine">At equal query budgets the ideal-simulator QAE error is smaller than Monte Carlo's
    (expected quadratic scaling); on today's noisy hardware the deeper circuits lose that edge, so hardware values are reported
    raw and with a noise-aware fit, next to the exact answer. Circuits are a two-level discretisation of the fitted model.</p>`;
}

/* ---------------------------------------------------------------- 5. year replay */

let map2, layer2;
function setupReplay() {
  map2 = baseMap("leaf2");
  layer2 = L.layerGroup().addTo(map2);
  const chips = $("#year-chips");
  [1966, 1984, 2005, 2018, 2024, 2025].forEach((y) => {
    const b = document.createElement("button");
    b.textContent = y; b.dataset.y = y;
    b.onclick = () => { $("#year").value = y; renderReplay(); };
    chips.appendChild(b);
  });
  $("#year").value = 2005;
  $("#year").oninput = renderReplay;
}

function renderReplay() {
  const y = String($("#year").value);
  document.querySelectorAll("#year-chips button").forEach((b) => b.classList.toggle("on", b.dataset.y === y));
  const peaks = APP.replay.peaks[y] || {};
  let over = 0, have = 0;
  layer2.clearLayers();
  const rows = APP.areas.map((a) => {
    const v = peaks[a.area];
    const lvl = a.q10_empirical, r = v == null ? null : v / lvl;
    const isOver = r != null && v > lvl;
    if (r != null) { have++; if (isOver) over++; }
    const col = CLUSTER_COLOR[a.cluster];
    L.circleMarker([a.lat, a.lon], {
      radius: isOver ? 11 : 7, color: r == null ? "#9aa6b5" : col, weight: 2,
      dashArray: r == null ? "2 3" : null, fillColor: col, fillOpacity: isOver ? 0.95 : 0.08,
    }).bindTooltip(`${a.area}: ${r == null ? "no data" : `${Math.round(v)} m³/s = ${(r * 100).toFixed(0)} % of its 1-in-10 level`}`).addTo(layer2);
    const w = r == null ? 0 : Math.min(r / 2, 1) * 100;
    return `<div class="rrow ${r == null ? "na" : isOver ? "over" : ""}"><span class="name">${esc(a.area)}</span>
      <span class="track" title="Line marks the 1-in-10 level (${lvl} m³/s)"><span class="fill" style="width:${w}%;background:${isOver ? col : col + "55"}"></span><span class="mark" style="left:50%"></span></span>
      <span class="num">${r == null ? "no data" : (r * 100).toFixed(0) + " %"}</span></div>`;
  });
  const swe = APP.replay.swe_national_pct[y];
  $("#replay-head").innerHTML = `<span class="big">${over} of ${have}</span> areas over their 1-in-10 level in spring ${y}
    ${tag("data", "Spring (Mar–Jun) peak daily discharge vs " + APP.replay.level_src)}<br>
    <span class="cap">1 March snow, national index: ${swe != null ? ordinal(swe) + " percentile" : "–"} ${tag("data", "SYKE areal SWE")} · bars: peak as % of 1-in-10 level (line = 100 %)</span>`;
  $("#replay-list").innerHTML = rows.join("");
}

/* ---------------------------------------------------------------- boot */

function render() { renderOutlook(); renderCard(); }

async function boot() {
  const bust = "?t=" + Date.now();
  APP = await fetch("data/app.json" + bust).then((r) => r.json());
  PRICING = await fetch("data/pricing.json" + bust).then((r) => r.json()).catch(() => null);
  BASEMAP = await fetch("data/basemap.json").then((r) => r.json()).catch(() => null);
  drawIntro();
  drawMap();
  setupOutlook();
  render();
  renderHood();
  setupReplay();
  renderReplay();
  document.querySelectorAll(".src:empty").forEach((s) => {
    const k = s.dataset.src; s.textContent = SRC_LABEL[k] || k; s.title = SRC_HELP[k] || "";
  });
  $("#gen").textContent = "Data exported " + APP.generated_utc + (PRICING && PRICING.status === "ready" ? " · prices from out/pricing.json" : " · prices pending (placeholder)");
}
boot();
