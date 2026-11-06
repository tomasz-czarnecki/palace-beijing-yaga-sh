// Round 23: Beautiful light and the cog, tested in the automated browser (SwiftShader here: slow, so the lowest useful quality, lightq=low).
// Loads 3d.html?time=19.5&lightq=low and checks: no console errors, __ready, the clock readout, play advances the hour, the cog (closed on load, opens, Escape, Enter from the keyboard, a press outside, a phone's width),
// Clean restores the old materials (no patched material left, no tone mapping, no shadow maps, the Clean fog back), Beautiful light again; then a second load with light=clean fetches no light code at all.
// Prints a pass/fail list; exits 1 on any failure.
//   node tools/light_test.mjs [--port 8993] [--base http://127.0.0.1:8991] (another server: none is started) [--out <dir>] (screenshots)
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
const REPO = '/opt/data/workspace/000_Dev/palace-beijing-yaga-sh';
const arg = (name, dflt) => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : dflt; };
const PORT = Number(arg('port', 8993));
const OUT = arg('out', '/opt/data/cache/scratch/palace_light_test');
fs.mkdirSync(OUT, { recursive: true });
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
const results = [];
const check = (name, ok, detail = '') => { results.push({ name, ok: Boolean(ok), detail }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? `  (${detail})` : ''}`); };
const t0 = Date.now();
try {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(900000);
  const errors = [], requests = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 240)); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + String(e).slice(0, 240)));
  page.on('request', (r) => requests.push(new URL(r.url()).pathname));
  await page.goto(`${base}/reconstruction/3d.html?time=19.5&lightq=low`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 900000, polling: 1000 });
  check('__ready is true', true, `${((Date.now() - t0) / 1000).toFixed(1)} s`);
  const s1 = await page.evaluate(() => { const b = window.viewer.beauty; return { on: b?.on, hour: b?.hour, patched: b?.patched, quality: b?.quality, clock: document.getElementById('tod-time').textContent, todHidden: document.getElementById('tod').hidden, valuetext: document.getElementById('sun-hour').getAttribute('aria-valuetext'), tone: window.viewer.renderer.toneMapping, shadows: window.viewer.renderer.shadowMap.enabled, night: b?.night?.stats() }; });
  check('Beautiful light is on by default', s1.on && s1.patched > 0, `${s1.patched} materials patched, quality ${s1.quality}`);
  check('the clock reads 19:30', s1.clock === '19:30' && !s1.todHidden, `"${s1.clock}", ${s1.valuetext}`);
  check('the night is loaded behind the dusk', Boolean(s1.night) && s1.night.galleries > 0 && s1.night.halls > 0, JSON.stringify(s1.night));
  check('beauty3d.js and night3d.js came through fetch', requests.some((p) => p.endsWith('/beauty3d.js')) && requests.some((p) => p.endsWith('/night3d.js')));
  await page.screenshot({ path: `${OUT}/a_1930.png` });

  // play the day
  const cogClosed = await page.evaluate(() => ({ hidden: document.getElementById('panel').hidden, expanded: document.getElementById('panel-cog').getAttribute('aria-expanded') }));
  check('the cog panel is closed on load', cogClosed.hidden && cogClosed.expanded === 'false');
  await page.click('#tod-play');
  const h0 = await page.evaluate(() => window.viewer.beauty.hour);
  await sleep(4000);
  const played = await page.evaluate(() => ({ hour: window.viewer.beauty.hour, playing: window.viewer.cycle.playing, steps: window.viewer.cycle.steps, label: document.getElementById('tod-play').getAttribute('aria-label'), speed: !document.getElementById('tod-speed').hidden, clock: document.getElementById('tod-time').textContent }));
  check('play advances the hour', played.playing && played.steps > 0 && played.hour !== h0, `${h0.toFixed(3)} -> ${played.hour.toFixed(3)} in ${played.steps} steps, clock ${played.clock}`);
  check('the play button turns to Pause, the speed button shows', played.label === 'Pause' && played.speed);
  await page.click('#tod-speed');
  check('the speed button changes the speed', (await page.evaluate(() => window.viewer.cycle.speed)) === 3);
  await page.click('#tod-play');
  check('pause stops it', !(await page.evaluate(() => window.viewer.cycle.playing)));

  // the cog: mouse, Escape, keyboard, a press outside
  await page.click('#panel-cog');
  const open1 = await page.evaluate(() => ({ hidden: document.getElementById('panel').hidden, expanded: document.getElementById('panel-cog').getAttribute('aria-expanded'), rect: document.getElementById('panel').getBoundingClientRect().toJSON() }));
  check('a click on the cog opens the panel', !open1.hidden && open1.expanded === 'true', `at x ${Math.round(open1.rect.x)}, ${Math.round(open1.rect.width)} px wide`);
  await page.screenshot({ path: `${OUT}/b_cog_open_1440.png` });
  await page.keyboard.press('Escape');
  const esc = await page.evaluate(() => ({ hidden: document.getElementById('panel').hidden, focus: document.activeElement?.id }));
  check('Escape closes it and gives the focus back to the cog', esc.hidden && esc.focus === 'panel-cog', `focus on #${esc.focus}`);
  await page.evaluate(() => document.getElementById('sun-hour').focus());
  let tabs = 0, onCog = false;
  for (; tabs < 12 && !onCog; tabs++) { await page.keyboard.press('Tab'); onCog = await page.evaluate(() => document.activeElement?.id === 'panel-cog'); }
  check('Tab reaches the cog', onCog, `${tabs} Tab presses from the slider`);
  await page.keyboard.press('Enter');
  const kb = await page.evaluate(() => ({ hidden: document.getElementById('panel').hidden, focus: document.activeElement?.id }));
  check('Enter opens it and moves the focus in', !kb.hidden && kb.focus === 'panel-close', `focus on #${kb.focus}`);
  await page.keyboard.press('Escape');
  await page.click('#panel-cog');
  await page.mouse.click(330, 24); // the header's empty middle: outside the panel, and no hall under it
  check('a press outside closes it', await page.evaluate(() => document.getElementById('panel').hidden));

  // Clean and back
  await page.click('#panel-cog');
  await page.click('[data-light="clean"]');
  await page.waitForFunction(() => window.viewer.beauty && !window.viewer.beauty.on);
  const clean = await page.evaluate(() => { const v = window.viewer; let shadowed = 0; v.scene.traverse((o) => { if (o.castShadow || o.receiveShadow) shadowed++; }); return { patched: v.beauty.patched, tone: v.renderer.toneMapping, shadows: v.renderer.shadowMap.enabled, fog: v.scene.fog && v.scene.fog.isFog && !v.scene.fog.isFogExp2 ? [v.scene.fog.near, v.scene.fog.far] : null, shadowed, todHidden: document.getElementById('tod').hidden, pressed: document.querySelector('[data-light="clean"]').getAttribute('aria-pressed'), url: location.search }; });
  check('Clean restores the old materials: no patched material left', clean.patched === 0, `${clean.patched} patched`);
  check('Clean: no tone mapping, no shadow maps, no mesh casting or taking shadow', clean.tone === 0 && !clean.shadows && clean.shadowed === 0, `toneMapping ${clean.tone}, shadowMap ${clean.shadows}, ${clean.shadowed} meshes flagged`);
  check('Clean: the Round 20 fog is back', clean.fog && clean.fog[0] === 6000 && clean.fog[1] === 40000, JSON.stringify(clean.fog));
  check('Clean: the time of day leaves the header, the switch shows Clean, the address says light=clean', clean.todHidden && clean.pressed === 'true' && /light=clean/.test(clean.url), clean.url);
  await page.screenshot({ path: `${OUT}/c_clean.png` });
  await page.click('[data-light="sun"]');
  await page.waitForFunction(() => window.viewer.beauty?.on);
  const back = await page.evaluate(() => window.viewer.beauty.patched);
  check('Beautiful light again', back > 0, `${back} patched`);
  await page.evaluate(() => localStorage.removeItem('palace-light'));

  // a phone's width
  await page.keyboard.press('Escape');
  await page.setViewportSize({ width: 390, height: 844 });
  await sleep(500);
  await page.click('#panel-cog');
  const phone = await page.evaluate(() => { const p = document.getElementById('panel'), r = p.getBoundingClientRect(), t = document.getElementById('tod').getBoundingClientRect(); return { w: r.width, x: r.x, top: r.top, bottom: r.bottom, scroll: getComputedStyle(p).overflowY, tall: p.scrollHeight > p.clientHeight, todTop: t.top, todW: t.width }; });
  check('on a phone the panel is the full width and scrolls', phone.w >= 370 && phone.x <= 10 && phone.scroll === 'auto' && phone.bottom <= 844, `${Math.round(phone.w)} px wide at x ${Math.round(phone.x)}, top ${Math.round(phone.top)}, overflow ${phone.scroll}, ${phone.tall ? 'longer than the screen: scrolls' : 'fits'}`);
  check('on a phone the time of day is a bar under the header', phone.todTop === 48 && phone.todW === 390, `top ${phone.todTop}, ${phone.todW} px`);
  await page.screenshot({ path: `${OUT}/d_cog_open_390.png` });
  check('no console errors', errors.length === 0, errors.slice(0, 4).join(' | '));
  await ctx.close();

  // light=clean: no light code fetched
  const ctx2 = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const p2 = await ctx2.newPage();
  p2.setDefaultTimeout(900000);
  const req2 = [], err2 = [];
  p2.on('request', (r) => req2.push(new URL(r.url()).pathname));
  p2.on('console', (m) => { if (m.type() === 'error') err2.push(m.text().slice(0, 240)); });
  await p2.goto(`${base}/reconstruction/3d.html?light=clean&lightq=low`, { waitUntil: 'load' });
  await p2.waitForFunction(() => window.__ready === true, null, { timeout: 900000, polling: 1000 });
  const c2 = await p2.evaluate(() => ({ beauty: window.viewer.beauty, tone: window.viewer.renderer.toneMapping, todHidden: document.getElementById('tod').hidden }));
  check('light=clean: Clean from the start, no light code fetched', c2.beauty === null && c2.tone === 0 && c2.todHidden && !req2.some((p) => /\/(beauty|night)3d\.js$/.test(p)), `${req2.filter((p) => /3d\.js$/.test(p)).length} *3d.js requests, none of them the light's`);
  check('light=clean: no console errors', err2.length === 0, err2.slice(0, 3).join(' | '));
  await ctx2.close();
} catch (err) {
  check('the test ran to its end', false, String(err).slice(0, 300));
} finally {
  await browser.close();
  if (srv) srv.kill();
}
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length} of ${results.length} passed in ${((Date.now() - t0) / 1000).toFixed(0)} s${failed.length ? `; FAILED: ${failed.map((r) => r.name).join('; ')}` : ''}`);
process.exit(failed.length ? 1 : 0);
