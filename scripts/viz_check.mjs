// Plays a few real stations in headless Chromium and checks that the
// visualizer gets real sound data (not the simulated fallback).
// Run from the repo root: node scripts/viz_check.mjs   (needs: npm i playwright)
import { chromium } from "playwright";
import http from "http";
import fs from "fs";

const html = fs.readFileSync("index.html");
const server = http.createServer((q, r) => { r.writeHead(200, { "content-type": "text/html" }); r.end(html); }).listen(8765);
// Real Google Chrome when it's installed (GitHub runners have it), else Playwright's Chromium
const opts = { args: ["--autoplay-policy=no-user-gesture-required"] };
const browser = await chromium.launch({ ...opts, channel: "chrome" }).catch(() => chromium.launch(opts));
console.log("browser:", browser.version());
const page = await browser.newPage();
await page.goto("http://localhost:8765/");
// Extra stream URLs on the command line are tried as temporary stations
const extra = process.argv.slice(2);
if (extra.length) await page.evaluate(urls => urls.forEach((url, i) => {
  const s = { n: 900 + i, name: url, url, cat: "music" }; STATIONS.push(s);
  const b = document.createElement("button"); b.id = "stn-" + s.n; b.onclick = () => play(s); document.body.appendChild(b);
}), extra);
const ids = await page.evaluate(() => STATIONS.filter(s => s.cat !== "atc" && !s.feed).map(s => s.n));
let bad = 0;
for (const n of ids) {
  await page.evaluate(n => document.getElementById("stn-" + n).click(), n);
  // wait until the analysis copy has really played a second of this station
  let t = 0;
  for (let i = 0; i < 24 && t < 1; i++) { await page.waitForTimeout(500); t = await page.evaluate(() => audioFFT.currentTime); }
  let max = 0;
  for (let i = 0; i < 6 && max <= 3; i++) {
    await page.waitForTimeout(250);
    max = await page.evaluate(() => { const d = new Uint8Array(analyser.frequencyBinCount); analyser.getByteFrequencyData(d); return Math.max(...d); });
  }
  if (t < 1) max = 0; // never played: whatever the analyser holds is from the last station
  const r = await page.evaluate(() => ({ name: STATIONS[curIdx]?.name, main: !audio.paused, clone: !audioFFT.paused, err: audioFFT.error && audioFFT.error.code, mainErr: audio.error && (audio.error.code + " " + audio.error.message) }));
  const ok = max > 3;
  if (!ok) bad++;
  console.log(`${ok ? "LIVE" : "SIM "}  fft max ${String(max).padStart(3)}  main ${r.main ? "playing" : "stopped"}  ${r.name}${r.err ? "  (analysis copy error " + r.err + ")" : ""}${r.mainErr ? "  (player error " + r.mainErr + ")" : ""}`);
}
console.log(`\n${ids.length - bad}/${ids.length} stations give the real visualizer in a desktop browser`);
await browser.close(); server.close();
