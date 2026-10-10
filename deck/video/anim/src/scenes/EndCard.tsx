import React from "react";
import timing from "../timing.json";
import { BEAT, C, mix, ramp, word } from "../theme";

// Beat 5: "Tulva. The snow warns two months early." The words appear with the voice (no caption on this card).
const TAG = timing.words.filter((w) => w.beat === BEAT.end - 1).slice(1);
const FLAKES = Array.from({ length: 70 }, (_, i) => {
  const r = (k: number) => ((Math.sin(i * 17.123 + k * 61.77) * 43758.5453) % 1 + 1) % 1;
  return { x: r(1) * 1920, y: r(2) * 1080, s: 1.5 + r(3) * 3, v: 14 + r(4) * 30, ph: r(5) * 6.28 };
});

export const EndCard: React.FC<{ t: number }> = ({ t }) => {
  const tName = word(BEAT.end, "tulva");
  const logo = ramp(t, tName - 0.35, tName + 0.25, "out");
  return (
    <div style={{ position: "absolute", inset: 0, background: `radial-gradient(1200px 700px at 50% 45%, ${C.navy3}, ${C.navy})` }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {FLAKES.map((f, i) => (
          <circle key={i} cx={f.x + Math.sin(t + f.ph) * 10} cy={(f.y + t * f.v) % 1100} r={f.s} fill="#fff" opacity={0.28} />
        ))}
      </svg>
      <div style={{ position: "absolute", top: 330, left: 0, right: 0, display: "flex", justifyContent: "center",
        alignItems: "center", gap: 34, opacity: logo, transform: `scale(${mix(0.92, 1, logo)})` }}>
        <div style={{ width: 104, height: 104, borderRadius: "50% 50% 50% 22px", transform: "rotate(-45deg)",
          background: `linear-gradient(135deg, #3fa9f5, ${C.blue})`, boxShadow: "0 12px 40px rgba(31,111,235,.45)" }} />
        <div style={{ fontSize: 168, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1 }}>Tulva</div>
      </div>
      <div style={{ position: "absolute", top: 590, left: 0, right: 0, textAlign: "center", fontSize: 66, fontWeight: 600,
        letterSpacing: "-0.01em" }}>
        {TAG.map((w, i) => {
          const p = ramp(t, w.start - 0.08, w.start + 0.3, "out");
          return (
            <span key={i} style={{ display: "inline-block", marginRight: 18, opacity: p, transform: `translateY(${mix(14, 0, p)}px)`,
              color: w.w.startsWith("snow") ? C.pale : C.white }}>{w.w}</span>
          );
        })}
      </div>
    </div>
  );
};
