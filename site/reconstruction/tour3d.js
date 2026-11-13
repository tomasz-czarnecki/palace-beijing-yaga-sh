// Round 32: the guided tour of the 3D view, a live render in the visitor's browser. An ES module, fetched by 3d.js only for ?tour=1, the page /tour (tour.html) or the header's Tour button, so the normal view never loads it.
// Data: data/tour.json (hand-edited: chapters, their key poses in a model's own frame, the hour, the captions and what they rest on). Captions only restate the research.
// The camera is a pure function of the tour's time: a centripetal Catmull-Rom spline for the eye and another for the target through the chapter's key poses, the previous chapter's last pose first (the flight in),
// timed by a monotone cubic through the poses' times with a still start and end, so a dropped frame never makes it jump and the captions never drift. The eye is kept 1.7 m above the ground, the water and a model's
// terrace, and out of every hall's box. The hour of Beautiful light (beauty3d.js) eases from chapter to chapter during the flight in. The clock is wall-clock time times the speed; it holds while a chapter's models are still loading.
// URL (read here): tour=1 (3d.html: start the tour), ch=<chapter id>, ui=0 (no controls, the cursor hides after 2 s), captions=en|zh|both|none, aspect=16:9|9:16 (letterbox), fs=1 (full screen on the first click),
// poster=0 (/tour: start without the poster), tourdev=1 (the authoring drawer: Record pose prints the camera as a pose of tour.json), speed=0.5|1|1.5, lightq= (pins the quality: no adaptation).
// window.__tour: the test's handle (tools/tour_test.mjs).

const CAPTION_IN_S = 0.6, CAPTION_OUT_S = 0.8, EYE_CLEAR_M = 1.7, BOX_CLEAR_M = 2.5, RESUME_S = 1.5, MANUAL_EASE_S = 1.5;
const SPEEDS = [0.5, 1, 1.5];
const FRAME_BUDGET_MS = 33, ADAPT_WINDOW_S = 2.5; // frames slower than this, as a median over the window: one step down, at most once a chapter
const BASE_FOV = 45, PORTRAIT_MIN_HFOV = 50, MAX_FOV = 85; // portrait: the horizontal field widens so the subject stays in frame

const T = {
  en: {
    title: "Yuanmingyuan", sub: "before October 1860, a reconstruction", play: "Play", pause: "Pause", prev: "Previous chapter", next: "Next chapter", speed: "Speed",
    free: "Free look", resume: "Resume tour", cinema: "Cinema", cinemaExit: "Leave cinema", fullscreen: "Full screen", share: "Share", copied: "Link copied", explore: "Explore freely", exit: "Leave the tour",
    help: "How to record", lang: "中文", grade: "Grade", chapters: "Chapters", light: "Light", loading: "Preparing the next scene…", starting: "Starting the tour; the detailed buildings come in as it plays.",
    label: "A reconstruction: buildings sourced where graded A or B, assumed where graded C; atmosphere (people, boats, weather) is not evidence.",
    startLine: "A live tour of the 3D reconstruction, about five minutes.",
    endHead: "The end of the tour",
    end: "This was an evidence-graded reconstruction of 圆明园 Yuanmingyuan before October 1860: every building traced to a source and graded A, B or C, and the guesses marked.",
    again: "Watch again", gardens: "Explore the gardens", credits: "Credits", home: "Homepage",
    helpText: "To keep a video, record this page with your screen recorder. On a Mac, Shift-Command-5 and record the whole screen; a 4K screen gives the best result. Cinema hides the controls; add ?aspect=16:9 or ?aspect=9:16 to the address to frame it.",
    keys: "Space: play or pause · ← →: chapters · drag: look around",
  },
  zh: {
    title: "圆明园", sub: "1860年10月以前的复原", play: "播放", pause: "暂停", prev: "上一章", next: "下一章", speed: "速度",
    free: "自由视角", resume: "继续导览", cinema: "影院模式", cinemaExit: "退出影院模式", fullscreen: "全屏", share: "分享", copied: "链接已复制", explore: "自由探索", exit: "退出导览",
    help: "录制方法", lang: "EN", grade: "等级", chapters: "章节", light: "光线", loading: "正在准备下一处景物……", starting: "导览开始；精细建筑模型将在播放中陆续载入。",
    label: "复原：评为A级或B级的建筑有据可依，评为C级的是推测；氛围（人物、船只、天气）不是证据。",
    startLine: "三维复原的实时导览，约五分钟。",
    endHead: "导览结束",
    end: "这是1860年10月以前圆明园的分级复原：每座建筑都追溯到史料，并评为A、B或C级，推测之处都已标明。",
    again: "再看一遍", gardens: "自由游览园林", credits: "致谢与来源", home: "首页",
    helpText: "如需保存视频，请用屏幕录制工具录下本页。在Mac上按Shift-Command-5录制整个屏幕；4K屏幕效果最好。影院模式会隐藏控件；在地址后加 ?aspect=16:9 或 ?aspect=9:16 可设定画幅。",
    keys: "空格：播放或暂停 · ← →：章节 · 拖动：环顾",
  },
};

