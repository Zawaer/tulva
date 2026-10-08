// Records a ~60 s scripted walkthrough of the Tulva demo app (1920x1080, captions burned in).
//   source /data/chats/s_7z3ZoxoroN/env.sh; node deck/video/record_demo.mjs [url]
import { createRequire } from "node:module";
const require = createRequire("/data/chats/s_7z3ZoxoroN/talkoot/package.json");
const { chromium } = require("playwright");
const APP_URL = process.argv[2] || "http://127.0.0.1:3141";
const OUT = new URL("./", import.meta.url).pathname;

const browser = await chromium.launch({ args: ["--no-sandbox"] });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1,
  recordVideo: { dir: OUT + "raw", size: { width: 1920, height: 1080 } } });  
const page = await ctx.newPage();
await page.goto(APP_URL, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);
await page.evaluate(() => { document.documentElement.style.zoom = "1.3"; });   // readable on a projector
await page.waitForTimeout(800);
await page.addStyleTag({ content: `
  #demo-cap{position:fixed;left:50%;bottom:36px;transform:translateX(-50%);z-index:99999;max-width:1200px;
    background:rgba(11,31,58,.92);color:#fff;font:600 23px/1.35 Arial,sans-serif;padding:18px 34px;border-radius:14px;
    box-shadow:0 8px 30px rgba(0,0,0,.25);text-align:center;transition:opacity .4s}
  html{scroll-behavior:smooth}` });
await page.evaluate(() => { const d = document.createElement("div"); d.id = "demo-cap"; document.body.appendChild(d); });
const cap = (t) => page.evaluate((t) => { document.getElementById("demo-cap").textContent = t; }, t);
const to = async (sel, offset = -80) => page.evaluate(([s, o]) => {
  const el = document.querySelector(s); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY + o, behavior: "smooth" });
}, [sel, offset]);
const clickText = async (scope, text) => { const b = page.locator(`${scope} button`, { hasText: text }).first(); if (await b.count()) await b.click(); };
const w = (ms) => page.waitForTimeout(ms);

await cap("65 years of SYKE river data · 14 river flood-risk areas · linked areas flood together");
await w(7000);
await to("#outlook"); await w(1500);
await cap("Set the March snow outlook…");
await clickText("#presets", "No outlook"); await w(2500);
await clickText("#presets", "High snow"); await cap("High snow: chance of ≥2 gauges over 1-in-50 jumps, and the index price follows"); await w(6500);
await to("#product"); await w(1500);
await cap("Tulva Index: €10M if ≥2 northern gauges pass 1-in-50 · independence vs Tulva vs snowy March");
await w(8000);
await to("#hood"); await w(1500);
await cap("Under the hood: the same joint model on real quantum chips: IBM Marrakesh, IQM Garnet");
await w(7000);
await page.evaluate(() => { const h = [...document.querySelectorAll("h3")].find((x) => x.textContent.includes("All 14 areas")); if (h) window.scrollTo({ top: h.getBoundingClientRect().top + window.scrollY - 60, behavior: "smooth" }); });
await w(1500);
await cap("All 14 areas on IQM Emerald (18 qubits): the chip reproduces the joint tail independence misses");
await w(8000);
await to("#replay"); await w(1500);
await clickText("#year-chips", "2005");
await cap("Replay May 2005: Kittilä, Ivalo, Rovaniemi and Tornio over their flood levels together");
await w(8000);
await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" })); await w(1200);
await cap("Tulva · spring-flood risk, priced jointly");
await w(3000);
const video = page.video();
await ctx.close(); await browser.close();
console.log("raw video:", await video.path());
