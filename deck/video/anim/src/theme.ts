import { Easing } from "remotion";
import timing from "./timing.json";

export const FPS = 30;
export const W = 1920;
export const H = 1080;
export const CAPTION_TOP = 932; // everything above is scene content, below is the caption band

// Deck colours (deck/build_deck.py) + the app's outcome colours (web/pipeline.js).
export const C = {
  navy: "#0B1F3A", navy2: "#11284A", navy3: "#1B3A64", blue: "#1F6FEB", red: "#D13B2F", grey: "#6B7280",
  light: "#F3F6FA", line: "#DDE3EA", pale: "#A9C8F5", white: "#FFFFFF", muted: "#93A5C0",
  riverA: "#0f9e94", riverB: "#2f6fde", both: "#d0342c", none: "#e8edf3", ink: "#1c2b40",
  purple: "#8250DF", // IQM chip, as on slide 6
};
export const FONT = '"Inter", system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif';

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const inOut = Easing.bezier(0.45, 0, 0.2, 1);
const out = Easing.bezier(0.2, 0.7, 0.2, 1);
/** 0 → 1 between times a and b (seconds), eased. */
export const ramp = (t: number, a: number, b: number, kind: "inOut" | "out" | "linear" = "inOut") => {
  const x = clamp01((t - a) / (b - a));
  return kind === "linear" ? x : kind === "out" ? out(x) : inOut(x);
};
export const mix = (a: number, b: number, p: number) => a + (b - a) * p;

export type Beat = (typeof timing.beats)[number];
export const beat = (n: number): Beat => timing.beats.find((b) => b.n === n)!;
const beatNo = (title: string) => timing.beats.find((b) => b.title.startsWith(title))!.n;
/** Beat numbers by narration.md heading, so scenes survive beats being added or removed. */
export const BEAT = { app: beatNo("App"), chip: beatNo("Chip"), computers: beatNo("Computers"), end: beatNo("End card") };
/** Start time of the k-th word in beat n that begins with `w` (case-insensitive). */
export const word = (n: number, w: string, k = 0): number => {
  const hits = timing.words.filter((x) => x.beat === n - 1 && x.w.toLowerCase().startsWith(w.toLowerCase()));
  if (!hits[k]) throw new Error(`word "${w}" not found in beat ${n}`);
  return hits[k].start;
};
export const fmt = (n: number) => Math.round(n).toLocaleString("en");
