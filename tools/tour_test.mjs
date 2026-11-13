// Round 32: the guided tour (tour3d.js, data/tour.json, /tour), tested in the automated browser (SwiftShader here: slow, so lightq=low).
// Checks: the normal view never fetches the tour's code or data, its Tour button shows once the gardens are in and starts the tour; 3d.html?tour=1 starts it and the clock runs;
// Space pauses and resumes, the arrow keys and a chapter chip change chapter, a drag and the wheel pause it (Resume shows), a light chip moves the hour; ui=0 hides the controls and
// then the cursor, keeps the captions; aspect=9:16 letterboxes the canvas; ch= starts at that chapter; the language switch; the end card and Watch again; Explore freely hands over
// the normal view; /tour shows its poster and starts on Begin, /tour?ch= and /zh/tour; a phone (390 x 844, touch): the chips scroll sideways, the card is narrow, a swipe up is the
// next chapter, a tap pauses; a 4K screen; reduced motion starts paused; no console errors, no failed requests; and the pages are up to date (tools/tour_page.py --check).
// Prints what /tour fetches before its first frame and in all (bytes as served here, and gzip as a host would send them), and the size of tour3d.js and tour.json.
// --perf also plays the whole tour twice at speed 2, at lightq=low and at the quality the view starts on, and prints the frame times per chapter and every step down.
// Prints a pass/fail list; exits 1 on any failure.
//   node tools/tour_test.mjs [--port 9182] [--base http://127.0.0.1:9180] [--out <dir>] [--perf]
import fs from 'node:fs';
import zlib from 'node:zlib';
import { spawn, execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const REPO = '/opt/data/workspace/000_Dev/palace-beijing-yaga-sh';
const arg = (name, dflt) => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : dflt; };
const PORT = Number(arg('port', 9182));
const OUT = arg('out', '/opt/data/cache/scratch/palace_tour_test');
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
const mb = (n) => `${(n / 1048576).toFixed(2)} MB`;
const fileOf = (p) => { const f = `${REPO}/site${decodeURIComponent(p)}`; return fs.existsSync(f) && fs.statSync(f).isFile() ? f : fs.existsSync(f + '.html') ? f + '.html' : null; };
const gz = new Map();
const gzSize = (p) => { if (!gz.has(p)) { const f = fileOf(p); gz.set(p, f ? zlib.gzipSync(fs.readFileSync(f), { level: 6 }).length : 0); } return gz.get(p); };

async function open(path, { viewport = { width: 1280, height: 720 }, touch = false, reduced = false, wait = 'ready', dpr = 1 } = {}) {
  const ctx = await browser.newContext({ viewport, hasTouch: touch, isMobile: touch, deviceScaleFactor: dpr, reducedMotion: reduced ? 'reduce' : 'no-preference' });
  const page = await ctx.newPage();
  page.setDefaultTimeout(900000);
  const errors = [], requests = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 240)); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + String(e).slice(0, 240)));
  page.on('requestfailed', (r) => { if (!(r.method() === 'HEAD' && r.failure()?.errorText === 'net::ERR_ABORTED')) errors.push(`failed: ${r.method()} ${r.url()} ${r.failure()?.errorText}`); });
  page.on('response', (r) => { if (r.status() >= 400) errors.push(`${r.status()}: ${r.url()}`); });
  page.on('requestfinished', async (r) => { const p = new URL(r.url()).pathname; const s = await r.sizes().catch(() => null); requests.push({ p, at: Date.now(), bytes: s ? s.responseBodySize : 0 }); });
  await page.goto(`${base}${path}`, { waitUntil: 'load' });
  if (wait === 'ready') await page.waitForFunction(() => window.__ready === true && window.__tour, null, { polling: 500 });
  if (wait === 'viewer') await page.waitForFunction(() => window.__ready === true, null, { polling: 500 });
  return { ctx, page, errors, requests };
}
const state = (page) => page.evaluate(() => { const T = window.__tour; return T ? { t: T.t, i: T.index, playing: T.playing, ended: T.ended, lang: T.lang, cinema: T.cinema, waiting: T.waiting } : null; });
const chipIndex = (page) => page.evaluate(() => [...document.querySelectorAll('#tour .t-chapters .chip')].findIndex((b) => b.getAttribute('aria-current') === 'true'));

