import React from "react";
import data from "../data.json";
import { C, ramp, word } from "../theme";

// Beat 3: IQM Emerald vs exact, the same bars as slide 6 (out/bootstrap_ci.json via export_data.py): chance that both
// rivers of the two-river North pair pass their 1-in-50 level in one spring, low-snow vs snowy March; chip bars are the
// calibrated estimates from 240,000 shots per case with their 90 % intervals. Then the ratio, 3.05× chip vs 2.75× exact.
const cases = data.shots.cases;
const r = data.ratio;
const BLUE = C.blue, PURPLE = C.purple;
const BLUE_T = "#8fb8ff", PURPLE_T = "#bfa6ff";          // text tints that read on navy
const CH = { x: 140, base: 800, top: 350, bar: 150, gap: 18 };
const VMAX = 0.28;                                         // % at the top of the chart
const h = (pct: number) => ((CH.base - CH.top) * pct) / VMAX;
const GROUPS = [{ key: "low" as const, label: "Low-snow March", cx: 400 }, { key: "high" as const, label: "Snowy March", cx: 860 }];
const pc = (v: number) => `${(100 * v).toFixed(3)} %`;

export const ChipScene: React.FC<{ t: number }> = ({ t }) => {
  const tNow = word(3, "now"), tBlue = word(3, "blue"), tPurple = word(3, "purple");
  const tSnowy = word(3, "snowy"), tThree = word(3, "three"), tTwo = word(3, "two");
  const head = ramp(t, tNow - 0.6, tNow - 0.1);
  const grow = (t0: number, k: number) => ramp(t, t0 + 0.12 * k, t0 + 0.12 * k + 0.6, "out");
  const ci = ramp(t, tPurple + 0.7, tPurple + 1.1);
  const panel = ramp(t, tSnowy - 0.2, tSnowy + 0.3);
  const chip = ramp(t, tThree - 0.15, tThree + 0.55, "out");
  const exact = ramp(t, tTwo - 0.15, tTwo + 0.45, "out");
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: CH.x, top: 70, opacity: head }}>
        <div style={{ fontSize: 22, letterSpacing: "0.16em", color: C.pale, fontWeight: 600 }}>REAL QUANTUM HARDWARE · IQM EMERALD</div>
        <div style={{ fontSize: 54, fontWeight: 800, marginTop: 8, letterSpacing: "-0.01em" }}>Chance both rivers flood in one spring</div>
        <div style={{ fontSize: 26, color: "#dbe5f3", marginTop: 4 }}>two northern rivers, both over their 1-in-50 level</div>
        <div style={{ display: "flex", gap: 40, marginTop: 26, fontSize: 28, fontWeight: 600 }}>
          {[["Exact", BLUE, ramp(t, tBlue - 0.1, tBlue + 0.2)], ["IQM chip", PURPLE, ramp(t, tPurple - 0.1, tPurple + 0.2)]].map(
            ([lab, col, op]) => (
              <div key={lab as string} style={{ display: "flex", alignItems: "center", gap: 12, opacity: 0.35 + 0.65 * (op as number) }}>
                <div style={{ width: 26, height: 26, borderRadius: 5, background: col as string }} />{lab as string}
              </div>
            ))}
        </div>
      </div>

      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={CH.x} x2={1090} y1={CH.base} y2={CH.base} stroke="#3a5680" strokeWidth={2} opacity={head} />
        {GROUPS.map((g, gi) => {
          const c = cases[g.key];
          const bars = [
            { v: c.exact, p: grow(tBlue, gi), col: BLUE, tint: BLUE_T, x: g.cx - CH.bar - CH.gap / 2 },
            { v: c.estimate, p: grow(tPurple, gi), col: PURPLE, tint: PURPLE_T, x: g.cx + CH.gap / 2 },
          ];
          return (
            <g key={g.key}>
              {bars.map((b, k) => {
                const bh = h(100 * b.v) * b.p;
                return (
                  <g key={k}>
                    <rect x={b.x} y={CH.base - bh} width={CH.bar} height={bh} rx={6} fill={b.col} />
                    <text x={b.x + CH.bar / 2} y={CH.base - bh - (k === 1 ? 44 : 16)} textAnchor="middle" fontSize={32}
                      fontWeight={700} fill={b.tint} opacity={b.p}>{pc(b.v)}</text>
                  </g>
                );
              })}
              {/* 90 % interval of the chip estimate */}
              <g stroke="#fff" strokeWidth={2.5} opacity={0.85 * ci}>
                <line x1={bars[1].x + CH.bar / 2} x2={bars[1].x + CH.bar / 2} y1={CH.base - h(100 * c.ci90[0])} y2={CH.base - h(100 * c.ci90[1])} />
                <line x1={bars[1].x + CH.bar / 2 - 14} x2={bars[1].x + CH.bar / 2 + 14} y1={CH.base - h(100 * c.ci90[1])} y2={CH.base - h(100 * c.ci90[1])} />
                <line x1={bars[1].x + CH.bar / 2 - 14} x2={bars[1].x + CH.bar / 2 + 14} y1={CH.base - h(100 * c.ci90[0])} y2={CH.base - h(100 * c.ci90[0])} />
              </g>
              <text x={g.cx} y={CH.base + 46} textAnchor="middle" fontSize={30} fontWeight={600} fill="#fff" opacity={head}>{g.label}</text>
            </g>
          );
        })}
      </svg>

      <div style={{ position: "absolute", left: 1220, top: 350, width: 600, opacity: panel,
        transform: `translateY(${(1 - panel) * 20}px)` }}>
        <div style={{ fontSize: 30, color: "#dbe5f3", fontWeight: 600 }}>Snowy vs low-snow March</div>
        {[["on chip", r.chip, chip, PURPLE_T], ["exact", r.exact, exact, BLUE_T]].map(([lab, v, p, col], k) => (
          <div key={k} style={{ display: "flex", alignItems: "baseline", gap: 20, marginTop: k ? 6 : 18, opacity: p as number,
            transform: `translateY(${(1 - (p as number)) * 16}px)` }}>
            <span style={{ fontSize: 120, fontWeight: 800, color: col as string, letterSpacing: "-0.02em",
              fontVariantNumeric: "tabular-nums" }}>{(v as number).toFixed(2)}×</span>
            <span style={{ fontSize: 34, fontWeight: 600 }}>{lab as string}</span>
          </div>
        ))}
        <div style={{ height: 2, background: "#2a4a78", marginTop: 22, opacity: exact }} />
        <div style={{ fontSize: 21, color: C.muted, marginTop: 14, lineHeight: 1.35, opacity: exact }}>
          Chip: noise-corrected, 240,000 shots per case<br />white lines = 90 % interval · ratio {r.chip_ci90[0].toFixed(1)}–{r.chip_ci90[1].toFixed(1)}×
        </div>
      </div>
    </div>
  );
};
