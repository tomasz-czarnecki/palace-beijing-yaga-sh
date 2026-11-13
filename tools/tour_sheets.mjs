// Round 32: contact sheets and the camera report of the guided tour (tour3d.js), for authoring and review. SwiftShader here: slow, so the lowest useful quality.
// Loads 3d.html?tour=1&lightq=low, pauses the tour, seeks it one frame per `--step` seconds (default 1) and screenshots each, then writes sheets of 4 columns per chapter
// (`<out>/sheet_<nn>_<id>.jpg`), and prints the clearance report (per chapter: the eye's least height over the ground, water or terrace, its least distance to a hall's box,
// the nearest model, wall or bridge surface by rays, how often the clamp moved it, the fastest turn and speed) and which models each chapter has in view. Writes report.json.
// The tour's controls are hidden (ui=0: the title and the captions stay); --ui shows them.
//   node tools/tour_sheets.mjs [--port 9181] [--ui] [--base http://127.0.0.1:9180] [--out <dir>] [--chapters gate,island] [--step 1] [--w 960 --h 540] [--hz 10] [--no-sheets] [--no-report]
import fs from 'node:fs';
import { spawn, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const REPO = '/opt/data/workspace/000_Dev/palace-beijing-yaga-sh';
const arg = (name, dflt) => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : dflt; };
const has = (name) => process.argv.includes(`--${name}`);
const PORT = Number(arg('port', 9181)), OUT = arg('out', '/opt/data/cache/scratch/palace_tour_sheets'), STEP = Number(arg('step', 1)), W = Number(arg('w', 960)), H = Number(arg('h', 540)), HZ = Number(arg('hz', 10));
const only = arg('chapters', '') ? arg('chapters').split(',') : null;
fs.mkdirSync(`${OUT}/frames`, { recursive: true });
const require = createRequire('/opt/data/cache/scratch/palace_r11_kit_tools/node_modules/noop.js');
const { chromium } = require('playwright');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let srv = null, base = arg('base', null);
if (!base) {
  srv = spawn(REPO + '/.venv/bin/python', [REPO + '/tools/serve_local.py', '--port', String(PORT), '--public'], { cwd: REPO, stdio: 'ignore' });
  base = `http://127.0.0.1:${PORT}`;
}
for (let k = 0; k < 60; k++) { try { await fetch(`${base}/reconstruction/3d.html`, { method: 'HEAD' }); break; } catch { await sleep(300); } }
const browser = await chromium.launch({ executablePath: '/opt/hermes/tools/chromium-1208/chrome-linux64/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await (await browser.newContext({ viewport: { width: W, height: H } })).newPage();
  page.setDefaultTimeout(900000);
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(`${base}/reconstruction/3d.html?tour=1&lightq=low${has('ui') ? '' : '&ui=0'}${has('tourdev') ? '&tourdev=1' : ''}`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__tour && window.__ready === true, null, { polling: 500 });
  await page.evaluate(() => window.__tour.pause());
  const chapters = await page.evaluate(() => window.__tour.chapters);
  const report = { clearance: has('no-report') ? [] : await page.evaluate((hz) => window.__tour.clearance(hz), HZ) };
  report.inView = await page.evaluate(() => {
    const s = window.__tour.inView(2), out = {};
    for (const [id, v] of Object.entries(s)) out[id] = { chapters: [...new Set(v.map((x) => x.ch))], centred: [...new Set(v.filter((x) => x.centre).map((x) => x.ch))], nearest_m: Math.min(...v.map((x) => x.d)) };
    return out;
  });
  console.log('Clearance per chapter (m; minSurface by 14 rays to 40 m against the models, walls and bridges; turn in degrees a second):');
  console.table(report.clearance);
  console.log('Models in view (chapters where a model is within 700 m in the frame; centred = in the middle of the frame):');
  console.table(Object.fromEntries(Object.entries(report.inView).map(([k, v]) => [k, { chapters: v.chapters.join(' '), centred: v.centred.join(' '), nearest_m: v.nearest_m }])));
  const models = await page.evaluate(() => Object.keys(window.viewer.models));
  report.missing = models.filter((m) => !report.inView[m]);
  console.log('Models never in view:', report.missing.length ? report.missing.join(', ') : 'none');
  if (!has('no-sheets')) {
    for (const [ci, ch] of chapters.entries()) {
      if (only && !only.includes(ch.id)) continue;
      const files = [];
      for (let t = ch.start + 0.5; t < ch.end; t += STEP) {
        await page.evaluate(async (t) => {
          window.__tour.seek(t);
          for (let k = 0; k < 3; k++) { window.viewer.kit.update(window.viewer.camera, 3); window.viewer.render(); await new Promise((r) => requestAnimationFrame(r)); }
        }, t);
        const f = `${OUT}/frames/${String(ci).padStart(2, '0')}_${t.toFixed(1)}.png`;
        await page.screenshot({ path: f });
        files.push([f, t]);
      }
      const sheet = `${OUT}/sheet_${String(ci).padStart(2, '0')}_${ch.id}.jpg`;
      execFileSync('python3', ['-c', `
import sys, json
from PIL import Image, ImageDraw
files = json.loads(sys.argv[1]); out = sys.argv[2]; cols = 4
ims = [Image.open(f).convert('RGB') for f, t in files]
w, h = ims[0].size; s = 0.5; tw, th = int(w * s), int(h * s)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * th), 'black')
for k, (im, (f, t)) in enumerate(zip(ims, files)):
    im = im.resize((tw, th)); d = ImageDraw.Draw(im); d.rectangle([0, 0, 56, 14], fill='black'); d.text((3, 1), f't={t:.1f}', fill='white')
    sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
sheet.save(out, quality=82)
`, JSON.stringify(files), sheet]);
      console.log('sheet', sheet, files.length, 'frames');
    }
  }
  report.errors = errors;
  fs.writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 1));
  console.log(errors.length ? `console errors:\n${errors.join('\n')}` : 'no console errors');
} finally {
  await browser.close();
  if (srv) srv.kill();
}
