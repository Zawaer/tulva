import React, { useLayoutEffect, useRef } from "react";
import data from "../data.json";
import { C, clamp01, fmt, mix, ramp, word } from "../theme";

// Beat 3: the 8,000 real IQM Emerald shots of the app's "How it works" step 5 (web/pipeline.js drawShots: same
// counts, same fixed shuffle), low-snow March, then snowy March; then the corrected ratio vs exact.
type Key = "00" | "01" | "10" | "11";
const COLS = 100, ROWS = 80, PITCH = 9.5, SQ = 7.6;
const COL: Record<Key, string> = { "00": C.none, "01": C.riverA, "10": C.riverB, "11": C.both };
const cases = data.shots.cases;

function layout(k: Record<string, number>, total: number): Key[] {
  const cells: Key[] = [];
  const push = (key: Key, m: number) => { for (let i = 0; i < m; i++) cells.push(key); };
  push("11", k["11"]); push("01", k["01"]); push("10", k["10"]); push("00", total - k["11"] - k["01"] - k["10"]);
  let seed = 7; // web/pipeline.js: fixed shuffle so the picture is the same every time
  for (let i = cells.length - 1; i > 0; i--) {
    seed = (seed * 16807) % 2147483647;
    const j = seed % (i + 1);
    [cells[i], cells[j]] = [cells[j], cells[i]];
  }
  return cells;
}
const LOW = layout(cases.low.shots, cases.low.total);
const HIGH = layout(cases.high.shots, cases.high.total);
const hash = (i: number, k: number) => ((Math.sin(i * 91.345 + k * 47.853) * 43758.5453) % 1 + 1) % 1;
const APPEAR = LOW.map((_, i) => Math.pow(hash(i, 1), 0.8));
const SWITCH = LOW.map((_, i) => (i % COLS) / COLS * 0.55 + hash(i, 2) * 0.15);

const PILL = [200, 250]; // toggle pill widths (px)
const GRID = { x: 132, y: 92, w: COLS * PITCH, h: ROWS * PITCH };

