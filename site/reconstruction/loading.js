// Loading screen and console for the 3D view (3d.html): what is being loaded, and how far along it is. Ported from the Küstrin project's loading.js.
// Classic script, run before every other script. It wraps window.fetch and counts the bytes of each file as they arrive (hosts send brotli without
// a Content-Length, so sizes grow as they come in), names the files (the detailed models from data/models.json, one line per building), and ticks off the stages.
// In the palace view the detailed models load BEFORE 3d.js sets window.__ready (it waits for them), so the card stays over the view while the buildings
// come in one by one, then shows a closing line and fades out. The viewer is untouched except for one line in 3d.js: it must not hide #loading itself
// when this script is running (window.__loaderOn).
// Off for screenshots: ?shot=1, ?loading=0, and automated browsers (navigator.webdriver), unless ?loading=1.
(() => {
  const root = document.getElementById("loading");
  if (!root) return;
  const q = new URLSearchParams(location.search);
  if (q.get("shot") || q.get("loading") === "0" || (navigator.webdriver && q.get("loading") !== "1")) {
    root.remove();
    return;
  }
  window.__loaderOn = true;

  const $ = (id) => document.getElementById(id);
  const log = $("ld-log");
  const t0 = performance.now();
  const STEPS = [
    ["engine", "3D engine"],
    ["ground", "Ground, hills, lakes and canals"],
    ["halls", "Halls, walls and gates"],
    ["kit", "Hall kit: roofs, columns, courts"],
    ["paths", "Paths, galleries, bridges and routes"],
    ["greens", "Trees, lotus and rockeries"],
    ["around", "The surroundings of the palace"],
    ["models", "Detailed buildings"],
    ["light", "Light: sun, shadows, sky and the night"],
  ];
  const steps = {};
  for (const [key, label] of STEPS) {
    const li = document.createElement("li");
    li.textContent = label;
    $("ld-steps").append(li);
    steps[key] = { li, label, files: 0, done: 0, state: "" };
  }

  const files = []; // { path, step, name, base, bytes, start, end, ok, note, el }
  const names = {}; // pathname -> "含经堂 Hanjingtang (CC02)", from data/models.json
  let phase = "base"; // base -> after
  let engineDone = false, modelsExpected = 0, modelsDone = 0, bytes = 0, inFlight = 0;
  let shown = 0, dirty = true, lastProgress = performance.now(), stick = true;

  const mb = (n) => (n >= 1048576 ? (n / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB");
  const secs = (ms) => (ms / 1000).toFixed(1) + " s";
  const pathOf = (u) => {
    try { return new URL(u, document.baseURI).pathname; } catch { return String(u); }
  };
  const classify = (path) => {
    const file = path.split("/").pop();
    if (path.endsWith("/generated/ground.json")) return ["ground", "Ground · index"];
    if (path.endsWith("/generated/ground.bin")) return ["ground", "Ground · heights, hills and lakebeds"];
    if (path.endsWith("/generated/ground_grid.i16")) return ["ground", "Ground · height grid"];
    if (path.endsWith("/generated/ground_level.u8")) return ["ground", "Ground · water levels"];
    if (path.endsWith("/generated/ground_outer.json") || path.endsWith("/generated/ground_outer.bin")) return ["around", "Land beyond the walls · " + (file.endsWith("json") ? "index" : "heights")];
    if (path.endsWith("/data/around_1860.json")) return ["around", "Villages, camps, neighbouring gardens and roads"];
    if (path.endsWith("/data/halls_1860.geojson")) return ["halls", "Halls and their footprints"];
    if (path.endsWith("/generated/structures.json")) return ["halls", "Walls, gates and terraces"];
    if (path.endsWith("/data/labels_1860.json")) return ["halls", "Names of the scenes"];
    if (path.endsWith("/data/kit_1860.json")) return ["kit", "Hall kit · the form of every hall"];
    if (path.endsWith("/generated/courts.bin")) return ["kit", "Hall kit · paved courts"];
    if (path.endsWith("/data/paths_1860.geojson")) return ["paths", "Paths and galleries"];
    if (path.endsWith("/data/landings_1860.geojson")) return ["paths", "Boat landings"];
    if (path.endsWith("/data/routes_1860.geojson")) return ["paths", "Walking and boat routes"];
    if (path.endsWith("/data/greens_1860.json")) return ["greens", "Planting · areas and species"];
    if (path.endsWith("/generated/greens_1860.bin")) return ["greens", "Planting · the trees"];
    if (path.endsWith("/data/models.json")) return ["models", "Index of the detailed buildings"];
    if (path.endsWith("/data/plates.json")) return ["engine", "Engraving cameras"];
    if (path.endsWith("/beauty3d.js")) return ["light", "Beautiful light · sun, shadows, sky, haze"];
    if (path.endsWith("/night3d.js")) return ["light", "Beautiful light · lanterns and lit windows"];
    if (path.includes("/data/buildings/")) return ["models", "Page · " + decodeURIComponent(file.replace(".json", ""))];
    if (file.endsWith(".glb")) {
      const id = path.split("/").slice(-2, -1)[0];
      return ["models", names[path] || (file === "model.glb" ? "Model " + id : id + " · " + file.replace(".glb", ""))];
    }
    return [null, path.replace(/^\/reconstruction\//, "")];
  };
  const learnModels = (idx) => {
    if (!idx || !idx.models) return;
    let n = 0;
    for (const [id, c] of Object.entries(idx.models)) {
      const name = c.name ? `${c.name} (${id})` : id;
      if (c.url) { names[pathOf(c.url)] = name; n++; }
      if (c.photoUrl) names[pathOf(c.photoUrl)] = name + " · photo";
      if (c.groundUrl) { names[pathOf(c.groundUrl)] = name + " · ground"; n++; }
    }
    modelsExpected = n;
    for (const f of files) if (f.step === "models" && names[f.path]) { f.name = names[f.path]; if (f.el) f.el.children[1].textContent = f.name; }
    dirty = true;
  };

  // ---- the fetch wrapper ----
  const origFetch = window.fetch.bind(window);
  const restore = () => { if (window.fetch === wrapped) window.fetch = origFetch; };
  const wrapped = async (input, init) => {
    if (phase === "after") return origFetch(input, init);
    const path = pathOf(typeof input === "string" ? input : input instanceof URL ? input.href : input.url);
    const [step, name] = classify(path);
    if (init && init.method === "HEAD") return origFetch(input, init); // the local-server probe is not a download
    const f = { path, step, name, base: !path.endsWith(".glb") && step !== "models", bytes: 0, start: performance.now(), end: 0, ok: null, note: "", el: null };
    files.push(f);
    inFlight++;
    if (step) steps[step].files++;
    dirty = true;
    const finish = (ok, note) => {
      if (f.end) return;
      f.end = performance.now();
      f.ok = ok;
      f.note = note || "";
      inFlight--;
      lastProgress = f.end;
      if (step) steps[step].done++;
      if (ok && path.endsWith(".glb")) modelsDone++;
      dirty = true;
    };
    let res;
    try {
      res = await origFetch(input, init);
    } catch (err) {
      finish(false, "network error");
      throw err;
    }
    if (!res.ok) { finish(false, String(res.status)); return res; } // optional files (a 404 the viewer tolerates) show as skipped
    if (path.endsWith("/data/models.json")) res.clone().json().then(learnModels).catch(() => {});
    if (!res.body || [101, 204, 205, 304].includes(res.status)) { finish(true); return res; }
    const counter = new TransformStream({
      transform(chunk, ctl) {
        f.bytes += chunk.byteLength;
        bytes += chunk.byteLength;
        lastProgress = performance.now();
        dirty = true;
        ctl.enqueue(chunk);
      },
      flush() { finish(true); },
    });
    return new Response(res.body.pipeThrough(counter), { status: res.status, statusText: res.statusText, headers: res.headers });
  };
  window.fetch = wrapped;

  // ---- the stages ----
  document.addEventListener("DOMContentLoaded", () => {
    engineDone = true;
    // The scripts came in through <script> tags, not fetch: list them from the resource timings.
    const label = {
      "three.bundle.js": "3D engine (three.js)", "ground3d.js": "Ground renderer", "around3d.js": "Surroundings renderer", "halls3d.js": "Halls: picking and colour",
      "stonekit3d.js": "Stone kit (the European palaces)", "kit3d.js": "Hall kit (Chinese timber halls)", "paths3d.js": "Paths and routes", "greens3d.js": "Planting",
      "glb_lite.js": "Model reader", "model3d.js": "Model viewer", "panel3d.js": "Building panel", "3d.js": "Viewer", "loading.js": "Loading console",
    };
    const scripts = performance.getEntriesByType("resource").filter((e) => e.initiatorType === "script" && /\/reconstruction\//.test(e.name));
    for (const e of scripts.reverse()) {
      const file = pathOf(e.name).split("/").pop();
      const size = e.decodedBodySize || e.transferSize || 0;
      bytes += size;
      files.unshift({ path: e.name, step: "engine", name: label[file] || "Script · " + file, base: true, bytes: size, start: e.startTime, end: e.responseEnd, ok: true, note: "", el: null, script: true });
    }
    dirty = true;
  });
  // window.__ready: 3d.js sets it when the gardens and every detailed building are built. Tools read it too, so it keeps its plain value.
  let readyFlag = false;
  Object.defineProperty(window, "__ready", {
    configurable: true,
    enumerable: true,
    get: () => readyFlag,
    set: (v) => {
      readyFlag = v;
      if (v && phase === "base") allDone();
    },
  });
  const allDone = (note) => {
    if (phase === "after") return;
    phase = "after";
    restore();
    for (const [key] of STEPS) steps[key].state = "ok";
    const loaded = files.filter((f) => f.ok && f.path.endsWith(".glb")).length;
    $("ld-sub").classList.remove("bad");
    $("ld-sub").textContent = note || `All built: ${loaded} detailed buildings, ${mb(bytes)} in ${secs(performance.now() - t0)}.`;
    $("ld-reload").hidden = true;
    $("ld-close").hidden = true;
    paint();
    setTimeout(() => {
      root.classList.add("done");
      setTimeout(() => root.remove(), 900);
    }, note ? 6000 : 1600);
  };
  // An error before the gardens are built: say so and offer a reload, but keep watching. A harmless error must not leave the card over a
  // working view, so if 3d.js still reaches __ready the card closes as usual; the × hides it at any time.
  const fail = (err) => {
    if (phase !== "base") return;
    const msg = (err && (err.message || err.reason)) || String(err || "unknown error");
    $("ld-sub").textContent = "Something didn't load: " + msg;
    $("ld-sub").classList.add("bad");
    $("ld-reload").hidden = false;
    $("ld-close").hidden = false;
    dirty = true;
  };
  addEventListener("unhandledrejection", (e) => fail(e.reason));
  addEventListener("error", (e) => fail(e.error || e.message));
  $("ld-close").onclick = () => { allDone(); root.remove(); };
  $("ld-reload").onclick = () => location.reload();
  log.addEventListener("scroll", () => { stick = log.scrollTop + log.clientHeight >= log.scrollHeight - 8; });

  // ---- drawing ----
  const SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏";
  const paint = () => {
    const now = performance.now();
    // stages
    for (const [key] of STEPS) {
      const s = steps[key];
      let st = s.state || (s.files === 0 ? "" : s.done < s.files ? "run" : "ok");
      if (key === "engine") st = engineDone ? "ok" : "run";
      s.li.className = st;
      if (key === "models" && modelsExpected) s.li.textContent = `${s.label}: ${modelsDone} of ${modelsExpected}`;
    }
    // progress: 40 % for the garden data, 60 % for the detailed buildings; never runs backwards
    const base = files.filter((f) => f.base && !f.script);
    const baseDone = base.filter((f) => f.end).length;
    const baseFrac = phase === "after" ? 1 : (engineDone ? 0.1 : 0.03) + 0.9 * (baseDone / Math.max(16, base.length));
    const modelFrac = phase === "after" ? 1 : modelsExpected ? Math.min(1, modelsDone / modelsExpected) : 0;
    shown = Math.max(shown, phase === "after" ? 100 : 40 * Math.min(0.99, baseFrac) + 60 * Math.min(0.97, modelFrac));
    $("ld-bar").style.width = shown.toFixed(1) + "%";
    $("ld-count").textContent = modelsExpected && baseDone >= 16 ? `Buildings ${modelsDone} of ${modelsExpected}` : `Garden data · ${baseDone} of ${Math.max(16, base.length)} files`;
    $("ld-bytes").textContent = `${mb(bytes)} · ${secs(now - t0)}`;
    if (phase === "base" && now - lastProgress > 30000 && !$("ld-sub").classList.contains("bad")) $("ld-sub").textContent = "Still loading. A slow connection?";
    // the console, one line per file
    let appended = false;
    files.forEach((f, i) => {
      if (!f.el) {
        f.el = document.createElement("div");
        f.el.innerHTML = '<span class="i"></span><span class="n"></span><span class="s"></span><span class="t"></span>';
        f.el.children[1].textContent = f.name;
        const next = files.slice(i + 1).find((g) => g.el);
        if (next) log.insertBefore(f.el, next.el);
        else log.append(f.el);
        appended = true;
      }
      const cls = f.ok === null ? "run" : f.ok ? "ok" : f.note === "network error" ? "bad" : "skip";
      if (f.el.className !== "ln " + cls) f.el.className = "ln " + cls;
      const [ic, , sz, tm] = f.el.children;
      ic.textContent = f.ok === null ? SPIN[Math.floor(now / 90) % SPIN.length] : f.ok ? "✓" : cls === "bad" ? "✗" : "–";
      sz.textContent = f.ok === false ? (cls === "bad" ? "failed" : "skipped " + f.note) : f.bytes ? mb(f.bytes) : "";
      tm.textContent = secs((f.end || now) - f.start);
    });
    if (appended && stick) log.scrollTop = log.scrollHeight;
  };
  const tick = () => {
    if (!root.isConnected || phase === "after") return;
    if (dirty || inFlight > 0) { dirty = false; paint(); }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
})();
