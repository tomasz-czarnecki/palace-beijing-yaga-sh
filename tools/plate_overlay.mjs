// The plate overlay test's renders (Round 13): the 3D view from every fitted camera of an object (site/reconstruction/data/plates.json, tools/plate_overlay.py fit), one page load for all,
// then the composites by `tools/plate_overlay.py compose`. With --views, also the model's own views (front, rear, ends, joints, the panel) and, with --before <dir>, the same views of an older copy of site/.
//
//   node tools/plate_overlay.mjs --object XY01 [--port 8891] [--fits all,anchored] [--views] [--before /opt/data/cache/scratch/palace_r13_pilot_before/site] [--tag after]
//
// Needs Node and Playwright outside the repo (NODE_PATH, default /opt/data/cache/scratch/palace_r11_kit_tools/node_modules) and a Chrome (CHROME_PATH). Starts tools/serve_local.py --public on --port
// (and a plain static server on port + 1 for --before), stops them at the end. Software WebGL: everything of one view from one page load. Writes screenshots/r13/.
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, '..');
const NODE_PATH = process.env.NODE_PATH || '/opt/data/cache/scratch/palace_r11_kit_tools/node_modules';
const require = createRequire(path.join(NODE_PATH, 'noop.js'));
const { chromium } = require('playwright');
const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf('--' + n); return i < 0 ? d : args[i + 1]; };
const has = (n) => args.includes('--' + n);
const OBJ = opt('object', 'XY01');
const PORT = Number(opt('port', '8891'));
const FITS = opt('fits', 'all,anchored').split(',');
const TAG = opt('tag', 'after');
const OUT = path.join(ROOT, 'screenshots/r13');
fs.mkdirSync(OUT, { recursive: true });
const py = path.join(ROOT, '.venv/bin/python');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const servers = [];
const serve = async (cmd, argv, port) => {
  const p = spawn(cmd, argv, { stdio: 'ignore' });
  servers.push(p);
  for (let k = 0; k < 50; k++) { try { await fetch(`http://127.0.0.1:${port}/reconstruction/3d.html`, { method: 'HEAD' }); return; } catch { await sleep(200); } }
  throw new Error('server did not start on ' + port);
};
const stopAll = () => servers.forEach((p) => p.kill());
process.on('exit', stopAll);

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/opt/hermes/tools/chromium-1208/chrome-linux64/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const errors = [];
const newPage = async (w, h) => {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const page = await ctx.newPage();
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e));
  page.on('response', (r) => { if (r.status() >= 400 && !r.url().includes('favicon')) errors.push(`${r.status()} ${r.url()}`); });
  return page;
};
const canvasPng = async (page, file) => {
  const d = await page.evaluate(() => { window.viewer.render(); return window.viewer.renderer.domElement.toDataURL('image/png'); });
  fs.writeFileSync(file, Buffer.from(d.split(',')[1], 'base64'));
};
const settle = async (page) => {
  // the kit and the plants build their near tiles over several frames; ?shot=1 makes one render() wait for all
  await page.evaluate(() => new Promise((r) => { window.viewer.render(); requestAnimationFrame(() => requestAnimationFrame(r)); }));
};

await serve(py, [path.join(ROOT, 'tools/serve_local.py'), '--port', String(PORT), '--public'], PORT);
const base = `http://127.0.0.1:${PORT}`;
const t0 = Date.now();

