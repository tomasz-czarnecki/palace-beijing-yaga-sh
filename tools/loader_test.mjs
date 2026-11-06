// Loading screen test: ?loading=1 forces it on in the automated browser. Screenshots of the card at intervals, then checks it ends and the view is ready.
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
const REPO = '/opt/data/workspace/000_Dev/palace-beijing-yaga-sh';
const OUT = process.argv[2] || '/opt/data/cache/scratch/palace_loader_test';
fs.mkdirSync(OUT, { recursive: true });
const require = createRequire('/opt/data/cache/scratch/palace_r11_kit_tools/node_modules/noop.js');
const { chromium } = require('playwright');
const PORT = Number(process.env.PORT || 8977);
const srv = spawn(REPO + '/.venv/bin/python', [REPO + '/tools/serve_local.py', '--port', String(PORT), '--public'], { cwd: REPO, stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
for (let k = 0; k < 60; k++) { try { await fetch(`http://127.0.0.1:${PORT}/reconstruction/3d.html`, { method: 'HEAD' }); break; } catch { await sleep(300); } }
const browser = await chromium.launch({ executablePath: '/opt/hermes/tools/chromium-1208/chrome-linux64/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
const errors = [];
try {
  const page = await (await browser.newContext({ viewport: { width: Number(process.env.W || 1280), height: Number(process.env.H || 800) } })).newPage();
  if (process.env.THROTTLE) { const c = await page.context().newCDPSession(page); await c.send('Network.enable'); await c.send('Network.emulateNetworkConditions', { offline: false, latency: 40, downloadThroughput: Number(process.env.THROTTLE), uploadThroughput: 1e6 }); }
  page.setDefaultTimeout(600000);
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e));
  const t0 = Date.now();
  await page.goto(`http://127.0.0.1:${PORT}/reconstruction/3d.html?loading=1`, { waitUntil: 'commit' });
  const snap = async (n) => { try { await page.screenshot({ path: `${OUT}/${n}.png`, timeout: 60000 }); console.log('shot', n, ((Date.now() - t0) / 1000).toFixed(1) + ' s'); } catch (e) { console.log('shot failed', n, String(e).slice(0, 80)); } };
  await sleep(1500); await snap('a_start');
  await sleep(3000); await snap('b_loading');
  let ready = false; const t1 = Date.now();
  while (!ready && Date.now() - t1 < 400000) {
    ready = await page.evaluate(() => window.__ready === true).catch(() => false);
    if (!ready) { await sleep(1500); if (!fs.existsSync(`${OUT}/c_mid.png`) && Date.now() - t1 > 5000) await snap('c_mid'); }
  }
  console.log('ready', ready, ((Date.now() - t0) / 1000).toFixed(1) + ' s');
  await sleep(300); await snap('d_done_line');
  const info = await page.evaluate(() => ({ sub: document.getElementById('ld-sub')?.textContent, count: document.getElementById('ld-count')?.textContent, steps: [...document.querySelectorAll('#ld-steps li')].map((l) => l.className + ' ' + l.textContent), lines: document.querySelectorAll('#ld-log .ln').length, glb: [...document.querySelectorAll('#ld-log .ln .n')].map((n) => n.textContent).filter((t) => /\(.*\)/.test(t)).slice(0, 20) }));
  console.log(JSON.stringify(info, null, 1));
  await sleep(3500); await snap('e_after');
  console.log('card gone', await page.evaluate(() => !document.getElementById('loading')));
} finally { await browser.close(); srv.kill(); }
console.log('errors', JSON.stringify(errors.slice(0, 8)));
