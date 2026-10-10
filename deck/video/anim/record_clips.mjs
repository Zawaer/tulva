// Records the real Tulva web app for the video's app scene (beat 2), frame by frame, so it is sharp and lands on
// the voiceover's words (times from src/timing.json):
//   python3 -m http.server 3141 --directory web          # in the repo root
//   node deck/video/anim/record_clips.mjs [url]
// Opens the app at the top with "No outlook", scrolls to the March snow outlook, moves a cursor to "High snow" and
// clicks it on the word "high". The app's own bar transitions are stepped frame by frame through the DevTools
// Animation domain. Output: public/app_snow.mp4 (3200x1800, 30 fps) and src/clips.json (clip start, element boxes
// for the zoom). Uses the installed Google Chrome.
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";

const HERE = new URL("./", import.meta.url).pathname;
const APP_URL = process.argv[2] || "http://127.0.0.1:3141";
const FPS = 30, VW = 1280, VH = 720, DSF = 2.5;
const T = JSON.parse(readFileSync(HERE + "src/timing.json", "utf8"));
const beat = T.beats.find((b) => b.title.startsWith("App"));   // the narration.md beat this clip plays under
const word = (w) => T.words.find((x) => x.beat === beat.n - 1 && x.w.toLowerCase().startsWith(w)).start;
const PRE = Math.min(0.5, beat.start), POST = 0.5;  // extra footage for the cross-fades (none before 0 s)
const t0 = beat.start - PRE, t1 = beat.end + POST;  // absolute video times covered by the clip
const cue = {
  scroll: [word("snow") - 0.1, word("price") + 0.35],   // "Our app turns that snow into a price."
  cursorIn: word("set") - 0.15,
  move: [word("set") + 0.05, word("high") - 0.2],
  click: word("high") - 0.05,                            // "Set March snow to HIGH,"
  cursorOut: word("high") + 0.75,
};
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2);
const prog = (t, [a, b]) => ease((t - a) / (b - a));

const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage({ viewport: { width: VW, height: VH }, deviceScaleFactor: DSF });
await page.goto(APP_URL, { waitUntil: "networkidle" });
await page.addStyleTag({ content: `
  html { scroll-behavior: auto !important; scrollbar-width: none; } ::-webkit-scrollbar { display: none; }
  #vcur { position: fixed; left: 0; top: 0; z-index: 99999; pointer-events: none; opacity: 0; will-change: transform; }
  #vcur .ring { position: absolute; left: -22px; top: -22px; width: 44px; height: 44px; border-radius: 50%;
    border: 3px solid #d13b2f; opacity: 0; }` });
await page.evaluate(() => {
  const c = document.createElement("div"); c.id = "vcur";
  c.innerHTML = `<div class="ring"></div><svg width="30" height="38" viewBox="0 0 30 38" style="position:absolute;left:-3px;top:-2px">
    <path d="M3 2 L3 30 L10.5 23.5 L15.5 35 L20.5 32.8 L15.6 21.6 L25.5 21.2 Z" fill="#fff" stroke="#0b1f3a" stroke-width="2.4"
      stroke-linejoin="round"/></svg>`;
  document.body.appendChild(c);
  [...document.querySelectorAll("#presets button")].find((b) => b.textContent.includes("No outlook")).click();
  window.scrollTo(0, 0);
});
await page.waitForTimeout(600);

// Target scroll: the snow presets just under the sticky header; then the boxes Remotion zooms into.
const geo = await page.evaluate(() => {
  const head = document.querySelector("header").getBoundingClientRect().bottom;
  const presets = document.querySelector("#presets");
  const y = presets.getBoundingClientRect().top + window.scrollY - head - 28;
  window.scrollTo(0, y);
  const r = (el) => { const b = el.getBoundingClientRect(); return { x: b.left, y: b.top, w: b.width, h: b.height }; };
  const high = [...presets.querySelectorAll("button")].find((b) => b.textContent.includes("High snow"));
  const out = { scrollY: window.scrollY, high: r(high), north: r(document.querySelector("#tiles > *")) };
  window.scrollTo(0, 0);
  return out;
});
console.log("geometry", geo);