try {
  // ---- the normal view: no tour code, a Tour button ----
  {
    const { ctx, page, errors, requests } = await open('/reconstruction/3d.html?lightq=low', { wait: 'viewer' });
    await page.waitForFunction(() => window.__modelsReady === true, null, { polling: 500 });
    check('the normal view fetches neither tour3d.js nor tour.json', !requests.some((r) => /tour3d\.js$|tour\.json$/.test(r.p)), requests.filter((r) => /tour/.test(r.p)).map((r) => r.p).join(' '));
    const btn = await page.evaluate(() => { const b = document.getElementById('tour-btn'); return { hidden: b.hidden, text: b.textContent }; });
    check('the header shows the Tour button once the gardens are in', !btn.hidden && btn.text === 'Tour');
    await page.click('#tour-btn');
    await page.waitForFunction(() => window.__tour && window.__tour.playing, null, { polling: 300 });
    check('the Tour button starts the tour, and fetches its code then', requests.some((r) => r.p.endsWith('/tour3d.js')) && requests.some((r) => r.p.endsWith('/tour.json')));
    const hdr = await page.evaluate(() => getComputedStyle(document.querySelector('.recon-header')).display);
    check('the dev header hides while the tour plays', hdr === 'none', hdr);
    await page.keyboard.press('Escape');
    await sleep(500);
    const back = await page.evaluate(() => ({ tour: Boolean(window.__tour), guided: document.body.classList.contains('guided'), header: getComputedStyle(document.querySelector('.recon-header')).display, url: location.search }));
    check('Escape leaves the tour on 3d.html: the normal view and header are back', !back.tour && !back.guided && back.header !== 'none' && !/tour=/.test(back.url), JSON.stringify(back));
    check('the normal view: no console errors, no failed requests', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }

  // ---- 3d.html?tour=1: the clock, keys, chips, a drag, the wheel, light chips, language, the end ----
  {
    const { ctx, page, errors } = await open('/reconstruction/3d.html?tour=1&lightq=low');
    const s0 = await state(page);
    await sleep(6000);
    const s1 = await state(page);
    check('3d.html?tour=1 starts the tour and its clock runs', s1.playing && s1.t > s0.t + 1, `t ${s0.t.toFixed(2)} -> ${s1.t.toFixed(2)} in 6 s (SwiftShader: a frame may take a second), chapter ${s1.i}`);
    await page.screenshot({ path: `${OUT}/a_start.png` });
    const cap = await page.evaluate(() => ({ head: document.querySelector('#tour .t-head').textContent, text: document.querySelector('#tour .t-texts').textContent, grade: document.querySelector('#tour .t-grade').textContent, start: !document.querySelector('#tour .t-cardbox.start').hidden }));
    check('the caption card holds the chapter title, its text and a grade', /圆明园/.test(cap.head) && cap.text.length > 60 && /Grade [ABC]/.test(cap.grade), `${cap.head} | ${cap.grade}`);
    check('the start card shows the reconstruction label', cap.start && /assumed where graded C/.test(await page.evaluate(() => document.querySelector('#tour .t-cardbox.start').textContent)));
    await page.keyboard.press('Space');
    const sp = await state(page); await sleep(1200); const sp2 = await state(page);
    check('Space pauses: the clock stands', !sp.playing && Math.abs(sp2.t - sp.t) < 1e-6);
    await page.keyboard.press('Space');
    await sleep(800);
    check('Space again resumes', (await state(page)).playing);
    await page.keyboard.press('ArrowRight');
    await sleep(900);
    const k1 = await state(page);
    check('the right arrow goes to the next chapter', k1.i === 1 && (await chipIndex(page)) === 1, `chapter ${k1.i}`);
    await page.click('#tour .t-chapters .chip[data-ch="5"]');
    await sleep(900);
    const k5 = await state(page);
    check('a chapter chip jumps to that chapter', k5.i === 5 && (await chipIndex(page)) === 5, `chapter ${k5.i}`);
    await page.keyboard.press('ArrowLeft');
    await sleep(900);
    check('the left arrow goes back a chapter', (await state(page)).i === 4);
    const h0 = await page.evaluate(() => window.viewer.beauty.hour);
    await page.click('#tour .t-lights .chip[data-light="golden"]');
    await sleep(4500);
    const h1 = await page.evaluate(() => ({ hour: window.viewer.beauty.hour, pressed: document.querySelector('#tour .t-lights .chip[data-light="golden"]').getAttribute('aria-pressed') }));
    check('a light chip eases the hour to it and stays pressed', Math.abs(h1.hour - 18.9) < 0.1 && h1.pressed === 'true', `${h0.toFixed(2)} -> ${h1.hour.toFixed(2)}`);
    // a drag on the view pauses, Resume shows and plays again
    await page.mouse.move(640, 400); await page.mouse.down(); await page.mouse.move(700, 380, { steps: 6 }); await page.mouse.up();
    await sleep(300);
    const dr = await page.evaluate(() => ({ playing: window.__tour.playing, resume: !document.querySelector('#tour .t-resume').hidden }));
    check('a drag pauses the tour and shows Resume', !dr.playing && dr.resume);
    await page.click('#tour .t-resume');
    await sleep(600);
    check('Resume plays again', (await state(page)).playing);
    await page.mouse.move(640, 400); await page.mouse.wheel(0, 240);
    await sleep(500);
    check('the wheel pauses it', !(await state(page)).playing);
    await page.click('#tour [data-act="play"]');
    await sleep(300);
    check('the play button plays', (await state(page)).playing);
    await page.mouse.click(640, 400);
    await sleep(300);
    check('a click on the view pauses', !(await state(page)).playing);
    await page.mouse.click(640, 400);
    await sleep(300);
    check('a second click plays', (await state(page)).playing);
    await page.click('#tour [data-act="speed"]');
    check('the speed button steps the speed', (await page.evaluate(() => window.__tour.speed)) === 2);
    await page.click('#tour [data-act="lang"]');
    await sleep(200);
    const zh = await page.evaluate(() => ({ lang: window.__tour.lang, text: document.querySelector('#tour .t-texts').textContent, chip: document.querySelector('#tour .t-chapters .chip').textContent }));
    check('the language switch shows the Chinese captions and chips', zh.lang === 'zh' && /[一-鿿]{8}/.test(zh.text) && zh.chip === '全景', zh.text.slice(0, 30));
    await page.screenshot({ path: `${OUT}/b_zh.png` });
    await page.click('#tour [data-act="lang"]');
    await page.click('#tour [data-act="cinema"]');
    await sleep(300);
    const cin = await page.evaluate(() => ({ cinema: window.__tour.cinema, bottom: getComputedStyle(document.querySelector('#tour .t-bottom')).display, card: getComputedStyle(document.querySelector('#tour .t-card')).display }));
    check('Cinema hides the controls and keeps the caption', cin.cinema && cin.bottom === 'none' && cin.card !== 'none');
    await page.keyboard.press('Escape');
    check('Escape leaves cinema first', !(await page.evaluate(() => window.__tour.cinema)));
    // the end
    await page.evaluate(() => { window.__tour.seek(window.__tour.total - 1.2); window.__tour.play(); });
    await page.waitForFunction(() => window.__tour.ended, null, { polling: 300, timeout: 120000 });
    const end = await page.evaluate(() => ({ shown: !document.querySelector('#tour .t-cardbox.end').hidden, text: document.querySelector('#tour .t-cardbox.end').textContent }));
    check('the end card follows the last chapter, with Watch again, Explore and the credits', end.shown && /Watch again/.test(end.text) && /Explore the gardens/.test(end.text) && /Credits/.test(end.text));
    await sleep(900);
    await page.screenshot({ path: `${OUT}/c_end.png` });
    await page.click('#tour [data-act="again"]');
    await sleep(900);
    const ag = await state(page);
    check('Watch again starts from the beginning', ag.playing && ag.t < 3 && !ag.ended, `t ${ag.t.toFixed(2)}`);
    check('3d.html?tour=1: no console errors, no failed requests', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }

  // ---- deep link, ui=0, aspect=9:16 ----
  {
    const { ctx, page, errors } = await open('/reconstruction/3d.html?tour=1&lightq=low&ch=haiyan&ui=0&aspect=9:16&captions=both');
    const s = await state(page);
    const ids = await page.evaluate(() => window.__tour.chapters.map((c) => c.id));
    check('ch= starts at that chapter', s.i === ids.indexOf('haiyan'), `chapter ${s.i} (${ids[s.i]})`);
    const ui = await page.evaluate(() => ({ bottom: getComputedStyle(document.querySelector('#tour .t-bottom')).display, top: getComputedStyle(document.querySelector('#tour .t-top')).display, card: getComputedStyle(document.querySelector('#tour .t-card')).display, texts: document.querySelectorAll('#tour .t-texts .t-text').length }));
    check('ui=0 hides the controls and keeps the captions; captions=both shows both languages', ui.bottom === 'none' && ui.top === 'none' && ui.card !== 'none' && ui.texts === 2, JSON.stringify(ui));
    await page.mouse.move(300, 300);
    await sleep(2600);
    check('ui=0: the cursor hides after 2 s still', await page.evaluate(() => document.body.classList.contains('tour-idle')));
    const cv = await page.evaluate(() => { const c = window.viewer.renderer.domElement.getBoundingClientRect(); return { w: c.width, h: c.height, x: c.left, fov: window.viewer.camera.fov, aspect: window.viewer.camera.aspect }; });
    check('aspect=9:16 letterboxes the canvas and widens the field of view', Math.abs(cv.w / cv.h - 9 / 16) < 0.01 && cv.x > 100 && cv.fov > 45, JSON.stringify(cv));
    await sleep(2500);
    await page.screenshot({ path: `${OUT}/d_ui0_9x16.png` });
    check('ui=0 and aspect: no console errors, no failed requests', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }

  // ---- /tour: the poster, Begin, what it fetches; Explore freely ----
  {
    const { ctx, page, errors, requests } = await open('/tour?lightq=low', { wait: 'none' });
    const start = Date.now();
    const poster = await page.evaluate(() => ({ shown: Boolean(document.getElementById('tour-poster')), title: document.title, og: document.querySelector('meta[property="og:image"]')?.content, canonical: document.querySelector('link[rel=canonical]')?.href, ai: document.querySelector('#tour-poster .tp-ai')?.textContent }));
    check('/tour opens on its poster with the title, an AI label and a share card', poster.shown && /guided tour/.test(poster.title) && /hero-1-overview/.test(poster.og) && /AI visualisation/.test(poster.ai), poster.title);
    await page.waitForFunction(() => performance.getEntriesByName('palace-first-frame').length > 0, null, { polling: 200 });
    const firstAt = Date.now();
    await page.screenshot({ path: `${OUT}/e_poster.png` });
    await page.waitForFunction(() => window.__tour, null, { polling: 300 });
    check('/tour waits for Begin', !(await state(page)).playing);
    await page.click('#tour-begin');
    await page.waitForFunction(() => window.__tour.playing || window.__tour.waiting, null, { polling: 300 });
    await sleep(1200);
    check('Begin removes the poster and the tour plays', !(await page.evaluate(() => document.getElementById('tour-poster'))) && (await state(page)).playing);
    await page.waitForFunction(() => window.__ready === true, null, { polling: 500 });
    await sleep(1500);
    const first = requests.filter((r) => r.at <= firstAt), all = requests;
    const sum = (list, f) => list.reduce((n, r) => n + f(r), 0);
    const kinds = (list) => { const k = {}; for (const r of list) { const t = /\.glb$/.test(r.p) ? 'models' : /\.js$/.test(r.p) ? 'code' : /\.(webp|jpg|png|svg)$/.test(r.p) ? 'pictures' : /\.woff2$/.test(r.p) ? 'fonts' : /\.(json|geojson)$/.test(r.p) ? 'data' : /\.(bin|i16|u8)$/.test(r.p) ? 'binary' : 'pages'; (k[t] ||= { files: 0, bytes: 0, gz: 0 }); k[t].files++; k[t].bytes += r.bytes; k[t].gz += gzSize(r.p); } return Object.fromEntries(Object.entries(k).map(([a, b]) => [a, `${b.files} files, ${mb(b.bytes)} (gzip ${mb(b.gz)})`])); };
    console.log(`  /tour before the first frame (${((firstAt - start) / 1000).toFixed(1)} s here): ${first.length} files, ${mb(sum(first, (r) => r.bytes))} as served, gzip ${mb(sum(first, (r) => gzSize(r.p)))}`);
    console.log('   ', JSON.stringify(kinds(first)));
    console.log(`  /tour in all, once every model is in: ${all.length} files, ${mb(sum(all, (r) => r.bytes))} as served, gzip ${mb(sum(all, (r) => gzSize(r.p)))}`);
    console.log('   ', JSON.stringify(kinds(all)));
    for (const f of ['site/reconstruction/tour3d.js', 'site/reconstruction/data/tour.json']) { const b = fs.readFileSync(`${REPO}/${f}`); console.log(`  ${f}: ${(b.length / 1024).toFixed(1)} KB, gzip ${(zlib.gzipSync(b).length / 1024).toFixed(1)} KB`); }
    check('/tour fetches nothing from research/ or /_local/', !all.some((r) => /\/_local\/|research/.test(r.p)));
    await page.click('#tour [data-act="explore"]');
    await sleep(800);
    const ex = await page.evaluate(() => ({ tour: Boolean(window.__tour), page: document.body.classList.contains('tour-page'), header: getComputedStyle(document.querySelector('.recon-header')).display, path: location.pathname, search: location.search, controls: window.viewer.controls.enabled }));
    check('Explore freely hands over the normal 3D view at the same place', !ex.tour && !ex.page && ex.header !== 'none' && ex.path === '/reconstruction/3d.html' && /^\?cam=/.test(ex.search) && ex.controls, JSON.stringify(ex));
    check('/tour: no console errors, no failed requests', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await open('/tour?lightq=low&ch=fountains&poster=0');
    const s = await state(page), ids = await page.evaluate(() => window.__tour.chapters.map((c) => c.id));
    check('/tour?ch= starts at that chapter (poster=0 skips the poster)', s.i === ids.indexOf('fountains') && s.playing !== undefined, `chapter ${s.i}`);
    const share = await page.evaluate(() => { window.__tour.act('share'); return new URL(location.href).pathname; });
    check('the share link is the page with ?ch=', share === '/tour');
    check('/tour?ch=: no console errors', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await open('/zh/tour?lightq=low&poster=0');
    const z = await page.evaluate(() => ({ lang: document.documentElement.lang, tour: window.__tour.lang, sub: document.querySelector('#tour .t-sub').textContent }));
    check('/zh/tour starts in Chinese', z.lang === 'zh-Hans' && z.tour === 'zh' && /复原/.test(z.sub), JSON.stringify(z));
    await sleep(8000);
    await page.screenshot({ path: `${OUT}/f_zh_tour.png` });
    check('/zh/tour: no console errors', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }

  // ---- a phone ----
  {
    const { ctx, page, errors } = await open('/tour?poster=0', { viewport: { width: 390, height: 844 }, touch: true, dpr: 2 });
    await sleep(3000);
    const ph = await page.evaluate(() => { const c = document.querySelector('#tour .t-chapters'), card = document.querySelector('#tour .t-card').getBoundingClientRect(); return { scrolls: c.scrollWidth > c.clientWidth + 20, overflowX: getComputedStyle(c).overflowX, card: Math.round(card.width), fov: window.viewer.camera.fov, quality: window.viewer.beauty.quality, ratio: window.viewer.renderer.getPixelRatio(), bodyScroll: document.documentElement.scrollWidth }; });
    check('phone: the chapter chips scroll sideways, the caption card fits, the field widens', ph.scrolls && ph.overflowX === 'auto' && ph.card <= 370 && ph.fov > 60 && ph.bodyScroll <= 390, JSON.stringify(ph));
    check('phone: the lowest quality tier, pixel ratio at most 1.5', ph.quality === 'min' && ph.ratio <= 1.5, `${ph.quality}, ${ph.ratio}`);
    await page.screenshot({ path: `${OUT}/g_phone.png` });
    // SwiftShader takes a second or more a frame here, so a gesture sent while the tour renders arrives seconds long; the touch checks run with the tour held still (the page idle), then let it play
    // and OrbitControls would turn the view (a frame) on every move of the swipe: its look-around is off for the gesture, the tour's own touch handling is what is tested
    await page.evaluate(() => { window.__tour.pause(false); window.viewer.controls.enabled = false; });
    await sleep(1500);
    const i0 = (await state(page)).i;
    // even idle, this machine composites a phone-sized SwiftShader canvas in seconds and CDP's emulated touches wait for each frame (a swipe arrives 7 s long):
    // the swipe is dispatched as touch pointer events in one go, which is exactly what the tour's handler reads (the taps the same way)
    await page.evaluate(() => {
      const c = window.viewer.renderer.domElement, ev = (type, y) => c.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerType: 'touch', pointerId: 7, isPrimary: true, clientX: 195, clientY: y }));
      ev('pointerdown', 560); ev('pointermove', 470); ev('pointermove', 380); ev('pointerup', 380);
    });
    await sleep(1500);
    const sw = await state(page);
    check('phone: a swipe up goes to the next chapter and plays on', sw.i === i0 + 1 && sw.playing, `chapter ${i0} -> ${sw.i}`);
    const tap = () => page.evaluate(() => { const c = window.viewer.renderer.domElement, ev = (type) => c.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerType: 'touch', pointerId: 8, isPrimary: true, clientX: 195, clientY: 500 })); window.viewer.controls.enabled = false; ev('pointerdown'); ev('pointerup'); });
    await tap();
    await sleep(600);
    check('phone: a tap pauses', !(await state(page)).playing);
    await tap();
    await sleep(600);
    check('phone: a second tap plays', (await state(page)).playing);
    await page.evaluate(() => { window.viewer.controls.enabled = true; });
    check('phone: no console errors', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }
  // ---- a 4K screen, reduced motion ----
  {
    const { ctx, page, errors } = await open('/reconstruction/3d.html?tour=1&lightq=low&ch=haiyan', { viewport: { width: 3840, height: 2160 } });
    await sleep(3000);
    const k = await page.evaluate(() => ({ card: Math.round(document.querySelector('#tour .t-card').getBoundingClientRect().width), font: getComputedStyle(document.querySelector('#tour .t-text')).fontSize }));
    check('4K: the caption card and its type scale up', k.card >= 540 && parseFloat(k.font) >= 20, JSON.stringify(k));
    await page.screenshot({ path: `${OUT}/h_4k.png` });
    check('4K: no console errors', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await open('/reconstruction/3d.html?tour=1&lightq=low', { reduced: true });
    await sleep(1500);
    const r = await page.evaluate(() => ({ playing: window.__tour.playing, i: window.__tour.index, resume: document.querySelector('#tour .t-resume').hidden ? '' : document.querySelector('#tour .t-resume').textContent, speed: window.__tour.speed }));
    check('reduced motion: starts paused on chapter 1 with a play button, slower', !r.playing && r.i === 0 && /Play/.test(r.resume) && r.speed < 1, JSON.stringify(r));
    check('reduced motion: no console errors', errors.length === 0, errors.slice(0, 3).join(' | '));
    await ctx.close();
  }
  try { execFileSync(REPO + '/.venv/bin/python', [REPO + '/tools/tour_page.py', '--check'], { cwd: REPO }); check('the tour pages are up to date with 3d.html (tools/tour_page.py --check)', true); }
  catch (e) { check('the tour pages are up to date with 3d.html (tools/tour_page.py --check)', false, String(e.stderr || e.stdout)); }

  // ---- --perf: the whole tour, live, at speed 2 ----
  if (process.argv.includes('--perf')) {
    for (const q of ['lightq=low', '']) {
      const { ctx, page } = await open(`/reconstruction/3d.html?tour=1&speed=2${q ? '&' + q : ''}`, { viewport: { width: 1280, height: 720 } });
      const tot = await page.evaluate(() => window.__tour.total);
      const w0 = Date.now();
      await page.waitForFunction(() => window.__tour.ended, null, { polling: 2000, timeout: 1800000 });
      const r = await page.evaluate(() => ({ frames: window.__tour.frameStats(), steps: window.__tour.adaptations, quality: window.viewer.beauty.quality, clamps: window.__tour.clamps }));
      console.log(`  perf ${q || 'the quality the view starts on (no lightq)'}: the ${tot} s tour played in ${((Date.now() - w0) / 1000).toFixed(0)} s at speed 2; quality at the end ${r.quality}; ${r.steps.length} step(s) down; eye clamped on ${r.clamps} frames`);
      console.table(r.frames);
      for (const s of r.steps) console.log('   step', JSON.stringify(s));
      fs.writeFileSync(`${OUT}/perf_${q ? 'low' : 'auto'}.json`, JSON.stringify(r, null, 1));
      await ctx.close();
    }
  }
} finally {
  await browser.close();
  if (srv) srv.kill();
}
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} passed in ${((Date.now() - t0) / 1000).toFixed(0)} s${failed.length ? `; failed: ${failed.map((f) => f.name).join('; ')}` : ''}`);
process.exit(failed.length ? 1 : 0);