const clamp = (x, a, b) => Math.min(Math.max(x, a), b);
const smoother = (x) => { x = clamp(x, 0, 1); return x * x * x * (x * (x * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;

// A monotone cubic through (ts, vs) with a still start and end (Fritsch-Carlson), so the camera never runs back and eases in and out.
function monotone(ts, vs) {
  const n = ts.length, h = [], d = [], m = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) { h[i] = ts[i + 1] - ts[i]; d[i] = (vs[i + 1] - vs[i]) / h[i]; }
  for (let i = 1; i < n - 1; i++) {
    if (d[i - 1] * d[i] <= 0) continue;
    const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1];
    m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
  }
  return (t) => {
    if (t <= ts[0]) return vs[0];
    if (t >= ts[n - 1]) return vs[n - 1];
    let i = 0;
    while (i < n - 2 && t > ts[i + 1]) i++;
    const s = (t - ts[i]) / h[i], s2 = s * s, s3 = s2 * s;
    return (2 * s3 - 3 * s2 + 1) * vs[i] + (s3 - 2 * s2 + s) * h[i] * m[i] + (-2 * s3 + 3 * s2) * vs[i + 1] + (s3 - s2) * h[i] * m[i + 1];
  };
}

export async function createTour(V, opts = {}) {
  const params = opts.params || new URLSearchParams(location.search);
  const data = await fetch("data/tour.json").then((r) => r.json());
  const { camera, controls, renderer } = V;
  const page = Boolean(opts.page);
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const phone = () => innerWidth <= 760 || matchMedia("(pointer: coarse)").matches;
  let lang = params.get("lang") === "zh" || params.get("lang") === "en" ? params.get("lang") : opts.lang || "en";
  let captions = ["en", "zh", "both", "none"].includes(params.get("captions")) ? params.get("captions") : null; // null: the page's language
  const ui0 = params.get("ui") === "0", dev = params.get("tourdev") === "1";
  const aspect = (() => { const m = /^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$/.exec(params.get("aspect") || ""); return m ? Number(m[1]) / Number(m[2]) : null; })();
  const pinned = params.has("lightq"); // a link's quality is kept, as the probe keeps it

  // ---- poses in world metres, from the models' own frames (models.json position and rotationY) ----
  const frameOf = (at) => {
    if (at === "world" || !V.models[at]) return { x: 0, y: 0, z: 0, r: 0 };
    const c = V.models[at];
    return { x: c.position[0], y: c.position[1], z: c.position[2], r: c.rotationY };
  };
  const groundY = (x, z) => {
    let g = V.wayGroundAt(x, z);
    if (g === null || g === undefined) g = V.groundAt(x, z) ?? 0;
    const w = V.waterLevelAt(x, z);
    return w === null || w === undefined ? g : Math.max(g, w);
  };
  const toWorld = (at, v, g) => {
    const f = frameOf(at), c = Math.cos(f.r), s = Math.sin(f.r);
    const x = f.x + v[0] * c + v[2] * s, z = f.z - v[0] * s + v[2] * c;
    return new THREE.Vector3(x, (g ? groundY(x, z) : f.y) + v[1], z);
  };
  const chapters = data.chapters.map((c) => ({ ...c, eyes: c.poses.map((p) => toWorld(p.at, p.e, p.g)), tgts: c.poses.map((p) => toWorld(p.at, p.t, false)) }));

  // ---- the timeline ----
  let total = 0;
  chapters.forEach((ch, i) => {
    const prev = chapters[i - 1];
    const eyes = [], tgts = [], ts = [];
    const own = ch.poses.map((p, k) => (p.k ?? (ch.poses.length > 1 ? k / (ch.poses.length - 1) : 0)));
    let travel = 0;
    if (prev) {
      const a = prev.eyes[prev.eyes.length - 1], b = ch.eyes[0], dist = a.distanceTo(b);
      // long enough for the distance and for the turn: a look that swings round needs time, or the picture whips (20 degrees a second on average, under 40 at the fastest)
      const da = prev.tgts[prev.tgts.length - 1].clone().sub(a).setY(0).normalize(), db = ch.tgts[0].clone().sub(b).setY(0).normalize();
      const turn = (Math.acos(clamp(da.dot(db), -1, 1)) * 180) / Math.PI;
      travel = ch.travel ?? clamp(Math.max(3 + dist / 170, turn / 20), 3, 12);
      eyes.push(a.clone()); tgts.push(prev.tgts[prev.tgts.length - 1].clone()); ts.push(0);
      if (dist > 500) { // a long flight goes up and over: an aerial pass
        const mid = a.clone().lerp(b, 0.5);
        mid.y = Math.max(a.y, b.y, 80 + 0.22 * dist);
        const mt = prev.tgts[prev.tgts.length - 1].clone().lerp(ch.tgts[0], 0.7);
        eyes.push(mid); tgts.push(mt); ts.push(travel * 0.5);
      }
    }
    const rest = ch.seconds - travel;
    ch.eyes.forEach((e, k) => { eyes.push(e.clone()); tgts.push(ch.tgts[k].clone()); ts.push(travel + own[k] * rest); });
    // the last pose holds a moment while the caption fades, so the chapter ends at rest
    ch.start = total; ch.travel = travel; ch.end = total + ch.seconds; total = ch.end;
    ch.ts = ts;
    ch.eyeCurve = eyes.length > 1 ? new THREE.CatmullRomCurve3(eyes, false, "centripetal") : null;
    ch.tgtCurve = tgts.length > 1 ? new THREE.CatmullRomCurve3(tgts, false, "centripetal") : null;
    ch.eye0 = eyes[0]; ch.tgt0 = tgts[0];
    ch.param = monotone(ts.map((t, k) => (k === ts.length - 1 ? ch.seconds : t)), ts.map((_, k) => k));
    ch.n = eyes.length;
    // during the flight in the look turns by its own easing, yaw and pitch the shortest way, from the last look of the chapter before to the first of this one
    if (travel > 0) {
      const k0 = eyes.length - ch.eyes.length, look = (e, t) => { const d = t.clone().sub(e), l = d.length(); return { yaw: Math.atan2(d.x, -d.z), pitch: Math.asin(d.y / l), dist: l }; };
      ch.lookA = look(eyes[0], tgts[0]); ch.lookB = look(eyes[k0], tgts[k0]);
    }
    ch.hourFrom = prev ? prev.hour : data.start_hour ?? ch.hour;
    ch.hourOver = ch.hour_span === "chapter" || !prev ? ch.seconds : Math.max(travel, 2.5);
  });
  const chapterAt = (t) => { for (let i = 0; i < chapters.length; i++) if (t < chapters[i].end) return i; return chapters.length - 1; };

  // ---- the camera at a time, clamped clear of the ground and the halls ----
  const boxes = V.halls.info.filter((b) => !b.hidden && b.y1 > b.y0);
  const CELL = 40, grid = new Map();
  for (const b of boxes) {
    const r = Math.hypot(b.hf, b.hd) + BOX_CLEAR_M;
    for (let gx = Math.floor((b.cx - r) / CELL); gx <= Math.floor((b.cx + r) / CELL); gx++) for (let gz = Math.floor((b.cz - r) / CELL); gz <= Math.floor((b.cz + r) / CELL); gz++) {
      const k = gx * 100003 + gz;
      if (!grid.has(k)) grid.set(k, []);
      grid.get(k).push(b);
    }
  }
  const nearBoxes = (x, z) => grid.get(Math.floor(x / CELL) * 100003 + Math.floor(z / CELL)) || [];
  // signed distance from a point to a box (inside: negative), and the way out
  const boxDist = (p, b) => {
    const px = p.x - b.cx, pz = p.z - b.cz, u = px * b.u[0] + pz * b.u[1], a = px * b.a[0] + pz * b.a[1];
    const du = Math.abs(u) - b.hf, da = Math.abs(a) - b.hd, dy = Math.max(b.y0 - p.y, p.y - b.y1);
    const out = Math.hypot(Math.max(du, 0), Math.max(da, 0), Math.max(dy, 0));
    return out > 0 ? out : Math.max(du, da, dy);
  };
  let clamps = 0;
  const clampEye = (p) => {
    let moved = false;
    for (const b of nearBoxes(p.x, p.z)) {
      const px = p.x - b.cx, pz = p.z - b.cz, u = px * b.u[0] + pz * b.u[1], a = px * b.a[0] + pz * b.a[1];
      const pu = b.hf + BOX_CLEAR_M - Math.abs(u), pa = b.hd + BOX_CLEAR_M - Math.abs(a), py = b.y1 + BOX_CLEAR_M - p.y;
      if (pu <= 0 || pa <= 0 || py <= 0 || p.y < b.y0 - BOX_CLEAR_M) continue;
      moved = true;
      if (py <= pu && py <= pa) p.y += py; // over the roof is the shortest way out
      else if (pu < pa) { const s = Math.sign(u) || 1; p.x += b.u[0] * pu * s; p.z += b.u[1] * pu * s; }
      else { const s = Math.sign(a) || 1; p.x += b.a[0] * pa * s; p.z += b.a[1] * pa * s; }
    }
    const g = groundY(p.x, p.z) + EYE_CLEAR_M;
    if (p.y < g) { p.y = g; moved = true; }
    return moved;
  };
  const eyeAt = new THREE.Vector3(), tgtAt = new THREE.Vector3();
  const poseAt = (t, eye = eyeAt, tgt = tgtAt, count = false) => {
    t = clamp(t, 0, total - 1e-6);
    const ch = chapters[chapterAt(t)], lt = t - ch.start;
    if (!ch.eyeCurve) { eye.copy(ch.eye0); tgt.copy(ch.tgt0); }
    else { const s = clamp(ch.param(lt) / (ch.n - 1), 0, 1); ch.eyeCurve.getPoint(s, eye); ch.tgtCurve.getPoint(s, tgt); }
    if (ch.lookA && lt < ch.travel) {
      const k = smoother(lt / ch.travel), A = ch.lookA, B = ch.lookB;
      let dy = B.yaw - A.yaw;
      dy -= Math.round(dy / (2 * Math.PI)) * 2 * Math.PI;
      const yaw = A.yaw + dy * k, pitch = lerp(A.pitch, B.pitch, k), d = lerp(A.dist, B.dist, k);
      tgt.set(eye.x + Math.sin(yaw) * Math.cos(pitch) * d, eye.y + Math.sin(pitch) * d, eye.z - Math.cos(yaw) * Math.cos(pitch) * d);
    }
    const clamped = clampEye(eye);
    if (clamped && count) clamps++;
    return { eye, tgt, i: chapters.indexOf(ch), lt, clamped };
  };
  const hourAt = (t) => {
    t = clamp(t, 0, total - 1e-6);
    const ch = chapters[chapterAt(t)], lt = t - ch.start;
    return lerp(ch.hourFrom, ch.hour, smoother(lt / ch.hourOver));
  };

  // ---- state ----
  let tt = 0, playing = false, speed = SPEEDS.includes(Number(params.get("speed"))) ? Number(params.get("speed")) : reducedMotion ? 0.75 : 1;
  let raf = 0, last = 0, curIndex = -1, manual = null, blend = null, waiting = false, ended = false, alive = true, userPaused = false;
  let lastHour = -1, stepsThisChapter = 0, adaptLog = [], frameLog = [], cinema = ui0, startCard = null, startPaused = false;
  const first = params.get("ch") || opts.chapter;
  const firstIndex = Math.max(0, chapters.findIndex((c) => c.id === first));

  // ---- the chrome ----
  const css = document.createElement("style");
  css.textContent = `
  @font-face { font-family: 'Newsreader'; src: url('/assets/fonts/newsreader-latin.woff2') format('woff2'); font-style: italic; font-weight: 200 800; font-display: swap; unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
  @font-face { font-family: 'Newsreader'; src: url('/assets/fonts/newsreader-latin-ext.woff2') format('woff2'); font-style: italic; font-weight: 200 800; font-display: swap; unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF; }
  @font-face { font-family: 'Noto Serif SC'; src: url('/assets/fonts/noto-serif-sc-subset.woff2') format('woff2'); font-weight: 500; font-display: swap; }
  @font-face { font-family: 'Noto Serif SC Tour'; src: url('/assets/fonts/noto-serif-sc-tour.woff2') format('woff2'); font-weight: 500; font-display: swap; } /* tools/font_subset.py tour: what the subset lacks */
  #tour { position: fixed; inset: 0; z-index: 1200; pointer-events: none; font: 13px/1.4 'Geist', system-ui, sans-serif; color: #F5EEE2; }
  #tour button { pointer-events: auto; font: inherit; color: inherit; cursor: pointer; }
  #tour .t-frame { position: absolute; }
  #tour .t-title { position: absolute; top: 18px; left: 20px; display: flex; gap: 10px; align-items: center; text-shadow: 0 1px 8px #0008; }
  #tour .t-title img { width: 34px; height: 34px; flex: none; }
  #tour .t-name { font: 600 13px 'Geist Mono', ui-monospace, monospace; letter-spacing: .32em; text-transform: uppercase; }
  #tour .t-name [lang] { font: 500 16px 'Noto Serif SC', 'Noto Serif SC Tour', 'Songti SC', 'STSong', serif; letter-spacing: .18em; margin-right: .5em; }
  #tour .t-sub { font: italic 15px 'Newsreader', Georgia, serif; color: #EDE3D2; letter-spacing: .01em; }
  #tour .t-card { position: absolute; top: 74px; left: 20px; width: min(440px, calc(100% - 40px)); box-sizing: border-box; padding: 12px 16px 12px; border-radius: 10px; background: #17130Fb8; -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); box-shadow: 0 6px 24px #0004; opacity: 0; transform: translateY(4px); transition: opacity .8s ease, transform .8s ease; }
  #tour .t-card.on { opacity: 1; transform: none; transition: opacity .6s ease, transform .6s ease; }
  #tour .t-head { font: 600 11px 'Geist Mono', ui-monospace, monospace; letter-spacing: .14em; text-transform: uppercase; color: #E9C9A0; font-variant: small-caps; }
  #tour .t-head [lang] { font: 500 15px 'Noto Serif SC', 'Noto Serif SC Tour', 'Songti SC', 'STSong', serif; letter-spacing: .08em; text-transform: none; color: #F5EEE2; margin-right: .45em; }
  #tour .t-text { margin: 6px 0 0; font: italic 17.5px/1.42 'Newsreader', Georgia, 'Noto Serif SC', 'Noto Serif SC Tour', 'Songti SC', serif; color: #F7F1E6; }
  #tour .t-text.zh, #tour .t-text :lang(zh) { font-family: 'Noto Serif SC', 'Noto Serif SC Tour', 'Songti SC', 'STSong', 'Newsreader', serif; font-style: normal; }
  #tour .t-text.zh { font-size: 15.5px; line-height: 1.6; }
  #tour .t-text + .t-text { margin-top: 4px; }
  #tour .t-meta { display: flex; flex-wrap: wrap; gap: 6px 8px; align-items: center; margin-top: 8px; font-size: 11.5px; color: #D9CDBB; }
  #tour .t-grade { padding: 1px 6px; border-radius: 3px; font: 600 10.5px 'Geist Mono', ui-monospace, monospace; letter-spacing: .06em; color: #fff; }
  #tour .t-grade.A { background: #2f7d4a; } #tour .t-grade.B { background: #9b7424; } #tour .t-grade.C { background: #a2402a; }
  #tour .t-note { width: 100%; font-style: italic; color: #E9DCC8; }
  #tour .t-bottom { position: absolute; left: 0; right: 0; bottom: 0; padding: 0 14px 12px; background: linear-gradient(#0000, #0007); pointer-events: none; }
  #tour .t-progress { height: 3px; margin: 0 6px 10px; background: #F5EEE233; border-radius: 2px; overflow: hidden; }
  #tour .t-progress i { display: block; height: 100%; width: 0; background: #E9C9A0; }
  #tour .t-row { display: flex; align-items: center; gap: 8px; }
  #tour .t-chips { display: flex; gap: 6px; overflow-x: auto; scrollbar-width: none; flex: 1 1 auto; min-width: 0; pointer-events: auto; padding: 2px; -webkit-overflow-scrolling: touch; }
  #tour .t-chips::-webkit-scrollbar { display: none; }
  #tour .chip { flex: none; min-height: 30px; padding: 0 11px; border: 1px solid #F5EEE266; border-radius: 15px; background: #17130F80; font: 11px 'Geist Mono', ui-monospace, 'Noto Serif SC', 'Noto Serif SC Tour', monospace !important; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }
  #tour .chip:hover { border-color: #F5EEE2; }
  #tour .chip[aria-current="true"], #tour .chip[aria-pressed="true"] { background: #F5EEE2; color: #17130F !important; border-color: #F5EEE2; }
  #tour .t-div { flex: none; width: 1px; height: 22px; background: #F5EEE255; }
  #tour .t-ctl { display: flex; gap: 6px; flex: none; pointer-events: auto; }
  #tour .btn { min-width: 32px; min-height: 32px; padding: 0 9px; border: 1px solid #F5EEE266; border-radius: 16px; background: #17130F99; font: 11px 'Geist Mono', ui-monospace, 'Noto Serif SC', 'Noto Serif SC Tour', monospace !important; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }
  #tour .btn:hover { border-color: #F5EEE2; }
  #tour button:focus-visible { outline: 2px solid #E9C9A0; outline-offset: 2px; }
  #tour .t-top { position: absolute; top: 16px; right: 16px; display: flex; gap: 6px; pointer-events: auto; }
  #tour .t-resume { position: absolute; left: 50%; bottom: 96px; transform: translateX(-50%); padding: 9px 18px; border: 0; border-radius: 20px; background: #F5EEE2; color: #17130F !important; font: 600 12px 'Geist Mono', ui-monospace, monospace !important; letter-spacing: .08em; text-transform: uppercase; box-shadow: 0 4px 16px #0005; }
  #tour .t-wait { position: absolute; left: 0; right: 0; top: 0; height: 2px; overflow: hidden; }
  #tour .t-wait i { position: absolute; top: 0; height: 100%; width: 30%; background: #E9C9A0; animation: tourwait 1.4s linear infinite; }
  @keyframes tourwait { from { left: -30%; } to { left: 100%; } }
  #tour .t-wait span { position: absolute; top: 8px; left: 50%; transform: translateX(-50%); padding: 3px 10px; border-radius: 10px; background: #17130Fb0; font-size: 11.5px; white-space: nowrap; }
  #tour .t-veil { position: absolute; inset: 0; background: #000; opacity: 0; transition: opacity .35s; }
  #tour .t-veil.on { opacity: 1; }
  #tour .t-cardbox { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 16px; background: #0b0a0899; pointer-events: auto; opacity: 0; transition: opacity .8s; }
  #tour .t-cardbox.on { opacity: 1; }
  #tour .t-cardbox.start { background: none; pointer-events: none; }
  #tour .t-big { width: min(560px, 100%); box-sizing: border-box; padding: 22px 24px; border-radius: 12px; background: #17130Fd9; text-align: left; box-shadow: 0 10px 40px #0006; }
  #tour .t-big h2 { margin: 0 0 8px; font: 500 24px 'Noto Serif SC', 'Noto Serif SC Tour', 'Newsreader', serif; letter-spacing: .04em; }
  #tour .t-big p { margin: 8px 0; font: italic 17px/1.5 'Newsreader', Georgia, 'Noto Serif SC', 'Noto Serif SC Tour', serif; color: #F1E8D9; }
  #tour .t-big .t-label { font: 12.5px/1.45 'Geist', system-ui, sans-serif; color: #D9CDBB; }
  #tour .t-big .t-acts { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
  #tour .t-big a { color: #F0C79A; }
  #tour .t-big .btn.main { background: #F5EEE2; color: #17130F !important; border-color: #F5EEE2; }
  #tour .t-pop { position: absolute; right: 16px; top: 56px; width: min(340px, calc(100% - 32px)); padding: 12px 14px; border-radius: 8px; background: #17130Fe6; font-size: 12.5px; line-height: 1.5; pointer-events: auto; }
  #tour .t-toast { position: absolute; left: 50%; top: 18px; transform: translateX(-50%); padding: 5px 12px; border-radius: 12px; background: #F5EEE2; color: #17130F; font-size: 12px; }
  #tour [hidden] { display: none !important; }
  #tour .t-dev { position: absolute; right: 12px; bottom: 120px; width: 360px; padding: 8px; border-radius: 6px; background: #fffdf8f2; color: #222; font: 11px ui-monospace, monospace; pointer-events: auto; }
  #tour .t-dev textarea { width: 100%; height: 110px; font: 10.5px ui-monospace, monospace; }
  #tour .t-dev button { color: #222 !important; border: 1px solid #888; border-radius: 3px; background: #fff; margin: 2px 4px 2px 0; }
  #tour.cinema .t-bottom, #tour.cinema .t-top, #tour.cinema .t-resume, #tour.cinema .t-pop { display: none !important; }
  #tour .t-cine { position: absolute; right: 16px; top: 16px; display: none; pointer-events: none; opacity: 0; transition: opacity .4s; }
  #tour.cinema:not(.ui0) .t-cine { display: block; }
  #tour.cinema.stir .t-cine { opacity: 1; pointer-events: auto; }
  body.tour-idle, body.tour-idle canvas { cursor: none !important; }
  body.guided { background: #000; }
  body.guided canvas { position: fixed; }
  @media (max-width: 760px) {
    #tour .t-title { top: 12px; left: 12px; } #tour .t-title img { width: 28px; height: 28px; }
    #tour .t-name { font-size: 11px; letter-spacing: .22em; } #tour .t-sub { font-size: 13px; }
    #tour .t-card { top: 58px; left: 10px; width: calc(100% - 20px); padding: 9px 12px; }
    #tour .t-text { font-size: 15px; } #tour .t-text.zh { font-size: 14px; }
    #tour .t-top { top: auto; bottom: 118px; left: 10px; right: 10px; overflow-x: auto; scrollbar-width: none; justify-content: flex-end; }
    #tour .t-top::-webkit-scrollbar { display: none; } #tour .t-top .btn { flex: none; }
    #tour .t-top [data-act="fullscreen"], #tour .t-top [data-act="cinema"] { display: none; } /* a phone records in portrait with its own screen recorder; most phones have no page full screen */
    #tour .t-bottom { padding: 0 8px 10px; } #tour .t-row.light { margin-top: 6px; }
    #tour .t-resume { bottom: 140px; }
  }
  @media (min-width: 2400px) { #tour { font-size: 16px; } #tour .t-card { width: 560px; } #tour .t-text { font-size: 22px; } #tour .t-text.zh { font-size: 20px; } #tour .t-name { font-size: 16px; } #tour .t-sub { font-size: 19px; } #tour .chip, #tour .btn { font-size: 13px !important; min-height: 38px; } }
  `;
  document.head.append(css);
  const root = document.createElement("div");
  root.id = "tour";
  root.setAttribute("role", "region");
  const homeHref = lang === "zh" ? "../zh/" : "../";
  root.innerHTML = `
    <div class="t-frame">
      <div class="t-title"><img src="../assets/mark.svg" alt=""><div><div class="t-name"><span lang="zh-Hans">圆明园</span><span class="t-en">Yuanmingyuan</span></div><div class="t-sub"></div></div></div>
      <div class="t-card" aria-live="polite"><div class="t-head"></div><div class="t-texts"></div><div class="t-meta"></div></div>
      <div class="t-wait" hidden><i></i><span></span></div>
      <div class="t-top">
        <button type="button" class="btn" data-act="lang"></button>
        <button type="button" class="btn" data-act="help" aria-expanded="false"></button>
        <button type="button" class="btn" data-act="cinema"></button>
        <button type="button" class="btn" data-act="fullscreen"></button>
        <button type="button" class="btn" data-act="share"></button>
        <button type="button" class="btn" data-act="explore"></button>
      </div>
      <div class="t-pop" hidden></div>
      <button type="button" class="t-resume" data-act="resume" hidden></button>
      <div class="t-bottom">
        <div class="t-progress" aria-hidden="true"><i></i></div>
        <div class="t-row">
          <div class="t-ctl">
            <button type="button" class="btn" data-act="prev" aria-label="">◀</button>
            <button type="button" class="btn" data-act="play" aria-label=""></button>
            <button type="button" class="btn" data-act="next" aria-label="">▶</button>
            <button type="button" class="btn" data-act="speed"></button>
            <button type="button" class="btn" data-act="free"></button>
          </div>
          <div class="t-div"></div>
          <div class="t-chips t-chapters" role="group"></div>
        </div>
        <div class="t-row light"><div class="t-chips t-lights" role="group"></div></div>
      </div>
      <button type="button" class="btn t-cine" data-act="cinema"></button>
      <div class="t-cardbox start" hidden><div class="t-big"></div></div>
      <div class="t-cardbox end" hidden><div class="t-big"></div></div>
      <div class="t-toast" hidden></div>
      <div class="t-veil"></div>
    </div>`;
  document.body.append(root);
  const $ = (s) => root.querySelector(s);
  const frameEl = $(".t-frame");
  const chapterChips = chapters.map((ch, i) => { const b = document.createElement("button"); b.type = "button"; b.className = "chip"; b.dataset.ch = String(i); $(".t-chapters").append(b); return b; });
  const lightChips = data.light_chips.map((l) => { const b = document.createElement("button"); b.type = "button"; b.className = "chip"; b.dataset.hour = String(l.hour); b.dataset.light = l.id; $(".t-lights").append(b); return b; });
  let devBox = null;

  const showCaptionsIn = () => captions || lang;
  function paintChrome() {
    const L = T[lang];
    root.setAttribute("aria-label", lang === "zh" ? "圆明园导览" : "A guided tour of Yuanmingyuan");
    $(".t-en").textContent = lang === "zh" ? "" : L.title;
    $(".t-sub").textContent = L.sub;
    const set = (act, text, label) => root.querySelectorAll(`[data-act="${act}"]`).forEach((b) => { b.textContent = text; if (label) b.setAttribute("aria-label", label); else b.removeAttribute("aria-label"); });
    set("lang", L.lang, lang === "zh" ? "English" : "中文");
    set("help", L.help); set("cinema", cinema ? L.cinemaExit : L.cinema); set("fullscreen", L.fullscreen); set("share", L.share);
    set("explore", page ? L.explore : L.exit); set("resume", startPaused ? `▶ ${L.play}` : L.resume); set("free", L.free);
    set("prev", "◀", L.prev); set("next", "▶", L.next);
    set("play", playing ? "❚❚" : "▶", playing ? L.pause : L.play);
    set("speed", `${speed}×`, `${L.speed} ${speed}×`);
    $(".t-chapters").setAttribute("aria-label", L.chapters);
    $(".t-lights").setAttribute("aria-label", L.light);
    chapterChips.forEach((b, i) => { b.textContent = chapters[i].chip[lang]; b.setAttribute("aria-current", String(i === curIndex)); });
    lightChips.forEach((b, i) => { b.textContent = data.light_chips[i][lang]; b.setAttribute("aria-pressed", String(manual?.id === data.light_chips[i].id)); });
    $(".t-pop").innerHTML = `<p style="margin:0 0 6px">${L.helpText}</p><p style="margin:0;color:#D9CDBB">${L.keys}</p>`;
    $(".t-wait span").textContent = L.loading;
    if (curIndex >= 0) paintCaption(curIndex);
    if (ended) paintEnd();
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const zhWrap = (s) => esc(s).replace(/([㐀-鿿　-〿＀-￯]+)/g, '<span lang="zh-Hans">$1</span>');
  function paintCaption(i) {
    const ch = chapters[i], L = T[lang], mode = showCaptionsIn();
    $(".t-head").innerHTML = `<span lang="zh-Hans">${esc(ch.title.zh)}</span>${lang === "zh" && mode === "zh" ? "" : esc(ch.title.en)}`;
    const texts = [];
    if (mode === "en" || mode === "both") texts.push(`<p class="t-text">${zhWrap(ch.text.en)}</p>`);
    if (mode === "zh" || mode === "both") texts.push(`<p class="t-text zh" lang="zh-Hans">${esc(ch.text.zh)}</p>`);
    $(".t-texts").innerHTML = texts.join("");
    const bl = mode === "zh" ? "zh" : "en";
    $(".t-meta").innerHTML = `<span class="t-grade ${esc(ch.grade)}" title="${esc(L.grade)}">${esc(L.grade)} ${esc(ch.grade)}</span><span>${zhWrap(ch.basis[bl])}</span>${ch.note ? `<span class="t-note">${zhWrap(ch.note[bl])}</span>` : ""}`;
    $(".t-card").hidden = mode === "none";
  }
  function paintStart() {
    const L = T[lang];
    $(".t-cardbox.start .t-big").innerHTML = `<h2><span lang="zh-Hans">圆明园</span> ${lang === "zh" ? "" : "Yuanmingyuan"}</h2><p>${esc(L.startLine)}</p><p class="t-label">${esc(L.label)}</p>`;
  }
  function paintEnd() {
    const L = T[lang];
    $(".t-cardbox.end .t-big").innerHTML = `<h2>${esc(L.endHead)}</h2><p>${zhWrap(L.end)}</p><p class="t-label">${esc(L.label)}</p>
      <div class="t-acts"><button type="button" class="btn main" data-act="again">${esc(L.again)}</button><button type="button" class="btn" data-act="gardens">${esc(L.gardens)}</button></div>
      <p class="t-label" style="margin-top:12px"><a href="../credits.html">${esc(L.credits)}</a> · <a href="${homeHref}">${esc(L.home)}</a></p>`;
  }

  // ---- the letterbox and the portrait field of view ----
  const frameRect = () => {
    const W = innerWidth, H = innerHeight;
    if (!aspect) return [W, H, 0, 0];
    let w = W, h = Math.round(W / aspect);
    if (h > H) { h = H; w = Math.round(H * aspect); }
    return [w, h, Math.round((W - w) / 2), Math.round((H - h) / 2)];
  };
  const fitFrame = () => {
    const [w, h, x, y] = frameRect();
    Object.assign(frameEl.style, { left: `${x}px`, top: `${y}px`, width: `${w}px`, height: `${h}px` });
    Object.assign(renderer.domElement.style, { left: `${x}px`, top: `${y}px` });
    const a = w / h, fov = a >= 1 ? BASE_FOV : clamp((2 * Math.atan(Math.tan((PORTRAIT_MIN_HFOV * Math.PI) / 360) / a) * 180) / Math.PI, BASE_FOV, MAX_FOV);
    if (Math.abs(camera.fov - fov) > 0.01) { camera.fov = fov; camera.updateProjectionMatrix(); }
    root.classList.toggle("narrow", w <= 760);
  };
  const sizer = () => { const [w, h] = frameRect(); return [w, h]; };

  // ---- light ----
  const setHourNow = (h) => {
    const b = V.beauty;
    if (!b || !b.on || Math.abs(h - lastHour) < 0.002) return;
    lastHour = h;
    b.stepHour(h);
  };
  const currentHour = (now) => {
    const h = hourAt(tt);
    if (!manual) return h;
    const k = smoother((now - manual.t0) / (MANUAL_EASE_S * 1000));
    return lerp(manual.from, manual.hour, k);
  };

  // ---- the frame ----
  const look = (eye, tgt) => {
    camera.position.copy(eye);
    controls.target.copy(tgt);
    camera.lookAt(tgt);
  };
  const ahead = new THREE.Object3D(), aheadEye = new THREE.Vector3(), aheadTgt = new THREE.Vector3();
  let frameNo = 0;
  const draw = (now) => {
    const P = poseAt(tt, eyeAt, tgtAt, playing);
    if (userPaused && !playing) { setHourNow(currentHour(now)); V.render(); return; } // the visitor holds the camera: only the light moves
    if (blend) {
      const k = smoother((now - blend.t0) / (RESUME_S * 1000));
      P.eye.lerpVectors(blend.eye, P.eye, k); P.tgt.lerpVectors(blend.tgt, P.tgt, k);
      if (k >= 1) blend = null;
    }
    look(P.eye, P.tgt);
    setHourNow(currentHour(now));
    if (P.i !== curIndex) enterChapter(P.i);
    const lt = P.lt, ch = chapters[P.i];
    const capIn = startCard !== null && P.i === 0 ? 7 : CAPTION_IN_S; // the start card first
    $(".t-card").classList.toggle("on", lt >= capIn && lt <= ch.seconds - CAPTION_OUT_S && !ended);
    $(".t-progress i").style.width = `${((tt / total) * 100).toFixed(2)}%`;
    if (startCard !== null) { const on = tt < 6.5 && !ended; $(".t-cardbox.start").classList.toggle("on", on); if (!on && tt > 7.5) { $(".t-cardbox.start").hidden = true; startCard = null; } }
    V.render();
    // the kit's near detail a few seconds ahead of the camera, one tile now and then, so it is there when the camera arrives
    if (++frameNo % 3 === 0 && V.kit?.update) { poseAt(tt + 4 * speed, aheadEye, aheadTgt); ahead.position.copy(aheadEye); ahead.updateMatrixWorld(); V.kit.update(ahead, 1); }
  };
  const enterChapter = (i) => {
    const prev = curIndex;
    curIndex = i;
    manual = null;
    stepsThisChapter = 0;
    paintCaption(i);
    chapterChips.forEach((b, k) => b.setAttribute("aria-current", String(k === i)));
    lightChips.forEach((b) => b.setAttribute("aria-pressed", "false"));
    chapterChips[i].scrollIntoView({ block: "nearest", inline: "center", behavior: reducedMotion ? "auto" : "smooth" });
    if (pendingStep && prev !== i) { pendingStep(); pendingStep = null; }
  };
  const chapterReady = (i) => (chapters[i].models || []).every((id) => V.detailed[id]) && (i === 0 || window.__modelsReady === true);
  const tick = (now) => {
    raf = 0;
    if (!alive) return;
    const dt = clamp((now - last) / 1000, 0, 1); // the clock is wall-clock time (a slow machine drops frames, not seconds); a stall longer than a second is not a leap; a hidden tab restarts the count (onShow); a frame's timestamp may come before the loop's start
    last = now;
    if (playing && !ended) {
      let next = tt + dt * speed;
      const ni = chapterAt(next);
      waiting = !chapterReady(ni);
      if (waiting) next = tt; // hold: the end of the chapter before is at rest
      $(".t-wait").hidden = !waiting;
      tt = next;
      if (tt >= total - 1e-3) { tt = total - 1e-3; finish(); }
    }
    draw(now);
    adapt(now, dt);
    if (playing || blend || manual) raf = requestAnimationFrame(tick);
  };
  const loop = () => { if (!raf && alive) { last = performance.now(); raf = requestAnimationFrame(tick); } };

  // ---- quality: start where the probe left it (the lowest on a phone), one step down at most a chapter, never up ----
  const LADDER = ["high", "mid", "low", "min"];
  let pendingStep = null;
  const stepDown = (why) => {
    const b = V.beauty, q = b?.quality, i = LADDER.indexOf(q);
    const was = { q, ratio: renderer.getPixelRatio() };
    if (b && i >= 0 && i < LADDER.length - 1) b.setQuality(LADDER[i + 1]);
    else if (renderer.getPixelRatio() > 1) { renderer.setPixelRatio(1); V.resize(); }
    else return false;
    adaptLog.push({ t: +tt.toFixed(1), chapter: chapters[curIndex]?.id, from: was, to: { q: V.beauty?.quality, ratio: renderer.getPixelRatio() }, why });
    return true;
  };
  let windowStart = 0, windowFrames = [];
  const adapt = (now, dt) => {
    if (!playing || waiting) { windowFrames = []; windowStart = now; return; }
    windowFrames.push(dt * 1000);
    frameLog.push({ i: curIndex, ms: dt * 1000 });
    if (now - windowStart < ADAPT_WINDOW_S * 1000) return;
    const sorted = windowFrames.slice().sort((a, b) => a - b), med = sorted[Math.floor(sorted.length / 2)] || 0;
    windowFrames = []; windowStart = now;
    if (pinned || stepsThisChapter > 0 || med <= FRAME_BUDGET_MS) return;
    stepsThisChapter++;
    // a frame far too slow steps now; a little too slow waits for the next chapter, so the look does not change mid-shot
    if (med > 2 * FRAME_BUDGET_MS) stepDown(`median ${med.toFixed(0)} ms`);
    else pendingStep = () => stepDown(`median ${med.toFixed(0)} ms`);
  };

  // ---- controls ----
  const play = () => {
    if (ended) return;
    if (userPaused) { blend = { eye: camera.position.clone(), tgt: controls.target.clone(), t0: performance.now() }; userPaused = false; }
    startPaused = false;
    playing = true;
    $(".t-resume").hidden = true;
    if (V.beauty) V.beauty.cycling = true;
    paintChrome();
    loop();
  };
  const pause = (byUser = false) => {
    playing = false;
    if (V.beauty) V.beauty.cycling = false; // the light takes its exact place, shadows too
    if (byUser) { userPaused = true; $(".t-resume").hidden = cinema; }
    paintChrome();
    V.render();
  };
  const veil = (fn) => {
    const v = $(".t-veil");
    if (reducedMotion) { fn(); return; }
    v.classList.add("on");
    setTimeout(() => { fn(); requestAnimationFrame(() => v.classList.remove("on")); }, 360);
  };
  const seekChapter = (i, fade = true) => {
    i = clamp(i, 0, chapters.length - 1);
    const go = () => {
      tt = chapters[i].start + chapters[i].travel; // its own first pose: the flight in is skipped
      blend = null; ended = false; userPaused = false;
      $(".t-cardbox.end").hidden = true;
      $(".t-resume").hidden = true;
      const keepPaused = !playing && reducedMotion;
      draw(performance.now());
      if (keepPaused) loop(); else play();
    };
    if (fade) veil(go); else go();
  };
  const finish = () => {
    ended = true;
    playing = false;
    if (V.beauty) V.beauty.cycling = false;
    paintEnd();
    const box = $(".t-cardbox.end");
    box.hidden = false;
    requestAnimationFrame(() => box.classList.add("on"));
    paintChrome();
  };
  const again = () => {
    $(".t-cardbox.end").classList.remove("on");
    $(".t-cardbox.end").hidden = true;
    ended = false;
    veil(() => { tt = 0; curIndex = -1; startCard = 1; $(".t-cardbox.start").hidden = false; paintStart(); draw(performance.now()); play(); });
  };
  const toast = (text) => { const t = $(".t-toast"); t.textContent = text; t.hidden = false; clearTimeout(toast.id); toast.id = setTimeout(() => { t.hidden = true; }, 1800); };
  const shareUrl = () => {
    const id = chapters[curIndex]?.id || chapters[0].id;
    const u = new URL(location.href);
    for (const k of [...u.searchParams.keys()]) if (!["tour", "lang"].includes(k)) u.searchParams.delete(k);
    if (!page) u.searchParams.set("tour", "1");
    u.searchParams.set("ch", id);
    return u.toString();
  };
  const share = async () => {
    const url = shareUrl();
    try { await navigator.clipboard.writeText(url); toast(T[lang].copied); } catch { prompt(T[lang].share, url); }
  };
  const setCinema = (on) => {
    cinema = on;
    root.classList.toggle("cinema", on);
    if (on) $(".t-pop").hidden = true;
    $(".t-resume").hidden = on || !userPaused;
    paintChrome();
  };
  const fullscreen = () => { const d = document; if (d.fullscreenElement) d.exitFullscreen?.(); else d.documentElement.requestFullscreen?.().catch(() => {}); };
  const exit = (explore = true) => {
    alive = false;
    cancelAnimationFrame(raf);
    if (V.beauty) V.beauty.cycling = false;
    removeEventListener("keydown", onKey, true);
    removeEventListener("resize", fitFrame);
    controls.removeEventListener("start", onControlStart);
    removeEventListener("pointerdown", onDown, true);
    removeEventListener("pointerup", onUp);
    removeEventListener("pointermove", onStir);
    document.removeEventListener("visibilitychange", onShow);
    clearTimeout(idleId);
    document.body.classList.remove("guided", "tour-idle", "tour-page");
    root.remove(); css.remove(); devBox?.remove();
    renderer.domElement.style.left = renderer.domElement.style.top = "";
    camera.fov = BASE_FOV;
    camera.updateProjectionMatrix();
    V.setSizer(null);
    V.setGuided(false);
    // the view turns round its target: it must lie below the eye (OrbitControls keeps the camera above its horizon)
    const tgt = controls.target;
    if (tgt.y > camera.position.y - 0.5) tgt.y = camera.position.y - 0.5;
    controls.update();
    const c = [...camera.position.toArray(), ...controls.target.toArray()].map((v) => v.toFixed(1)).join(",");
    if (explore) {
      history.replaceState(null, "", `3d.html?cam=${c}`);
      document.title = "3D view · 圆明园 Yuanmingyuan before 1860";
    } else {
      const u = new URL(location.href);
      for (const k of ["tour", "ch", "ui", "captions", "aspect", "fs", "poster", "tourdev", "speed"]) u.searchParams.delete(k);
      history.replaceState(null, "", u);
    }
    V.render();
    window.__tour = null;
    opts.onExit?.();
  };

  const act = (name, el) => {
    if (name === "play") return playing ? pause(true) : play();
    if (name === "resume") { userPaused = userPaused && !startPaused; return play(); }
    if (name === "prev") return seekChapter(curIndex - (chapters[curIndex] && tt - chapters[curIndex].start - chapters[curIndex].travel > 2 ? 0 : 1));
    if (name === "next") return seekChapter(curIndex + 1);
    if (name === "speed") { speed = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length]; return paintChrome(); }
    if (name === "free") return pause(true);
    if (name === "lang") { lang = lang === "zh" ? "en" : "zh"; if (captions === "en" || captions === "zh") captions = lang; return paintChrome(); }
    if (name === "help") { const p = $(".t-pop"); p.hidden = !p.hidden; el.setAttribute("aria-expanded", String(!p.hidden)); return; }
    if (name === "cinema") return setCinema(!cinema);
    if (name === "fullscreen") return fullscreen();
    if (name === "share") return share();
    if (name === "explore" || name === "gardens") return exit(true);
    if (name === "again") return again();
  };
  root.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.act) act(b.dataset.act, b);
    else if (b.dataset.ch) seekChapter(Number(b.dataset.ch));
    else if (b.dataset.hour) {
      manual = { id: b.dataset.light, hour: Number(b.dataset.hour), from: currentHour(performance.now()), t0: performance.now() };
      lightChips.forEach((c) => c.setAttribute("aria-pressed", String(c === b)));
      V.beauty?.nightReady();
      loop();
    }
  });
  const onKey = (e) => {
    if (e.target.closest?.("input, textarea, select")) return;
    if (e.code === "Space") { e.preventDefault(); e.stopImmediatePropagation(); if (ended) return; playing ? pause(true) : play(); }
    else if (e.code === "ArrowRight") { e.preventDefault(); e.stopImmediatePropagation(); act("next"); }
    else if (e.code === "ArrowLeft") { e.preventDefault(); e.stopImmediatePropagation(); act("prev"); }
    else if (e.key === "Escape") { if (cinema && !ui0) { setCinema(false); e.stopImmediatePropagation(); } else if (!$(".t-pop").hidden) $(".t-pop").hidden = true; else if (!page) exit(false); }
    else if (e.key === "c" || e.key === "C") setCinema(!cinema);
  };
  addEventListener("keydown", onKey, true);
  // A press on the view: a tap plays or pauses, a drag or the wheel looks round (OrbitControls) and pauses, a quick swipe up or down on a touch screen is the next or the previous chapter.
  let press = null;
  const onControlStart = () => { if (playing) pause(true); };
  controls.addEventListener("start", onControlStart);
  const onDown = (e) => { if (e.target !== renderer.domElement) return; press = { x: e.clientX, y: e.clientY, t: e.timeStamp, wasPlaying: playing, touch: e.pointerType !== "mouse" }; if (params.get("fs") === "1" && !document.fullscreenElement) fullscreen(); };
  const onUp = (e) => {
    if (!press) return;
    const dx = e.clientX - press.x, dy = e.clientY - press.y, ms = e.timeStamp - press.t, p = press; // the events' own times: a busy page handles them late
    press = null;
    if (ended) return;
    if (p.touch && ms < 600 && Math.abs(dy) > 50 && Math.abs(dy) > 1.5 * Math.abs(dx)) { userPaused = false; seekChapter(curIndex + (dy < 0 ? 1 : -1)); return; }
    if (Math.hypot(dx, dy) < 6 && ms < 400) { if (p.wasPlaying) pause(true); else play(); }
  };
  addEventListener("pointerdown", onDown, true); // before OrbitControls, whose start pauses the tour
  addEventListener("pointerup", onUp);
  // ui=0 and cinema: the cursor hides after 2 s still; a move shows it, and in cinema the button to leave it
  let idleId = 0;
  const onStir = () => {
    document.body.classList.remove("tour-idle");
    root.classList.add("stir");
    clearTimeout(idleId);
    idleId = setTimeout(() => { root.classList.remove("stir"); if (cinema) document.body.classList.add("tour-idle"); }, 2000);
  };
  addEventListener("pointermove", onStir);
  const onShow = () => { if (!document.hidden) last = performance.now(); }; // back from a hidden tab: the clock goes on from here, no leap
  document.addEventListener("visibilitychange", onShow);
  addEventListener("resize", fitFrame);

  // ---- the authoring drawer (?tourdev=1): the camera as a pose of tour.json, in the frame of the nearest model ----
  const recordPose = () => {
    const e = camera.position, t = controls.target;
    let best = "world", bd = Infinity;
    for (const [id, c] of Object.entries(V.models)) { const d = Math.hypot(c.position[0] - t.x, c.position[2] - t.z); if (d < bd && d < 400) { bd = d; best = id; } }
    const f = frameOf(best), c = Math.cos(f.r), s = Math.sin(f.r);
    const loc = (v) => { const dx = v.x - f.x, dz = v.z - f.z; return [dx * c - dz * s, v.y - f.y, dx * s + dz * c].map((n) => Math.round(n)); };
    return { at: best, e: loc(e), t: loc(t) };
  };
  if (dev) {
    devBox = document.createElement("div");
    devBox.className = "t-dev";
    devBox.innerHTML = `<div><b>Tour authoring</b> <span class="d-stat"></span></div><button type="button" data-d="rec">Record pose</button><button type="button" data-d="copy">Copy</button><button type="button" data-d="clear">Clear</button><textarea spellcheck="false"></textarea>`;
    root.append(devBox);
    devBox.addEventListener("click", (e) => {
      const d = e.target.dataset.d, ta = devBox.querySelector("textarea");
      if (d === "rec") { const p = recordPose(); ta.value += `${JSON.stringify(p)},\n`; console.log("tour pose", JSON.stringify(p)); }
      if (d === "copy") navigator.clipboard?.writeText(ta.value);
      if (d === "clear") ta.value = "";
    });
    setInterval(() => { if (!alive) return; devBox.querySelector(".d-stat").textContent = `${chapters[curIndex]?.id} t=${tt.toFixed(1)} h=${currentHour(performance.now()).toFixed(2)} q=${V.beauty?.quality} clamps=${clamps}`; }, 500);
  }

  // ---- the test's handle and the reports ----
  // Clearance along the whole tour, sampled at `hz`: the eye's height over the ground (or water, or a terrace), its distance to the nearest hall box, and with rays, to the nearest surface of a model, a wall or a bridge.
  const rayTargets = () => {
    const list = [];
    for (const { group } of Object.values(V.detailed)) group.traverse((o) => { if (o.isMesh) list.push(o); });
    if (V.meshes?.structures) V.meshes.structures.traverse((o) => { if (o.isMesh) list.push(o); });
    return list;
  };
  const DIRS = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], [1, 1, 1], [1, 1, -1], [-1, 1, 1], [-1, 1, -1], [1, -1, 1], [1, -1, -1], [-1, -1, 1], [-1, -1, -1]].map((d) => new THREE.Vector3(...d).normalize());
  const clearance = (hz = 10, reach = 40) => {
    const meshes = rayTargets(), ray = new THREE.Raycaster(), hits = [], e = new THREE.Vector3(), g = new THREE.Vector3(), sphere = new THREE.Sphere();
    for (const m of meshes) { m.geometry.boundingSphere || m.geometry.computeBoundingSphere(); }
    const out = chapters.map((c) => ({ id: c.id, minHeight: Infinity, minBox: Infinity, minSurface: Infinity, at: null, clampedSamples: 0, maxTurnDegPerS: 0, turnAt: null, maxSpeed: 0 }));
    let prevDir = null, prevEye = null;
    for (let t = 0; t < total; t += 1 / hz) {
      const P = poseAt(t, e, g);
      const R = out[P.i];
      if (P.clamped) R.clampedSamples++;
      const ground = groundY(e.x, e.z);
      R.minHeight = Math.min(R.minHeight, e.y - ground);
      let nb = Infinity;
      for (const b of nearBoxes(e.x, e.z)) nb = Math.min(nb, boxDist(e, b));
      for (const b of boxes) if (Math.abs(b.cx - e.x) < 80 && Math.abs(b.cz - e.z) < 80) nb = Math.min(nb, boxDist(e, b));
      R.minBox = Math.min(R.minBox, nb);
      let ns = Infinity;
      for (const m of meshes) {
        sphere.copy(m.geometry.boundingSphere).applyMatrix4(m.matrixWorld);
        if (sphere.distanceToPoint(e) > reach) continue;
        for (const d of DIRS) {
          ray.set(e, d); ray.far = reach; hits.length = 0;
          THREE.Mesh.prototype.raycast.call(m, ray, hits);
          for (const h of hits) ns = Math.min(ns, h.distance);
        }
      }
      if (ns < R.minSurface) { R.minSurface = ns; R.at = +t.toFixed(1); }
      const dir = g.clone().sub(e).normalize();
      if (prevDir && t > 0) {
        const deg = (Math.acos(clamp(dir.dot(prevDir), -1, 1)) * 180) / Math.PI * hz;
        if (deg > R.maxTurnDegPerS) { R.maxTurnDegPerS = deg; R.turnAt = +t.toFixed(1); }
        R.maxSpeed = Math.max(R.maxSpeed, e.distanceTo(prevEye) * hz);
      }
      prevDir = dir; prevEye = e.clone();
    }
    return out.map((r) => ({ ...r, minHeight: +r.minHeight.toFixed(2), minBox: +r.minBox.toFixed(1), minSurface: Number.isFinite(r.minSurface) ? +r.minSurface.toFixed(1) : `>${reach}`, maxTurnDegPerS: +r.maxTurnDegPerS.toFixed(1), maxSpeed: +r.maxSpeed.toFixed(0) }));
  };
  // Which models stand in view, in the middle of the frame or anywhere in it, at some moment of each chapter
  const inView = (hz = 2) => {
    const seen = {}, e = new THREE.Vector3(), g = new THREE.Vector3(), cam = camera.clone(), fr = new THREE.Frustum(), m = new THREE.Matrix4();
    cam.near = 0.5; cam.far = 60000; cam.clearViewOffset();
    for (let t = 0; t < total; t += 1 / hz) {
      const P = poseAt(t, e, g);
      cam.position.copy(e); cam.lookAt(g); cam.updateMatrixWorld(); cam.updateProjectionMatrix();
      fr.setFromProjectionMatrix(m.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
      for (const [id, c] of Object.entries(V.models)) {
        const p = new THREE.Vector3(...c.position);
        p.y += (c.caption?.ridge_m || 6) / 2;
        if (!fr.containsPoint(p) || p.distanceTo(e) > 700) continue;
        const ndc = p.clone().project(cam);
        (seen[id] ||= []).push({ ch: chapters[P.i].id, t: +t.toFixed(1), d: Math.round(p.distanceTo(e)), centre: Math.abs(ndc.x) < 0.5 && Math.abs(ndc.y) < 0.6 });
      }
    }
    return seen;
  };
  const api = {
    chapters: chapters.map((c) => ({ id: c.id, start: c.start, end: c.end, travel: c.travel, seconds: c.seconds, hour: c.hour, models: c.models })),
    get total() { return total; }, get t() { return tt; }, get index() { return curIndex; }, get playing() { return playing; }, get waiting() { return waiting; }, get ended() { return ended; },
    get speed() { return speed; }, get lang() { return lang; }, get cinema() { return cinema; }, get clamps() { return clamps; }, get adaptations() { return adaptLog; },
    frameStats: () => { const by = {}; for (const f of frameLog) (by[chapters[f.i]?.id] ||= []).push(f.ms); return Object.fromEntries(Object.entries(by).map(([k, v]) => { v.sort((a, b) => a - b); return [k, { frames: v.length, median: +v[Math.floor(v.length / 2)].toFixed(1), p90: +v[Math.floor(v.length * 0.9)].toFixed(1) }]; })); },
    seek(t) { tt = clamp(t, 0, total - 1e-3); ended = false; userPaused = false; blend = null; $(".t-cardbox.end").hidden = true; draw(performance.now()); },
    seekChapter: (i) => seekChapter(i, false), play, pause: (byUser = false) => pause(byUser), exit, poseAt: (t) => { const P = poseAt(t, new THREE.Vector3(), new THREE.Vector3()); return { eye: P.eye.toArray(), tgt: P.tgt.toArray(), i: P.i }; },
    hourAt, clearance, inView, recordPose, setCinema, act,
  };
  window.__tour = api;

  // ---- go ----
  document.body.classList.add("guided");
  V.setGuided(true);
  V.cycle?.pause();
  V.close?.();
  V.panelCog?.close();
  if (!V.beauty?.on) await V.setLight("sun", { keepUrl: true });
  if (phone() && !pinned) V.beauty?.setQuality("min");
  V.beauty?.nightReady(); // the lanterns of the last chapter, loaded behind the day
  V.setSizer(sizer);
  fitFrame();
  setCinema(cinema);
  root.classList.toggle("ui0", ui0); // a link's ui=0 is for recording: not even the button to leave cinema shows
  if (ui0) onStir();
  paintStart();
  paintChrome();
  tt = firstIndex > 0 ? chapters[firstIndex].start + chapters[firstIndex].travel : 0;
  draw(performance.now());
  // the page /tour waits for its poster's button (a gesture, so full screen can follow); 3d.html?tour=1 starts at once
  const begin = () => {
    if (!alive) return;
    window.__loaderDone?.(T[lang].starting);
    if (firstIndex === 0) { startCard = 1; $(".t-cardbox.start").hidden = false; }
    if (reducedMotion) { startPaused = true; pause(false); $(".t-resume").hidden = false; paintChrome(); draw(performance.now()); } else play();
  };
  if (page && document.getElementById("tour-poster") && !window.__tourBegin && params.get("poster") !== "0") addEventListener("tour-begin", begin, { once: true });
  else begin();
  return api;
}