const cdp = await page.context().newCDPSession(page);
await cdp.send("Animation.enable");
const anims = [];                                   // [{id, start (video s)}] of the app's own transitions
let tNow = t0;
cdp.on("Animation.animationStarted", (e) => anims.push({ id: e.animation.id, start: tNow, fresh: true }));

const dir = HERE + "build/frames_app_snow/";
rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true });
const n = Math.round((t1 - t0) * FPS);
const start = { x: VW * 0.58, y: VH * 0.84 };
let clicked = false;
for (let i = 0; i < n; i++) {
  const t = t0 + i / FPS; tNow = t;
  if (!clicked && t >= cue.click) {
    clicked = true;
    await page.evaluate(() => [...document.querySelectorAll("#presets button")].find((b) => b.textContent.includes("High snow")).click());
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  }
  const fresh = anims.filter((a) => a.fresh);
  if (fresh.length) { await cdp.send("Animation.setPaused", { animations: fresh.map((a) => a.id), paused: true }); fresh.forEach((a) => (a.fresh = false)); }
  for (const a of anims) await cdp.send("Animation.seekAnimations", { animations: [a.id], currentTime: Math.max(0, (t - a.start) * 1000) });
  const target = { x: geo.high.x + geo.high.w * 0.5, y: geo.high.y + geo.high.h * 0.86 };  // tip below the label
  const m = prog(t, cue.move);
  const cur = { x: start.x + (target.x - start.x) * m, y: start.y + (target.y - start.y) * m };
  const press = t >= cue.click && t < cue.click + 0.12;
  const ringP = Math.min(1, Math.max(0, (t - cue.click) / 0.5));
  await page.evaluate(([y, cx, cy, op, press, ringP]) => {
    window.scrollTo(0, y);
    const c = document.getElementById("vcur");
    c.style.opacity = op; c.style.transform = `translate(${cx}px, ${cy}px) scale(${press ? 0.88 : 1})`;
    const ring = c.querySelector(".ring");
    ring.style.opacity = ringP > 0 && ringP < 1 ? 1 - ringP : 0; ring.style.transform = `scale(${0.4 + 1.2 * ringP})`;
  }, [geo.scrollY * prog(t, cue.scroll), cur.x, cur.y,
      Math.min(prog(t, [cue.cursorIn, cue.cursorIn + 0.25]), 1 - prog(t, [cue.cursorOut, cue.cursorOut + 0.3])), press, ringP]);
  await page.screenshot({ path: `${dir}${String(i).padStart(5, "0")}.jpg`, type: "jpeg", quality: 95 });
  if (i % 60 === 0) process.stdout.write(`frame ${i}/${n}\r`);
}
await browser.close();

mkdirSync(HERE + "public", { recursive: true });
execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", dir + "%05d.jpg", "-c:v", "libx264",
  "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", HERE + "public/app_snow.mp4"]);
writeFileSync(HERE + "src/clips.json", JSON.stringify({
  app_snow: { file: "app_snow.mp4", start: +t0.toFixed(3), end: +t1.toFixed(3), fps: FPS, viewport: [VW, VH], dsf: DSF,
    cues: Object.fromEntries(Object.entries(cue).map(([k, v]) => [k, Array.isArray(v) ? v.map((x) => +x.toFixed(3)) : +v.toFixed(3)])),
    // boxes in CSS px of the viewport after the scroll (multiply by dsf for clip pixels)
    high_button: geo.high, north_tile: geo.north },
}, null, 1));
console.log(`\npublic/app_snow.mp4: ${n} frames, ${(n / FPS).toFixed(2)} s (video ${t0.toFixed(2)}–${t1.toFixed(2)} s)`);
