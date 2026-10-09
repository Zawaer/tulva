// Records a ~40 s scripted walkthrough of the Tulva demo app (1920x1080, page zoom 1.5, short captions burned in).
// The presenter narrates live over it (deck/PITCH.md, slide 4).
//   source /data/chats/s_7z3ZoxoroN/env.sh; node deck/video/record_demo.mjs [url]
// Prints the second at which the first caption appears; trim the lead-in with ffmpeg -ss.
import { createRequire } from "node:module";
const require = createRequire(process.env.PLAYWRIGHT_PKG || (process.cwd() + "/package.json"))  // any project with playwright installed;
const { chromium } = require("playwright");
const APP_URL = process.argv[2] || "http://127.0.0.1:3141";
const OUT = new URL("./", import.meta.url).pathname;

const browser = await chromium.launch({ args: ["--no-sandbox"] });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1,
  recordVideo: { dir: OUT + "raw", size: { width: 1920, height: 1080 } } });
const t0 = Date.now();
const page = await ctx.newPage();
await page.goto(APP_URL, { waitUntil: "networkidle" });
await page.waitForTimeout(1200);
await page.evaluate(() => { document.documentElement.style.zoom = "1.5"; });   // readable on a projector
await page.addStyleTag({ content: `
  #demo-cap{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:99999;max-width:1200px;
    background:rgba(11,31,58,.94);color:#fff;font:700 22px/1.3 Arial,sans-serif;padding:10px 26px;border-radius:12px;
    box-shadow:0 8px 30px rgba(0,0,0,.25);text-align:center;white-space:nowrap}
  .demo-hl td{background:#fff3b0 !important;font-weight:700}
` });
await page.evaluate(() => { const d = document.createElement("div"); d.id = "demo-cap"; document.body.appendChild(d); });
await page.waitForTimeout(800);
const cap = (t) => page.evaluate((t) => { document.getElementById("demo-cap").textContent = t; }, t);
// With CSS zoom, element rects and scroll offsets use different scales, so find each target scroll position by
// trial (instant jumps during the lead-in, which is trimmed off), then scroll there smoothly during the take.
const findY = (fn, margin) => page.evaluate(([fn, m]) => {
  const el = new Function("return " + fn)(); if (!el) return null;
  const bar = document.querySelector("header.top"); const want = (bar ? bar.getBoundingClientRect().bottom : 0) + m;
  let y = 0;
  for (let i = 0; i < 8; i++) {
    window.scrollTo({ top: y, behavior: "instant" });
    const d = el.getBoundingClientRect().top - want; if (Math.abs(d) < 2) break;
    const before = window.scrollY; window.scrollTo({ top: y + d, behavior: "instant" });
    const d2 = el.getBoundingClientRect().top - want; const moved = window.scrollY - before;
    y = window.scrollY + (moved && d !== d2 ? d2 * moved / (d - d2) : d2);
  }
  window.scrollTo({ top: y, behavior: "instant" }); return window.scrollY;
}, [fn, margin]);
const glide = (y) => page.evaluate((y) => window.scrollTo({ top: y, behavior: "smooth" }), y);
// DOM clicks (a Playwright click would scroll the element into view and cut the smooth scroll short)
const clickText = (scope, text) => page.evaluate(([sc, t]) => {
  const b = [...document.querySelectorAll(`${sc} button`)].find((x) => x.textContent.includes(t)); if (b) b.click();
}, [scope, text]);
const w = (ms) => page.waitForTimeout(ms);
const Y = {
  map: await findY(`document.querySelector("#map .map-box")`, 10),
  snow: await findY(`document.querySelector("#presets")`, 10),
  shots: await findY(`document.querySelector("#pl-canvas").closest(".pl-step")`, 10),
  loader: await findY(`[...document.querySelectorAll("h3")].find((x) => x.textContent.includes("14-river model"))`, 10),
  replay: await findY(`document.querySelector("#replay")`, 0),
};
console.log("scroll targets", Y);
await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" })); await w(400);

// Each caption stays up >= 5 s; cues match deck/PITCH.md slide 4 (0 / 5 / 12 / 18 / 24 / 31 s after the first caption).
// (a) map with joint-flood lines
await glide(Y.map); await w(300);
const tCap = (Date.now() - t0) / 1000;
await cap("Live app: lines join rivers that flood together");
await w(5200);
// (b) March snow outlook → North price
await clickText("#presets", "No outlook"); await glide(Y.snow);
await cap("March snow set to HIGH: the northern price jumps"); await w(1000);
await clickText("#presets", "High snow"); await w(5000);
// (c) "How it works": real IQM Emerald shots, low vs snowy March
await page.evaluate(() => { const b = document.querySelector('.pl-snow button[data-k="low"]'); if (b) b.click(); });
await glide(Y.shots); await w(800);
await cap("Real IQM Emerald shots. Red = BOTH rivers flood. Low snow: little red"); await w(5800);
await page.evaluate(() => { const b = document.querySelector('.pl-snow button[data-k="high"]'); if (b) b.click(); });
await cap("Snowy March: more than twice the red"); await w(5600);
// (d) simplified (two-level) 14-river model on one chip, 1-in-10 run
await glide(Y.loader);
await w(800);
await cap("Simplified 14-river model on one chip: 18 qubits"); await w(6500);
// (e) 2005 replay
await glide(Y.replay); await w(600);
await clickText("#year-chips", "2005");
await cap("2005: Lapland floods together (March snow: top 15 %)"); await w(5500);
const tEnd = (Date.now() - t0) / 1000;
const video = page.video();
await ctx.close(); await browser.close();
console.log(`raw video: ${await video.path()}\nfirst caption at ~${tCap.toFixed(1)} s, end at ~${tEnd.toFixed(1)} s`);
