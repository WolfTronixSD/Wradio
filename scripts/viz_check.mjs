// Plays a few real stations in headless Chromium and checks that the
// visualizer gets real sound data (not the simulated fallback).
// Run from the repo root: node scripts/viz_check.mjs   (needs: npm i playwright)
import { chromium } from "playwright";
import http from "http";
import fs from "fs";

const html = fs.readFileSync("index.html");
const server = http.createServer((q, r) => { r.writeHead(200, { "content-type": "text/html" }); r.end(html); }).listen(8765);
const browser = await chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required"] });
const page = await browser.newPage();
await page.goto("http://localhost:8765/");
const ids = await page.evaluate(() => STATIONS.filter(s => s.cat !== "atc").map(s => s.n));
let bad = 0;
for (const n of ids) {
  await page.click("#stn-" + n);
  let max = 0;
  for (let i = 0; i < 16 && max <= 3; i++) {
    await page.waitForTimeout(500);
    max = await page.evaluate(() => { const d = new Uint8Array(analyser.frequencyBinCount); analyser.getByteFrequencyData(d); return Math.max(...d); });
  }
  const r = await page.evaluate(() => ({ name: STATIONS[curIdx]?.name, main: !audio.paused, clone: !audioFFT.paused, err: audioFFT.error && audioFFT.error.code }));
  const ok = max > 3;
  if (!ok) bad++;
  console.log(`${ok ? "LIVE" : "SIM "}  fft max ${String(max).padStart(3)}  main ${r.main ? "playing" : "stopped"}  ${r.name}${r.err ? "  (analysis copy error " + r.err + ")" : ""}`);
}
console.log(`\n${ids.length - bad}/${ids.length} stations give the real visualizer in a desktop browser`);
await browser.close(); server.close();
