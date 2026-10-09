import React from "react";
import data from "../data.json";
import { C, clamp01, mix, ramp, word } from "../theme";

// Beat 1: May 2005, four Lapland rivers over their 1-in-10 level together; two months earlier the March snow was in
// its top 15 %. Map = Natural Earth, dots = the 14 SYKE gauges, values from web/data/app.json.
const LIT = data.areas.filter((a) => a.over_1in10);
const LABEL_SIDE: Record<string, 1 | -1> = { Ivalo: 1, Kittilä: -1, Rovaniemi: 1, Tornio: -1 };
const FI = data.land.find((l) => l.name === "Finland")!.d;
const AX = data.land.find((l) => l.name === "Aland")!.d;

// deterministic snow flakes inside Finland's bounding box (clipped to the outline)
const FLAKES = Array.from({ length: 160 }, (_, i) => {
  const r = (k: number) => ((Math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1 + 1) % 1;
  return { x: 1120 + r(1) * 520, y: r(2) * 900, s: 1.6 + r(3) * 2.6, v: 18 + r(4) * 26, ph: r(5) * 6.28 };
});

export const MapScene: React.FC<{ t: number }> = ({ t }) => {
  const tMay = word(1, "may"), tEarlier = word(1, "two", 1), tTop = word(1, "top");
  const tRivers = [word(1, "four"), word(1, "lapland"), word(1, "rivers"), word(1, "hit")];
  const tTogether = word(1, "together");
  const snow = 0.8 * ramp(t, tEarlier, tEarlier + 1.2);      // the March snow, shown under the flooded rivers
  const meter = ramp(t, tEarlier + 0.4, tTop + 0.2);
  const pct = data.snow_north_pct * meter;
  const lit = LIT.map((_, k) => ramp(t, tRivers[k], tRivers[k] + 0.35, "out"));
  const count = lit.filter((p) => p > 0.5).length;
  const floodBlock = ramp(t, tRivers[0] - 0.4, tRivers[0] + 0.1);
  const lines = ramp(t, tTogether - 0.05, tTogether + 0.6);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <clipPath id="fi"><path d={FI} /></clipPath>
          <linearGradient id="snowg" x1="0" y1="66" x2="0" y2="910" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#fff" stopOpacity="0.95" />
            <stop offset="0.45" stopColor="#eaf3ff" stopOpacity="0.85" />
            <stop offset="1" stopColor="#d6e6fb" stopOpacity="0.25" />
          </linearGradient>
          <linearGradient id="fadeL" x1="740" y1="0" x2="1130" y2="0" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor={C.navy} stopOpacity="1" /><stop offset="1" stopColor={C.navy} stopOpacity="0" />
          </linearGradient>
          <radialGradient id="glow"><stop offset="0" stopColor={C.red} stopOpacity="0.75" /><stop offset="1" stopColor={C.red} stopOpacity="0" /></radialGradient>
        </defs>
        {data.land.filter((l) => !l.home).map((l) => <path key={l.name} d={l.d} fill={C.navy2} stroke="#24436e" strokeWidth={1.2} />)}
        {/* fade the neighbours out behind the text column */}
        <rect x={0} y={0} width={740} height={1080} fill={C.navy} />
        <rect x={740} y={0} width={390} height={1080} fill="url(#fadeL)" />
        <path d={FI} fill={C.navy3} stroke={C.pale} strokeOpacity={0.55} strokeWidth={1.6} />
        <path d={AX} fill={C.navy3} stroke={C.pale} strokeOpacity={0.4} strokeWidth={1} />
        <g clipPath="url(#fi)" opacity={snow}>
          <rect x={1000} y={0} width={800} height={1000} fill="url(#snowg)" />
          {FLAKES.map((f, i) => {
            const y = (f.y + t * f.v) % 920;
            return <circle key={i} cx={f.x + Math.sin(t * 0.8 + f.ph) * 6} cy={y} r={f.s} fill="#fff" opacity={0.85} />;
          })}
        </g>
        {data.edges.map((e, i) => {
          const a = data.areas.find((x) => x.area === e.a)!, b = data.areas.find((x) => x.area === e.b)!;
          const len = Math.hypot(b.x - a.x, b.y - a.y);
          return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={C.red} strokeOpacity={0.8} strokeWidth={4}
            strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - lines)} />;
        })}
        {data.areas.map((a, i) => {
          const k = LIT.findIndex((x) => x.area === a.area);
          const p = k >= 0 ? lit[k] : 0;
          const appear = ramp(t, 0.5 + i * 0.04, 0.9 + i * 0.04, "out");
          const tk = k >= 0 ? tRivers[k] : 0;
          const ring = k >= 0 ? clamp01((t - tk) / 1.1) : 0;
          return (
            <g key={a.area} opacity={appear}>
              {p > 0 && <circle cx={a.x} cy={a.y} r={46 * p} fill="url(#glow)" />}
              {ring > 0 && ring < 1 && <circle cx={a.x} cy={a.y} r={12 + 46 * ring} fill="none" stroke={C.red}
                strokeWidth={4 * (1 - ring)} opacity={1 - ring} />}
              <circle cx={a.x} cy={a.y} r={mix(8, 13, p)} fill={p > 0 ? C.red : C.navy2} fillOpacity={p > 0 ? 0.35 + 0.65 * p : 1}
                stroke={p > 0 ? "#fff" : "#a7b8d0"} strokeWidth={p > 0 ? 3 : 2.5} />
            </g>
          );
        })}
      </svg>
      {LIT.map((a, k) => {
        const p = lit[k], side = LABEL_SIDE[a.area] ?? 1;
        return (
          <div key={a.area} style={{ position: "absolute", top: a.y - 31, left: side > 0 ? a.x + 22 : undefined,
            right: side < 0 ? 1920 - a.x + 22 : undefined, opacity: p, transform: `translateX(${(1 - p) * 14 * side}px)`,
            textAlign: side > 0 ? "left" : "right", whiteSpace: "nowrap", background: "rgba(11,31,58,.88)",
            padding: "4px 12px 6px", borderRadius: 10, boxShadow: "0 4px 14px rgba(0,0,0,.3)" }}>
            <div style={{ fontSize: 30, fontWeight: 700, lineHeight: 1.05 }}>{a.area}</div>
            <div style={{ fontSize: 22, color: "#ffb4ab", fontWeight: 600 }}>{a.pct_of_1in10} % of 1-in-10</div>
          </div>
        );
      })}

      <div style={{ position: "absolute", left: 140, top: 128, width: 840 }}>
        <div style={{ fontSize: 22, letterSpacing: "0.16em", color: C.pale, fontWeight: 600, opacity: ramp(t, 0.2, 0.8) }}>
          FINLAND · 14 RIVER FLOOD-RISK AREAS
        </div>
        <div style={{ height: 130, marginTop: 14, fontSize: 104, fontWeight: 800, letterSpacing: "-0.02em",
          opacity: ramp(t, tMay - 0.1, tMay + 0.4), transform: `translateY(${(1 - ramp(t, tMay - 0.1, tMay + 0.4)) * 20}px)` }}>
          May 2005
        </div>

        <div style={{ marginTop: 30, opacity: floodBlock, transform: `translateY(${(1 - floodBlock) * 20}px)` }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
            <span style={{ fontSize: 120, fontWeight: 800, color: "#ff5a4d", lineHeight: 1 }}>{count}</span>
            <span style={{ fontSize: 46, fontWeight: 700 }}>of 14 areas</span>
          </div>
          <div style={{ fontSize: 28, color: "#dbe5f3", marginTop: 6 }}>over their 1-in-10 flood level, together</div>
        </div>

        <div style={{ marginTop: 50, opacity: ramp(t, tEarlier - 0.2, tEarlier + 0.3) }}>
          <div style={{ fontSize: 30, fontWeight: 600 }}>Two months earlier: Lapland's snow on 1 March</div>
          <div style={{ position: "relative", width: 640, height: 20, marginTop: 58, borderRadius: 10, background: C.navy3 }}>
            <div style={{ position: "absolute", left: "85%", width: "15%", top: -8, bottom: -8, borderRadius: 8,
              border: `2px dashed ${C.pale}`, opacity: 0.8 }} />
            <div style={{ position: "absolute", left: "85%", width: "15%", top: -44, textAlign: "center", fontSize: 21,
              color: C.pale, fontWeight: 700, whiteSpace: "nowrap" }}>top 15 %</div>
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${pct}%`, borderRadius: 10,
              background: "linear-gradient(90deg, #6f9fd8, #ffffff)" }} />
            <div style={{ position: "absolute", left: `${pct}%`, top: 10, width: 30, height: 30, marginLeft: -15, marginTop: -15,
              borderRadius: 15, background: "#fff", boxShadow: "0 0 0 6px rgba(169,200,245,.35)", opacity: meter > 0 ? 1 : 0 }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", width: 640, marginTop: 14, fontSize: 19, color: C.muted }}>
            <span>least snow</span><span>most snow (1961–2025)</span>
          </div>
          <div style={{ fontSize: 34, fontWeight: 700, marginTop: 12, opacity: ramp(t, tTop, tTop + 0.4) }}>
            {Math.round(pct)}th percentile <span style={{ color: C.pale }}>· top 15 %</span>
          </div>
        </div>

      </div>
      <div style={{ position: "absolute", left: 140, top: 878, fontSize: 18, color: C.muted, opacity: ramp(t, 1, 2) }}>
        SYKE river and snow data · peak spring flow vs each gauge's 1-in-10 level · back-test, not a forecast made in 2005
      </div>
    </div>
  );
};
