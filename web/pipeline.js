/* "How it works": one worked example from data to answer. Data: web/data/pipeline.json (scripts/export_pipeline.py). */
"use strict";
(function () {
  const C = { k: "#0f9e94", i: "#2f6fde", both: "#d0342c", line: "#e3e8ef", ink: "#1c2b40", muted: "#5d6b7e",
    navy: "#0b1f3a", snow: "#7fb3d9", band: "#eef5fb", none: "#e8edf3" };
  const SNOW_LABEL = { low: "Low-snow March", clim: "Normal March", high: "Snowy March" };
  let D, mode = "high";
  const $ = (s) => document.querySelector(s);
  const pc = (p, d = 3) => (100 * p).toFixed(d) + " %";
  const n = (x) => Math.round(x).toLocaleString("en");

  function riverSvg() {
    const yrs = Object.keys(D.rivers["Kittilä"].peaks).map(Number).sort((a, b) => a - b);
    const W = 1000, rowH = 120, top = 10, gap = 30, x0 = 70, bw = (W - x0 - 10) / yrs.length;
    let s = "";
    ["Kittilä", "Ivalo"].forEach((a, r) => {
      const R = D.rivers[a], vals = yrs.map((y) => R.peaks[y]), max = Math.max(...vals.filter((v) => v != null), R.q50) * 1.08;
      const y0 = top + r * (rowH + gap), base = y0 + rowH, sc = (v) => (v / max) * rowH;
      s += `<text x="0" y="${y0 + 16}" font-size="15" font-weight="700" fill="${a === "Kittilä" ? C.k : C.i}">${a}</text>`;
      s += `<text x="0" y="${y0 + 34}" font-size="12" fill="${C.muted}">m³/s</text>`;
      yrs.forEach((y, i) => {
        const v = R.peaks[y];
        if (v == null) return;
        const both = v > R.q50 && D.rivers[a === "Kittilä" ? "Ivalo" : "Kittilä"].peaks[y] > D.rivers[a === "Kittilä" ? "Ivalo" : "Kittilä"].q50;
        s += `<rect x="${x0 + i * bw + 1}" y="${base - sc(v)}" width="${bw - 2}" height="${sc(v)}" rx="1.5" fill="${both ? C.both : (a === "Kittilä" ? C.k : C.i)}" opacity="${both ? 1 : 0.55}"><title>${y}: ${v} m³/s</title></rect>`;
      });
      const yl = base - sc(R.q50);
      s += `<line x1="${x0}" x2="${W - 10}" y1="${yl}" y2="${yl}" stroke="${C.navy}" stroke-dasharray="5 4" stroke-width="1.5"/>`;
      s += `<text x="${W - 12}" y="${yl - 6}" font-size="12" text-anchor="end" fill="${C.navy}">1-in-50 level: ${n(R.q50)} m³/s</text>`;
      s += `<line x1="${x0}" x2="${W - 10}" y1="${base}" y2="${base}" stroke="${C.line}"/>`;
    });
    const yb = top + 2 * rowH + gap + 18;
    [1961, 1980, 2000, 2005, 2025].forEach((y) => {
      const i = yrs.indexOf(y);
      if (i >= 0) s += `<text x="${x0 + (i + 0.5) * bw}" y="${yb}" font-size="12" text-anchor="middle" fill="${y === 2005 ? C.both : C.muted}" font-weight="${y === 2005 ? 700 : 400}">${y}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${yb + 6}" role="img" aria-label="Spring peak river flow at Kittilä and Ivalo, 1961 to 2025">${s}</svg>`;
  }

  function snowSvg() {
    const S = D.snow, yrs = Object.keys(S.mm).map(Number).sort((a, b) => a - b);
    const W = 1000, H = 130, x0 = 70, bw = (W - x0 - 10) / yrs.length, max = Math.max(...Object.values(S.mm)) * 1.08;
    const sc = (v) => (v / max) * H, base = H + 10;
    let s = `<text x="0" y="26" font-size="15" font-weight="700" fill="${C.ink}">Snow</text><text x="0" y="44" font-size="12" fill="${C.muted}">mm water</text>`;
    const lo = S.p15, hi = S.p85;
    const band = mode === "high" ? [hi, max] : mode === "low" ? [0, lo] : [lo, hi];
    s += `<rect x="${x0}" y="${base - sc(band[1])}" width="${W - x0 - 10}" height="${sc(band[1]) - sc(band[0])}" fill="${C.band}"/>`;
    s += `<text x="${W - 12}" y="${base - sc(band[1]) + 15}" font-size="12" text-anchor="end" fill="${C.navy}">${SNOW_LABEL[mode]}: ${mode === "high" ? "above " + hi : mode === "low" ? "below " + lo : lo + "–" + hi} mm</text>`;
    yrs.forEach((y, i) => {
      const v = S.mm[y], inb = v >= band[0] && v <= band[1];
      s += `<rect x="${x0 + i * bw + 1}" y="${base - sc(v)}" width="${bw - 2}" height="${sc(v)}" rx="1.5" fill="${y === 2005 ? C.both : C.snow}" opacity="${inb || y === 2005 ? 1 : 0.35}"><title>${y}: ${v} mm</title></rect>`;
    });
    s += `<line x1="${x0}" x2="${W - 10}" y1="${base}" y2="${base}" stroke="${C.line}"/>`;
    [1961, 1980, 2000, 2005, 2025].forEach((y) => {
      const i = yrs.indexOf(y);
      if (i >= 0) s += `<text x="${x0 + (i + 0.5) * bw}" y="${base + 18}" font-size="12" text-anchor="middle" fill="${y === 2005 ? C.both : C.muted}" font-weight="${y === 2005 ? 700 : 400}">${y}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${base + 24}" role="img" aria-label="Snow on 1 March in the Kittilä and Ivalo catchments">${s}</svg>`;
  }

  function circuitSvg(c) {
    const W = 1000, rows = [["Wet spring?", c.p_wet], ["River A floods?", null], ["River B floods?", null]], y = (r) => 40 + r * 62;
    let s = "";
    rows.forEach(([lab], r) => {
      s += `<text x="0" y="${y(r) + 5}" font-size="15" font-weight="600" fill="${C.ink}">${lab}</text>`;
      s += `<text x="150" y="${y(r) + 5}" font-size="13" fill="${C.muted}">qubit ${r + 1}</text>`;
      s += `<line x1="215" x2="${W - 70}" y1="${y(r)}" y2="${y(r)}" stroke="${C.ink}" stroke-width="1.5"/>`;
    });
    const box = (x, r, t, fill) => `<rect x="${x - 58}" y="${y(r) - 18}" width="116" height="36" rx="6" fill="${fill}" stroke="${C.ink}" stroke-width="1"/><text x="${x}" y="${y(r) + 5}" font-size="13" text-anchor="middle" fill="${C.ink}">${t}</text>`;
    s += box(300, 0, `set ${Math.round(100 * c.p_wet)} % yes`, "#e3f1fa");
    [[1, 470, C.k], [2, 650, C.i]].forEach(([r, x, col]) => {
      s += `<line x1="${x}" x2="${x}" y1="${y(0)}" y2="${y(r) - 18}" stroke="${C.ink}" stroke-width="1.5"/><circle cx="${x}" cy="${y(0)}" r="6" fill="${C.ink}"/>`;
      s += box(x, r, `${pc(c.p_flood_dry, 2)} / ${(100 * c.p_flood_wet).toFixed(1)} %`, "#fff");
      s += `<rect x="${x - 58}" y="${y(r) + 18}" width="116" height="4" fill="${col}"/>`;
    });
    rows.forEach((_, r) => {
      if (r === 0) return;
      const x = W - 50;
      s += `<rect x="${x - 22}" y="${y(r) - 18}" width="44" height="36" rx="6" fill="#fff" stroke="${C.ink}"/><path d="M${x - 13} ${y(r) + 8} A 14 14 0 0 1 ${x + 13} ${y(r) + 8}" fill="none" stroke="${C.ink}" stroke-width="1.5"/><line x1="${x}" y1="${y(r) + 8}" x2="${x + 9}" y2="${y(r) - 8}" stroke="${C.ink}" stroke-width="1.5"/>`;
    });
    s += `<text x="${W - 50}" y="${y(2) + 46}" font-size="12" text-anchor="middle" fill="${C.muted}">read 0 or 1</text>`;
    s += `<text x="560" y="${y(2) + 46}" font-size="12" text-anchor="middle" fill="${C.muted}">each river: chance of flooding in a dry / wet spring</text>`;
    return `<svg viewBox="0 0 ${W} ${y(2) + 56}" role="img" aria-label="The three-qubit circuit">${s}</svg>`;
  }

  function drawShots(c) {
    const cv = $("#pl-canvas"), cols = 100, rows = 80, cell = 6;
    cv.width = cols * cell; cv.height = rows * cell;
    const ctx = cv.getContext("2d"), k = c.shots_k0, tot = c.shots_k0_total;
    const cells = [];
    const push = (key, m) => { for (let i = 0; i < m; i++) cells.push(key); };
    push("11", k["11"]); push("01", k["01"]); push("10", k["10"]); push("00", tot - k["11"] - k["01"] - k["10"]);
    let seed = 7;   // fixed shuffle so the picture is the same every time
    for (let i = cells.length - 1; i > 0; i--) { seed = (seed * 16807) % 2147483647; const j = seed % (i + 1); [cells[i], cells[j]] = [cells[j], cells[i]]; }
    const col = { "00": C.none, "01": C.k, "10": C.i, "11": C.both };
    cells.forEach((key, i) => {
      ctx.fillStyle = col[key];
      const x = (i % cols) * cell, y = Math.floor(i / cols) * cell;
      if (key === "11") ctx.fillRect(x - 1, y - 1, cell + 1, cell + 1); else ctx.fillRect(x, y, cell - 1, cell - 1);
    });
    $("#pl-leg").innerHTML = [["00", "no flood", C.none], ["01", "river A only", C.k], ["10", "river B only", C.i], ["11", "both flood", C.both]]
      .map(([b, t, cl]) => `<div><i style="background:${cl}"></i><span><code>${b}</code> ${t}</span><b>${n(k[b])}</b></div>`).join("")
      + `<div style="color:var(--muted);font-size:13px;grid-template-columns:1fr">Total ${n(tot)} shots on IQM Emerald</div>`;
  }

  function answer(c) {
    const rawK0 = c.shots_k0["11"] / c.shots_k0_total;
    const rows = [
      ["raw", `Raw count (${c.shots_k0["11"]} of ${n(c.shots_k0_total)} shots)`, rawK0],
      ["hw", `Quantum answer, noise-corrected<br><small>${n(c.shots_total)} shots, ${c.copies} copies side by side</small>`, c.estimate],
      ["ex", "Exact answer (normal computer)", c.exact],
    ];
    if (mode === "clim") rows.push(["ind", "If the rivers flooded independently", D.independent]);
    const max = Math.max(...rows.map((r) => r[2]));
    $("#pl-ans").innerHTML = rows.map(([cls, lab, v]) =>
      `<div class="row ${cls}"><span>${lab}</span><div class="bar" style="width:${Math.max(1, (100 * v) / max)}%"></div><b>${pc(v)}</b></div>`).join("");
  }

  function render() {
    const c = D.cases[mode];
    document.querySelectorAll(".pl-snow button").forEach((b) => b.classList.toggle("on", b.dataset.k === mode));
    $("#pl-snowsvg").innerHTML = snowSvg();
    $("#pl-nums").innerHTML = `
      <div class="pl-num-tile"><div class="v ch">${Math.round(100 * c.p_wet)} %</div><div class="k">chance of a wet spring in the north (changes with the snow)</div></div>
      <div class="pl-num-tile"><div class="v">${pc(c.p_flood_dry, 2)}</div><div class="k">chance one river floods in a dry spring</div></div>
      <div class="pl-num-tile"><div class="v">${(100 * c.p_flood_wet).toFixed(1)} %</div><div class="k">chance one river floods in a wet spring</div></div>`;
    $("#pl-circ").innerHTML = circuitSvg(c);
    const g = c.two_qubit_gates_by_k;
    $("#pl-circcap").textContent = `On the chip this is ${g[0]} two-qubit steps. The amplified versions, which make rare floods easier to see, use ${g[1]} and ${g[2]}.`;
    drawShots(c);
    answer(c);
  }

  function allDataSvg() {
    const CLC = { "Ostrobothnia": "#2f6fde", "North": "#0f9e94", "Satakunta–SE": "#d4902a" };
    const yrs = []; for (let y = 1961; y <= 2025; y++) yrs.push(y);
    const W = 1000, x0 = 230, bw = (W - x0 - 10) / yrs.length, rowH = 26, gapH = 8;
    let y = 8, s = "";
    const row = (label, sub, vals, color, thresh, markHi) => {
      const v = yrs.map((yy) => vals[yy]), nums = v.filter((a) => a != null);
      const lo = Math.min(0, ...nums), hi = Math.max(...nums, thresh || 0) * 1.05 || 1, sc = (a) => ((a - lo) / (hi - lo)) * (rowH - 4);
      s += `<text x="0" y="${y + 15}" font-size="12.5" font-weight="600" fill="${C.ink}">${label}</text>`;
      if (sub) s += `<text x="118" y="${y + 15}" font-size="11" fill="${C.muted}">${sub}</text>`;
      yrs.forEach((yy, i) => {
        const a = vals[yy]; if (a == null) return;
        const over = thresh != null && a > thresh, big = markHi && a >= markHi;
        s += `<rect x="${x0 + i * bw + 0.6}" y="${y + rowH - 2 - sc(a)}" width="${bw - 1.2}" height="${Math.max(0.8, sc(a))}" fill="${over || big ? C.both : color}" opacity="${over || big ? 1 : 0.6}"><title>${yy}: ${Number.isInteger(a) ? a : a.toFixed(1)}</title></rect>`;
      });
      if (thresh != null) { const yl = y + rowH - 2 - sc(thresh); s += `<line x1="${x0}" x2="${W - 10}" y1="${yl}" y2="${yl}" stroke="${C.navy}" stroke-width="1" stroke-dasharray="3 3"/>`; }
      y += rowH;
    };
    for (const [cl, E] of Object.entries(D.all_data)) {
      s += `<text x="0" y="${y + 14}" font-size="13" font-weight="700" fill="${CLC[cl]}" letter-spacing=".06em">${(cl === "Ostrobothnia" ? "Pohjanmaa" : cl).toUpperCase()}</text>`;
      y += 22;
      E.areas.forEach((A) => row(A.area, "river flow, m³/s", A.peaks, CLC[cl], A.q50));
      const snowVals = Object.values(E.snow_mm).filter((a) => a != null).sort((a, b) => a - b);
      row("Snow 1 March", "mm water", E.snow_mm, C.snow, null, snowVals[Math.floor(snowVals.length * 0.85)]);
      if (E.temp_c) {
        row("Apr–May temp", "°C, " + E.station, E.temp_c, "#c98a3a", null);
        row("Apr–May rain", "mm, " + E.station, E.rain_mm, "#6f8fb0", null);
      }
      y += gapH;
    }
    [1961, 1980, 2000, 2005, 2025].forEach((yy) => {
      const i = yrs.indexOf(yy);
      s += `<text x="${x0 + (i + 0.5) * bw}" y="${y + 12}" font-size="12" text-anchor="middle" fill="${yy === 2005 ? C.both : C.muted}" font-weight="${yy === 2005 ? 700 : 400}">${yy}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${y + 20}" role="img" aria-label="All input data: spring peaks of 14 rivers, snow, temperature and rain, 1961 to 2025">${s}</svg>`;
  }

  async function boot() {
    try { D = await fetch("data/pipeline.json?v=" + Date.now()).then((r) => r.json()); } catch (e) { return; }
    $("#pl-rivers").innerHTML = riverSvg();
    if (D.all_data && $("#pl-all")) $("#pl-all").innerHTML = allDataSvg();
    document.querySelectorAll(".pl-snow button").forEach((b) => b.addEventListener("click", () => { mode = b.dataset.k; render(); }));
    render();
  }
  document.addEventListener("DOMContentLoaded", boot);
})();