const Grid: React.FC<{ t: number }> = ({ t }) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const tEach = word(3, "each"), tRed = word(3, "red"), tSnowy = word(3, "snowy");
  useLayoutEffect(() => {
    const cv = ref.current!;
    const ctx = cv.getContext("2d")!;
    ctx.setTransform(2, 0, 0, 2, 0, 0);
    ctx.clearRect(0, 0, GRID.w, GRID.h);
    const fill = clamp01((t - (tEach - 0.25)) / 2.6);
    const dim = 0.62 * ramp(t, tRed - 0.15, tRed + 0.35) * (1 - 0.55 * ramp(t, tSnowy + 1.6, tSnowy + 2.4));
    const reds: [number, number, number][] = [];
    for (let i = 0; i < LOW.length; i++) {
      const a = clamp01((fill - APPEAR[i] * 0.9) / 0.1);
      const x = (i % COLS) * PITCH, y = Math.floor(i / COLS) * PITCH;
      ctx.globalAlpha = 1;
      ctx.fillStyle = "#f1f4f8";
      ctx.fillRect(x, y, SQ, SQ);
      if (a <= 0) continue;
      const sw = t - tSnowy - SWITCH[i];
      const key = sw >= 0 ? HIGH[i] : LOW[i];
      if (key === "11") { reds.push([x, y, sw >= 0 ? tSnowy + SWITCH[i] : tRed]); continue; }
      ctx.globalAlpha = a * (key === "00" ? 1 : 1 - dim);
      ctx.fillStyle = COL[key];
      ctx.fillRect(x, y, SQ, SQ);
    }
    for (const [x, y, t0] of reds) {          // red on top, bigger, with a ring when it first shows
      const a = clamp01((fill - 0.2) / 0.2);
      ctx.globalAlpha = a;
      ctx.fillStyle = C.both;
      ctx.fillRect(x - 2, y - 2, SQ + 4, SQ + 4);
      const r = clamp01((t - t0) / 0.9);
      if (r > 0 && r < 1) {
        ctx.globalAlpha = a * (1 - r);
        ctx.strokeStyle = C.both;
        ctx.lineWidth = 3 * (1 - r) + 0.5;
        ctx.beginPath();
        ctx.arc(x + SQ / 2, y + SQ / 2, 6 + 22 * r, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
  }, [t, tEach, tRed, tSnowy]);
  return <canvas ref={ref} width={GRID.w * 2} height={GRID.h * 2} style={{ width: GRID.w, height: GRID.h, display: "block" }} />;
};

export const ShotsScene: React.FC<{ t: number }> = ({ t }) => {
  const tEach = word(3, "each"), tRed = word(3, "red"), tSnowy = word(3, "snowy"), tAbout = word(3, "about");
  const tThree = word(3, "three"), tTwo = word(3, "two");
  const sw = ramp(t, tSnowy, tSnowy + 0.7);
  const fill = clamp01((t - (tEach - 0.25)) / 2.6);
  const shown = Math.round(8000 * fill);
  const count = (k: Key) => mix(cases.low.shots[k], cases.high.shots[k], sw) * fill;
  const ratioIn = ramp(t, tAbout - 0.25, tAbout + 0.3);
  const chipBar = ramp(t, tThree - 0.1, tThree + 0.6), exactBar = ramp(t, tTwo - 0.1, tTwo + 0.6);
  const MAXX = 4;
  const r = data.ratio;
  const redFocus = ramp(t, tRed - 0.15, tRed + 0.35);
  const rows: [Key, string][] = [["00", "no flood"], ["01", "river A only"], ["10", "river B only"], ["11", "both flood"]];
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: GRID.x - 24, top: GRID.y - 24, width: GRID.w + 48, height: GRID.h + 48,
        background: "#fff", borderRadius: 16, boxShadow: "0 24px 70px rgba(0,0,0,.4)" }} />
      <div style={{ position: "absolute", left: GRID.x, top: GRID.y }}><Grid t={t} /></div>

      <div style={{ position: "absolute", left: 1170, top: 72, width: 650 }}>
        <div style={{ fontSize: 22, letterSpacing: "0.16em", color: C.pale, fontWeight: 600 }}>REAL QUANTUM HARDWARE</div>
        <div style={{ fontSize: 50, fontWeight: 800, marginTop: 8, letterSpacing: "-0.01em" }}>IQM Emerald</div>
        <div style={{ fontSize: 26, color: "#dbe5f3", marginTop: 4 }}>
          <b style={{ color: C.white }}>{fmt(shown)}</b> shots · one square = one simulated spring
        </div>
        <div style={{ display: "flex", gap: 0, marginTop: 30, background: C.navy3, borderRadius: 30, padding: 5, width: "fit-content",
          position: "relative" }}>
          <div style={{ position: "absolute", top: 5, bottom: 5, left: mix(5, 5 + PILL[0], sw), width: mix(PILL[0], PILL[1], sw), borderRadius: 26,
            background: C.white }} />
          {["Low snow", "Snowy March"].map((l, k) => (
            <div key={l} style={{ position: "relative", padding: "12px 0", fontSize: 28, fontWeight: 700, whiteSpace: "nowrap",
              width: PILL[k], boxSizing: "border-box", textAlign: "center", color: (k === 0 ? 1 - sw : sw) > 0.5 ? C.navy : "#c9d6e8" }}>{l}</div>
          ))}
        </div>
        <div style={{ marginTop: 30, display: "grid", gap: 10 }}>
          {rows.map(([k, label]) => {
            const red = k === "11";
            return (
              <div key={k} style={{ display: "grid", gridTemplateColumns: "30px 52px 1fr auto", alignItems: "center", gap: 14,
                fontSize: red ? 34 : 27, fontWeight: red ? 800 : 500, opacity: red ? 1 : 1 - 0.45 * redFocus,
                color: red ? "#ff8a80" : "#dbe5f3" }}>
                <div style={{ width: red ? 28 : 24, height: red ? 28 : 24, borderRadius: 5, background: COL[k],
                  boxShadow: red ? `0 0 ${18 * redFocus}px ${C.both}` : undefined }} />
                <code style={{ fontFamily: "SF Mono, Menlo, monospace", fontSize: 22, color: C.muted }}>{k}</code>
                <span>{label}</span>
                <b style={{ fontVariantNumeric: "tabular-nums", color: red ? "#fff" : undefined }}>{fmt(count(k))}</b>
              </div>
            );
          })}
        </div>

        <div style={{ marginTop: 34, opacity: ratioIn, transform: `translateY(${(1 - ratioIn) * 24}px)`, background: C.navy2,
          border: "1px solid #2a4a78", borderRadius: 16, padding: "22px 26px 18px" }}>
          <div style={{ fontSize: 28, fontWeight: 700 }}>Snowy vs low snow: risk ratio</div>
          {[["On the chip (corrected)", r.chip, chipBar, C.red], ["Exact (classical)", r.exact, exactBar, C.pale]].map(
            ([label, v, p, col], k) => (
              <div key={k} style={{ marginTop: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 24, color: "#dbe5f3" }}>
                  <span>{label as string}</span>
                  <b style={{ fontSize: 34, color: C.white, opacity: p as number }}>{(v as number).toFixed(2)}×</b>
                </div>
                <div style={{ position: "relative", height: 16, marginTop: 6, borderRadius: 8, background: C.navy3 }}>
                  <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, borderRadius: 8, background: col as string,
                    width: `${(100 * (v as number) / MAXX) * (p as number)}%` }} />
                  {k === 0 && <div style={{ position: "absolute", top: -6, height: 28, left: `${100 * r.chip_ci90[0] / MAXX}%`,
                    width: `${100 * (r.chip_ci90[1] - r.chip_ci90[0]) / MAXX}%`, borderLeft: "2px solid #fff",
                    borderRight: "2px solid #fff", opacity: 0.8 * (p as number), boxSizing: "border-box" }} />}
                </div>
              </div>
            ))}
          <div style={{ fontSize: 18, color: C.muted, marginTop: 14 }}>
            Chip: {fmt(cases.high.shots_all)} shots per case, noise-corrected · 90 % interval {r.chip_ci90[0].toFixed(1)}–{r.chip_ci90[1].toFixed(1)}×
          </div>
        </div>
      </div>
    </div>
  );
};