// ---- 1. the renders from each fitted camera
if (!has('views-only')) {
  const plates = JSON.parse(fs.readFileSync(path.join(ROOT, 'site/reconstruction/data/plates.json'), 'utf8')).plates;
  const ids = Object.keys(plates).filter((k) => plates[k].object === OBJ);
  const page = await newPage(1600, 1200);
  await page.goto(`${base}/reconstruction/3d.html?shot=1&labels=0&greens=0&plate=${ids[0]}&plateimg=0`, { waitUntil: 'load' });
  await page.waitForFunction('window.__ready === true && window.__plateReady === true', null, { timeout: 600000 });
  for (const id of ids) for (const fit of FITS) {
    if (!plates[id].fits[fit]) continue;
    await page.evaluate(([i, f]) => { window.__plateReady = false; return window.plateMode(i, f); }, [id, fit]);
    await settle(page);
    await canvasPng(page, path.join(OUT, `render_${id}_${OBJ}_${fit}.png`));
    console.log('render', id, fit, `${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  await page.context().close();
}

// ---- 2. the model's own views, as world cameras from the model's frame (data/models.json)
const VIEWS = [
  // name, eye [x, y, z] and target in the model's frame (x east, y up from its base, z south)
  ['front', [0, 14, 78], [0, 6, 8]],
  ['rear', [4, 16, -72], [0, 6, -6]],
  ['west_end', [-62, 12, -18], [-14, 5, 2]],
  ['east_end', [62, 10, -6], [14, 5, 2]],
  ['aerial', [70, 60, 95], [0, 3, 8]],
  ['aerial_rear', [-70, 55, -80], [0, 3, -5]],
  ['joint_block_se', [21, 2.6, 15], [13.6, 1.2, 4.3]],
  ['joint_stair_w', [-22, 2.4, 16], [-12, 0.6, 6]],
  ['joint_pool', [9, 3, 34], [0, 0.8, 22]],
  ['joint_octagon_e', [40, 3.2, 34], [30.9, 1.5, 23.75]],
  ['joint_colonnade_w', [-26, 3, 4], [-15, 1.2, 2]],
  ['joint_north_stairs', [7, 2.4, -24], [2, 0.6, -11]],
];
const toWorld = (c, p) => { const s = Math.sin(c.rotationY), k = Math.cos(c.rotationY); return [c.position[0] + k * p[0] + s * p[2], c.position[1] + p[1], c.position[2] - s * p[0] + k * p[2]]; };
async function views(siteBase, tag, withPanel) {
  const page = await newPage(1400, 900);
  await page.goto(`${siteBase}/reconstruction/3d.html?shot=1&labels=0`, { waitUntil: 'load' });
  await page.waitForFunction('window.__ready === true', null, { timeout: 600000 });
  await page.waitForFunction('window.__modelsReady === true || !window.viewer.detailed', null, { timeout: 120000 }).catch(() => {});
  const frame = JSON.parse(fs.readFileSync(path.join(ROOT, 'site/reconstruction/data/models.json'), 'utf8')).models[OBJ];
  for (const [name, eye, tgt] of VIEWS) {
    const e = toWorld(frame, eye), t = toWorld(frame, tgt);
    await page.evaluate(([e, t]) => { const v = window.viewer; v.camera.position.set(...e); v.controls.target.set(...t); v.controls.update(); }, [e, t]);
    await settle(page);
    await canvasPng(page, path.join(OUT, `${tag}_${name}.png`));
    console.log(tag, name, `${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  for (const extra of has('conf') ? [['conf=1', 'conf'], ['assumed=0', 'assumed0']] : []) {
    await page.goto(`${siteBase}/reconstruction/3d.html?shot=1&labels=0&${extra[0]}`, { waitUntil: 'load' });
    await page.waitForFunction('window.__ready === true', null, { timeout: 600000 });
    await page.waitForFunction('window.__modelsReady === true', null, { timeout: 120000 }).catch(() => {});
    const e = toWorld(frame, [70, 60, 95]), t = toWorld(frame, [0, 3, 8]);
    await page.evaluate(([e, t]) => { const v = window.viewer; v.camera.position.set(...e); v.controls.target.set(...t); v.controls.update(); }, [e, t]);
    await settle(page);
    await canvasPng(page, path.join(OUT, `${tag}_aerial_${extra[1]}.png`));
  }
  await page.context().close();
  if (!withPanel) return;
  // the panel with the model's own view: a real viewport, no shot mode
  const p2 = await newPage(1400, 900);
  await p2.goto(`${siteBase}/reconstruction/3d.html?b=${OBJ}&labels=0`, { waitUntil: 'load' });
  await p2.waitForFunction('window.__ready === true && window.__modelsReady === true', null, { timeout: 600000 });
  await p2.evaluate(() => window.viewer.open('XY01'));
  await sleep(4000);
  await p2.evaluate(() => { const s = [...document.querySelectorAll('#bpanel h3')].find((h) => /Our model now/.test(h.textContent)); if (s) s.scrollIntoView(); });
  await sleep(4000);
  await p2.screenshot({ path: path.join(OUT, `${tag}_panel.png`) });
  await p2.context().close();
}
if (has('views') || has('views-only')) {
  await views(base, TAG, true);
  const before = opt('before', '');
  if (before) {
    await serve('python3', ['-m', 'http.server', String(PORT + 1), '--bind', '127.0.0.1', '--directory', before], PORT + 1);
    await views(`http://127.0.0.1:${PORT + 1}`, 'before', false);
  }
}
await browser.close();
stopAll();
console.log('console errors:', errors.length ? [...new Set(errors)].slice(0, 12) : 'none');
process.exit(0);
