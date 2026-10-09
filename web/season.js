/* "This year" section: what the model said on 1 March 2026 vs what the rivers did. Data: web/data/season2026.json
   (scripts/season_2026.py; the model is fitted on 1961–2025 only, so 2026 is out of sample). */
"use strict";
(function () {
  const COLOR = { "Ostrobothnia": "#2f6fde", "North": "#0f9e94", "Satakunta–SE": "#d4902a" };
  const NAME = { "Ostrobothnia": "Pohjanmaa" };
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const pc = (p) => { const v = 100 * p; return (v >= 10 ? v.toFixed(0) : v >= 1 ? v.toFixed(1) : v >= 0.1 ? v.toFixed(2) : v < 0.005 ? "<0.01" : v.toFixed(2)) + " %"; };
  const ord = (n) => { n = Math.round(n); const s = ["th", "st", "nd", "rd"], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); };
  const snowWords = (p) => p < 15 ? "much less snow than usual" : p < 40 ? "less snow than usual" : p <= 60 ? "about a normal amount of snow" : p <= 85 ? "more snow than usual" : "much more snow than usual";
  const day = (iso) => { if (!iso) return ""; const d = new Date(iso); return d.getDate() + " " + ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][d.getMonth()]; };

  function verdict(c) {
    const exp = c.predicted.expected_areas_over_1in10, got = c.result.areas_over_1in10;
    if (exp < 0.5 && got === 0) return ["ok", "Quiet spring predicted, quiet spring came."];
    if (exp >= 1 && got >= 1) return ["ok", "Floods were expected, and they came."];
    if (exp < 0.5 && got >= 2) return ["miss", "A quiet spring was predicted, but rivers flooded."];
    if (exp >= 1.5 && got === 0) return ["miss", "Floods were expected, but none came."];
    return ["mixed", "Within what the model allowed for."];
  }

  function card(name, c) {
    const col = COLOR[name], p = c.predicted, r = c.result, [vcls, vtxt] = verdict(c);
    const maxRatio = Math.max(1.15, ...c.areas.map((a) => a.ratio_to_q10 || 0));
    const bars = c.areas.map((a) => {
      const ratio = a.ratio_to_q10, w = ratio == null ? 0 : Math.min(100, ratio / maxRatio * 100);
      const label = a.peak_2026 == null ? "no data" : `${Math.round(a.peak_2026)} m³/s, ${day(a.peak_date)}`;
      return `<div class="se-bar"><span class="se-area">${esc(a.area)}</span>
        <span class="se-track"><span class="se-mark" style="left:${100 / maxRatio}%"></span><span class="se-fill" style="width:${w}%;background:${a.over_1in10 ? "#d0342c" : col}"></span></span>
        <span class="se-num">${ratio == null ? "–" : Math.round(ratio * 100) + " %"}</span><span class="se-peak">${label}</span></div>`;
    }).join("");
    return `<div class="se-card" style="--cc:${col}">
      <div class="se-head"><h3>${esc(NAME[name] || name)}</h3><span class="se-n">${c.n} rivers</span></div>
      <div class="se-snow"><b>1 March 2026 snow: ${ord(c.snow_pct_2026)} percentile</b> · ${snowWords(c.snow_pct_2026)}</div>
      <div class="se-cols">
        <div class="se-col"><div class="se-lab">Said on 1 March</div>
          <div class="se-row"><span>Chance ≥2 rivers pass their 1-in-10 level</span><b>${pc(p.p_ge2_1in10)}</b><small>average year ${pc(p.p_ge2_1in10_average_year)}</small></div>
          <div class="se-row"><span>Chance the cover pays (≥2 pass 1-in-50)</span><b>${pc(p.p_ge2_1in50)}</b><small>average year ${pc(p.p_ge2_1in50_average_year)}</small></div>
          <div class="se-row"><span>Rivers expected over 1-in-10</span><b>${p.expected_areas_over_1in10.toFixed(2)}</b><small>average year ${p.expected_areas_over_1in10_average_year.toFixed(2)}</small></div>
        </div>
        <div class="se-col"><div class="se-lab">What happened by June</div>
          <div class="se-row"><span>Rivers over their 1-in-10 level</span><b>${r.areas_over_1in10} of ${c.n}</b></div>
          <div class="se-row"><span>Rivers over their 1-in-50 level</span><b>${r.areas_over_1in50} of ${c.n}</b></div>
          <div class="se-row"><span>Cover pays?</span><b>${r.payout ? "Yes" : "No"}</b></div>
        </div>
      </div>
      <div class="se-lab">Spring 2026 peak, as a share of each river's 1-in-10 level <span class="se-hint">(line = 100 %)</span></div>
      <div class="se-bars">${bars}</div>
      <div class="se-verdict ${vcls}">${vtxt}</div>
    </div>`;
  }

  async function boot() {
    let D;
    try { D = await fetch("data/season2026.json?v=" + Date.now()).then((r) => r.json()); } catch (e) { return; }
    const el = $("#season-body");
    if (!el) return;
    const cls = Object.entries(D.clusters);
    const over10 = cls.reduce((s, [, c]) => s + c.result.areas_over_1in10, 0);
    const n = cls.reduce((s, [, c]) => s + c.n, 0);
    const pay = cls.filter(([, c]) => c.result.payout).length;
    const quiet = cls.filter(([, c]) => c.predicted.expected_areas_over_1in10 < c.predicted.expected_areas_over_1in10_average_year).length;
    $("#season-sum").innerHTML = `
      <div class="stat"><div class="big">${n - over10} of ${n}</div><div class="cap">rivers stayed below their 1-in-10 level in spring ${D.year} <span class="src" data-src="data">observed</span></div></div>
      <div class="stat"><div class="big">${pay === 0 ? "No" : pay}</div><div class="cap">${pay === 0 ? "payout anywhere" : "regions with a payout"} · the model gave ${quiet === cls.length ? "every region" : quiet + " of " + cls.length + " regions"} a below-average chance on 1 March <span class="src" data-src="exact">exact</span></div></div>`;
    el.innerHTML = cls.map(([name, c]) => card(name, c)).join("");
    $("#season-foot").textContent = `Model fitted on ${D.fitted_on}; ${D.year} is a year it never saw. One year is one data point: a quiet year agreeing with a low chance is consistent, not proof. ${D.sources}.`;
  }
  document.addEventListener("DOMContentLoaded", boot);
})();
