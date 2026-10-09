import React from "react";
import { beat, CAPTION_TOP, C, H, ramp } from "./theme";
import timing from "./timing.json";

// Burned-in captions = the narration.md caption lines, timed to the voice. The end card (beat 5) shows its words
// on screen instead.
const CHUNKS = timing.chunks.filter((c) => c.beat < 4);
const HOLD = 0.9; // s a caption may stay after its last word, unless the next one starts or its scene ends
const until = (k: number) => {
  const c = CHUNKS[k], next = CHUNKS[k + 1];
  return Math.min(c.end + HOLD, next && next.beat === c.beat ? next.start - 0.06 : beat(c.beat + 1).end - 0.2);
};

export const Captions: React.FC<{ t: number }> = ({ t }) => {
  const i = CHUNKS.findIndex((c, k) => t >= c.start - 0.1 && t < until(k));
  if (i < 0) return null;
  const c = CHUNKS[i];
  const end = until(i);
  const prevJoined = i > 0 && until(i - 1) >= c.start - 0.1;
  const nextJoined = i + 1 < CHUNKS.length && end >= CHUNKS[i + 1].start - 0.1; // swap without a blink
  const op = (prevJoined ? 1 : ramp(t, c.start - 0.1, c.start + 0.05, "linear")) *
    (nextJoined ? 1 : 1 - ramp(t, end - 0.12, end, "linear"));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: CAPTION_TOP, height: H - CAPTION_TOP, display: "flex",
      alignItems: "center", justifyContent: "center", padding: "0 110px", boxSizing: "border-box" }}>
      <div style={{ opacity: op, fontSize: 46, fontWeight: 600, lineHeight: 1.22, textAlign: "center", color: C.white,
        letterSpacing: "-0.005em", textShadow: "0 2px 10px rgba(0,0,0,.35)" }}>
        {c.show}
      </div>
    </div>
  );
};
