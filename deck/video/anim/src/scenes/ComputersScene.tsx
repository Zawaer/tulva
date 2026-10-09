import React from "react";
import data from "../data.json";
import { C, mix, ramp, word } from "../theme";

// Beat 4: the four quantum computers the two-river core ran on (CLAIMS.md "VTT Q50": Q50 counts as run, not as a
// successful estimate). Each card lands on its maker's name in the voice.
const Chip: React.FC<{ color: string }> = ({ color }) => (
  <svg width={92} height={92} viewBox="0 0 92 92">
    {[0, 1, 2, 3].map((k) => (
      <g key={k} stroke={C.pale} strokeWidth={3} strokeLinecap="round" opacity={0.7}>
        <line x1={26 + k * 13} y1={4} x2={26 + k * 13} y2={16} /><line x1={26 + k * 13} y1={76} x2={26 + k * 13} y2={88} />
        <line x1={4} y1={26 + k * 13} x2={16} y2={26 + k * 13} /><line x1={76} y1={26 + k * 13} x2={88} y2={26 + k * 13} />
      </g>
    ))}
    <rect x={16} y={16} width={60} height={60} rx={10} fill={C.navy3} stroke={color} strokeWidth={3} />
    {[0, 1, 2].map((r) => [0, 1, 2].map((c) => <circle key={`${r}${c}`} cx={32 + c * 14} cy={32 + r * 14} r={4} fill={color} />))}
  </svg>
);

export const ComputersScene: React.FC<{ t: number }> = ({ t }) => {
  const cues = [word(4, "ibm"), word(4, "iqm"), word(4, "iqm") + 0.3, word(4, "vtt")];
  const colors = [C.pale, "#7fd6c9", "#7fd6c9", "#ff8a80"];
  const head = ramp(t, cues[0] - 1.25, cues[0] - 0.75);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", top: 170, left: 0, right: 0, textAlign: "center", opacity: head }}>
        <div style={{ fontSize: 22, letterSpacing: "0.16em", color: C.pale, fontWeight: 600 }}>SAME TWO-RIVER CIRCUIT</div>
        <div style={{ fontSize: 60, fontWeight: 800, marginTop: 10, letterSpacing: "-0.01em" }}>Four quantum computers</div>
      </div>
      <div style={{ position: "absolute", top: 410, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 36 }}>
        {data.computers.map((c, k) => {
          const p = ramp(t, cues[k] - 0.1, cues[k] + 0.45, "out");
          return (
            <div key={k} style={{ width: 330, height: 330, borderRadius: 22, background: C.navy2, opacity: p,
              transform: `translateY(${mix(40, 0, p)}px) scale(${mix(0.94, 1, p)})`,
              border: `2px solid ${k === 3 ? "#ff8a80" : "#2a4a78"}`, boxShadow: "0 20px 50px rgba(0,0,0,.35)",
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14 }}>
              <Chip color={colors[k]} />
              <div style={{ fontSize: 54, fontWeight: 800, letterSpacing: "0.01em" }}>{c.maker}</div>
              <div style={{ fontSize: 32, color: "#dbe5f3", fontWeight: 500 }}>{c.name}</div>
              <div style={{ fontSize: 22, color: "#ff8a80", fontWeight: 700, height: 26 }}>{c.note ?? ""}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 820, left: 0, right: 0, textAlign: "center", fontSize: 26, color: C.muted,
        opacity: ramp(t, cues[3] + 0.3, cues[3] + 0.9) }}>
        Checked against exact classical values · classical computers still win today · no quantum advantage claimed
      </div>
    </div>
  );
};
