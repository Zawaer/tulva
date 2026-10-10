import React from "react";
import { AbsoluteFill, Audio, useCurrentFrame } from "remotion";
import narration from "../narration.mp3";
import { Captions } from "./Captions";
import { AppScene } from "./scenes/AppScene";
import { ChipScene } from "./scenes/ChipScene";
import { ComputersScene } from "./scenes/ComputersScene";
import { EndCard } from "./scenes/EndCard";
import { BEAT, beat, C, FONT, FPS, mix, ramp } from "./theme";

const SCENES: [number, React.FC<{ t: number }>][] = [
  [BEAT.app, AppScene], [BEAT.chip, ChipScene], [BEAT.computers, ComputersScene], [BEAT.end, EndCard],
];
// Scene changes dip through the navy background: the old scene fades out over [b - X, b + 0.05], the new one fades
// in over [b - 0.05, b + X] (b = the beat boundary, in the pause between sentences).
const X = 0.26;

export const Demo: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  return (
    <AbsoluteFill style={{ background: C.navy, fontFamily: FONT, color: C.white }}>
      <Audio src={narration} />
      {SCENES.map(([n, Scene]) => {
        const b = beat(n);
        if (t < b.start - 0.05 || t > b.end + 0.05) return null;
        const last = n === SCENES[SCENES.length - 1][0];
        const p = (n === SCENES[0][0] ? ramp(t, 0, 0.35) : ramp(t, b.start - 0.05, b.start + X)) *
          (last ? 1 : 1 - ramp(t, b.end - X, b.end + 0.05));
        return (
          <AbsoluteFill key={n} style={{ opacity: p, transform: `scale(${mix(1.015, 1, p)})` }}>
            <Scene t={t} />
          </AbsoluteFill>
        );
      })}
      <Captions t={t} />
    </AbsoluteFill>
  );
};
