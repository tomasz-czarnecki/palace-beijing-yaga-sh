// 3D preview of the three gardens before October 1860, real scale. A preview: not the project's final engine. Rendered on demand, not in a loop.
// Data: generated/ground.json + ground.bin (scripts/ground1860.py), generated/structures.json and data/halls_1860.geojson (scripts/boxes1860.py), data/buildings/<ID>.json (scripts/building_pages.py), data/labels_1860.json.
// World axes: x = east, z = south, y = height above the water, metres. Halls are one merged mesh (halls3d.js); a click tests rectangles, not triangles.
// URL: ?b=<ID> (opens that page and frames its object) &cam=x,y,z,tx,ty,tz &halls=0 &walls=0 &labels=0 &conf=1 &vx=2 &shot=1 (hides the panels, nothing animates, no labels) &public=1 (localhost: no research copy of the pages).
// Round 10: the ground (ground3d.js): hills, banks, beds, one level per water body; &contours=1 draws contour lines; &conf=1 also tints the ground; &assumed=0 also flattens the generated hills.
// Round 11: the hall kit (kit3d.js, stonekit3d.js, data/kit_1860.json): every hall drawn from its numbers, courts paved between the halls; &kit=0 returns to the plain boxes; &assumed=0 also hides the boxes with no block on the plan, the courts, and draws a hall whose form is only its class's as its plain box.
// Round 12: the planting and the rockeries (greens3d.js, data/greens_1860.json, generated/greens_1860.bin): &greens=0 hides them; &season=spring|summer|autumn|winter (default summer); &assumed=0 also hides the generated fill and lowers plants on generated hills; &conf=1 tints plants by the grade of their species, the fill pale.
// Round 13: detailed models (data/models.json, models/<ID>-<slug>/ by scripts/building_pages.py, glb_lite.js): the model replaces its boxes' drawing, the boxes stay the click target, unseen; &assumed=0 hides the parts carried round with no picture (materials ~fill), &conf=1 tints them pale and the rest by its grade. The panel's "Our model now" has the model's own small view (model3d.js).
// Round 13: &plate=<photo id>[&platefit=all|anchored] is a development mode: the camera of that plate or photograph as tools/plate_overlay.py fitted it (data/plates.json), the picture laid over the view at a set opacity; &plateimg=0 the view alone.
// Round 9: &paths=0 hides the ways (data/paths_1860, landings_1860: paths3d.js), &assumed=0 only the assumed (C) ones; &route=<R1..> walks a route of data/routes_1860 from its start, &routet=<0..1> from that share of its length (with &shot=1 the camera stands there, still).
const params = new URLSearchParams(location.search);
const shot = Boolean(params.get("shot"));
if (shot) document.body.classList.add("shot");
const reduced = () => shot || matchMedia("(prefers-reduced-motion: reduce)").matches;
const SKY = 0xcfd8dd;

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
document.body.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(SKY);
scene.fog = new THREE.Fog(SKY, 6000, 40000); // Round 20: clear over the gardens, the Western Hills (10-40 km) a hazy ridge
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8370, 1.7));
const sun = new THREE.DirectionalLight(0xfff4e0, 2.3);
sun.position.set(-700, 900, 800); // from the south-west, so roofs read
scene.add(sun);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 1, 60000);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.maxDistance = 9000;
controls.screenSpacePanning = false;
controls.maxPolarAngle = Math.PI / 2 - 0.01;
const REACH_M = 5000; // how far the view's turning point may be moved from the middle of the gardens
controls.addEventListener("change", () => {
  const t = controls.target, dx = Math.max(Math.min(t.x, REACH_M), -REACH_M) - t.x, dz = Math.max(Math.min(t.z, REACH_M), -REACH_M) - t.z;
  if (dx || dz) { t.x += dx; t.z += dz; camera.position.x += dx; camera.position.z += dz; }
});
const world = new THREE.Group(); // scaled in y for the 2x option
scene.add(world);

const ABOVE_ALL_M = 40; // higher than any ridge above the water
let plateLock = false; // Round 13: ?plate= holds its own projection
function fitNearPlane() {
  if (plateLock) return;
  const room = camera.position.y - ABOVE_ALL_M * world.scale.y;
  const near = Math.max(0.5, Math.min(room * 0.6, camera.position.distanceTo(controls.target) * 0.4));
  if (Math.abs(near - camera.near) > 0.05 * camera.near) { camera.near = near; camera.updateProjectionMatrix(); }
}
let labels = [];
function updateLabels() {
  const on = state.labels && !shot && !walking && !touring;
  for (const l of labels) {
    const d = camera.position.distanceTo(l.position);
    if (l.userData.around) { l.visible = on && state.around && !(l.userData.assumed && !state.assumed) && (l.userData.rank === 1 ? d > 900 : d < 3200); continue; } // Round 20
    l.visible = on && (l.userData.rank === 1 ? d > 700 : d < 1400);
  }
}
let kitUpdate = null, kitFrame = 0, greensUpdate = null, lastRender = 0;
function render() {
  lastRender = performance.now();
  fitNearPlane();
  updateLabels();
  // Round 11: the kit builds the near detail of the tiles in reach; while some wait, another frame follows. A still (shot=1) waits for all. Round 12: so do the plants.
  const kitWaits = kitUpdate && kitUpdate(camera, shot ? 1e9 : 4), greensWait = greensUpdate && greensUpdate(camera, shot ? 1e9 : 3);
  if ((kitWaits || greensWait) && !kitFrame) kitFrame = requestAnimationFrame(() => { kitFrame = 0; render(); });
  renderer.render(scene, camera);
}
controls.addEventListener("change", render);
addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  setOffset(offset);
  renderer.setSize(innerWidth, innerHeight);
  render();
});

// The panel covers part of the canvas, so the picture's centre moves into the part still free. Pixels, as in camera.setViewOffset.
let offset = [0, 0];
function setOffset(o) {
  offset = o;
  if (o[0] || o[1]) camera.setViewOffset(innerWidth, innerHeight, o[0], o[1], innerWidth, innerHeight);
  else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}
const isPhone = () => innerWidth <= 760;
const PANEL_W = 400, SHEET = 0.56, HEADER = 48;
function freeArea(open) {
  if (!open) return [0, 0, 1, 1];
  if (isPhone()) { const sheet = innerHeight * SHEET; return [0, Math.round((sheet - HEADER) / 2), 1, (innerHeight - sheet - HEADER) / innerHeight]; }
  const w = Math.min(PANEL_W, innerWidth);
  return [Math.round(w / 2), -HEADER / 2, (innerWidth - w) / innerWidth, (innerHeight - HEADER) / innerHeight];
}

// The camera's glide: at once with ?shot=1 or prefers-reduced-motion. Any press on the canvas stops it.
let glideId = 0;
function glideTo(pos, tgt, off, ms = 700) {
  const id = ++glideId, p0 = camera.position.clone(), t0 = controls.target.clone(), o0 = offset.slice(), p1 = new THREE.Vector3(...pos), t1 = new THREE.Vector3(...tgt);
  const set = (k) => {
    camera.position.lerpVectors(p0, p1, k);
    controls.target.lerpVectors(t0, t1, k);
    setOffset([o0[0] + (off[0] - o0[0]) * k, o0[1] + (off[1] - o0[1]) * k]);
    controls.update();
    render();
  };
  if (reduced()) { set(1); return; }
  const start = performance.now();
  const step = (now) => {
    if (id !== glideId) return;
    const t = Math.min((now - start) / ms, 1);
    set(t < 0.5 ? 2 * t * t : 1 - (2 - 2 * t) ** 2 / 2);
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

const state = { kit: params.get("kit") !== "0", halls: params.get("halls") !== "0", walls: params.get("walls") !== "0", labels: params.get("labels") !== "0", conf: params.get("conf") === "1", vx: Number(params.get("vx") || 1), paths: params.get("paths") !== "0", assumed: params.get("assumed") !== "0", contours: params.get("contours") === "1", greens: params.get("greens") !== "0", around: params.get("around") !== "0", season: ["spring", "summer", "autumn", "winter"].includes(params.get("season")) ? params.get("season") : "summer" };
const meshes = {};
let walking = false, touring = null;

// Walls as thin solids, bridges as decks. One mesh each. Bridges with a row in buildings.csv are clickable through `bridgeBoxes`. Round 18: a bridge a detailed model draws (models.json `bridges`) is left out; Round 19: so are the wall segments inside a model's `walls_cut`.
function buildStructures(data, skipBridges = new Set(), wallCuts = []) {
  const group = new THREE.Group();
  const pushBox = (out, ax, az, bx, bz, half, y0, y1, y0b = y0, y1b = y1) => {
    const dx = bx - ax, dz = bz - az, len = Math.hypot(dx, dz) || 1, nx = (-dz / len) * half, nz = (dx / len) * half;
    const p = [[ax + nx, az + nz], [bx + nx, bz + nz], [bx - nx, bz - nz], [ax - nx, az - nz]];
    const ys = [[y0, y1], [y0b, y1b], [y0b, y1b], [y0, y1]];
    const tri = (a, b, c) => out.push(...a, ...b, ...c);
    const v = (i, top) => [p[i][0], ys[i][top ? 1 : 0], p[i][1]];
    tri(v(0, 1), v(1, 1), v(2, 1)); tri(v(0, 1), v(2, 1), v(3, 1));
    for (let i = 0; i < 4; i++) { const j = (i + 1) % 4; tri(v(i, 1), v(i, 0), v(j, 0)); tri(v(i, 1), v(j, 0), v(j, 1)); }
  };
  const wall = [];
  const half = data.wall.thickness_m / 2;
  const cut = (x, z) => wallCuts.some((poly) => { let ins = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, zi] = poly[i], [xj, zj] = poly[j]; if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) ins = !ins; } return ins; });
  for (const [ax, az, bx, bz, y0, y1] of data.wall.segments) if (!cut((ax + bx) / 2, (az + bz) / 2)) pushBox(wall, ax, az, bx, bz, half, y0, y1); // Round 19: a model's `walls_cut` (it draws those walls itself)
  const wallGeo = new THREE.BufferGeometry();
  wallGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(wall), 3));
  wallGeo.computeVertexNormals();
  group.add(new THREE.Mesh(wallGeo, new THREE.MeshLambertMaterial({ color: 0x8c8378, side: THREE.DoubleSide })));
  const deck = [];
  for (const b of data.bridges) {
    if (skipBridges.has(b.id)) continue; // Round 18: a detailed model draws this bridge (models.json `bridges`)
    for (let i = 0; i < b.pts.length - 1; i++) {
      const [ax, ay, az] = b.pts[i], [bx, by, bz] = b.pts[i + 1];
      pushBox(deck, ax, az, bx, bz, b.width_m / 2, Math.min(ay, by) - 0.5, ay, Math.min(ay, by) - 0.5, by);
    }
  }
  const deckGeo = new THREE.BufferGeometry();
  deckGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(deck), 3));
  deckGeo.computeVertexNormals();
  group.add(new THREE.Mesh(deckGeo, new THREE.MeshLambertMaterial({ color: 0xbdb4a2, side: THREE.DoubleSide })));
  return group;
}

// A name as a sprite that keeps its size on screen.
function labelSprite(text, sub, rank) {
  const canvas = document.createElement("canvas"), ctx = canvas.getContext("2d");
  const size = rank === 1 ? 22 : 13, subSize = rank === 1 ? 12 : 9, ratio = 2;
  const font = (s, w) => `${w} ${s * ratio}px 'Noto Sans SC','PingFang SC','Microsoft YaHei','Geist',system-ui,sans-serif`;
  ctx.font = font(size, 600);
  const w1 = ctx.measureText(text).width;
  ctx.font = font(subSize, 500);
  const w2 = sub ? ctx.measureText(sub).width : 0;
  canvas.width = Math.ceil(Math.max(w1, w2)) + 16;
  canvas.height = Math.ceil((size * 1.25 + (sub ? subSize * 1.3 : 0)) * ratio) + 8;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.strokeStyle = "#17130fd0";
  ctx.fillStyle = rank === 1 ? "#fff3d6" : "#ffffff";
  ctx.lineJoin = "round";
  ctx.lineWidth = rank === 1 ? 8 : 5;
  ctx.font = font(size, 600);
  ctx.strokeText(text, canvas.width / 2, 4);
  ctx.fillText(text, canvas.width / 2, 4);
  if (sub) {
    ctx.font = font(subSize, 500);
    ctx.lineWidth = 4;
    ctx.strokeText(sub, canvas.width / 2, 4 + size * 1.25 * ratio);
    ctx.fillText(sub, canvas.width / 2, 4 + size * 1.25 * ratio);
  }
  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, depthWrite: false, sizeAttenuation: false, transparent: true }));
  // Without size attenuation a sprite's scale is a share of the view's height over the projection's y scale: pixels on a page of this height.
  const k = (2 * Math.tan((camera.fov * Math.PI) / 360)) / innerHeight / ratio;
  s.scale.set(canvas.width * k, canvas.height * k, 1);
  s.center.set(0.5, 0);
  s.renderOrder = 10;
  return s;
}

async function main() {
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname) && !params.get("public") && (await fetch(location.href, { method: "HEAD" }).then((r) => r.headers.get("X-Palace-Local") === "1").catch(() => false));
  const [meta, buf, gridBuf, levelBuf, fc, structures, labelData, pathFc, landingFc, routeFc, kitSpec, greensMeta, greensBuf] = await Promise.all([
    fetch("generated/ground.json").then((r) => r.json()),
    fetch("generated/ground.bin").then((r) => r.arrayBuffer()),
    fetch("generated/ground_grid.i16").then((r) => r.arrayBuffer()),
    fetch("generated/ground_level.u8").then((r) => r.arrayBuffer()),
    fetch("data/halls_1860.geojson").then((r) => r.json()),
    fetch("generated/structures.json").then((r) => r.json()),
    fetch("data/labels_1860.json").then((r) => r.json()),
    fetch("data/paths_1860.geojson").then((r) => r.json()),
    fetch("data/landings_1860.geojson").then((r) => r.json()),
    fetch("data/routes_1860.geojson").then((r) => r.json()),
    fetch("data/kit_1860.json").then((r) => r.json()),
    fetch("data/greens_1860.json").then((r) => r.json()),
    fetch("generated/greens_1860.bin").then((r) => r.arrayBuffer()),
  ]);
  // Round 20: the ground past the domain and what stood on it (around3d.js); the view works without them
  const [outerMeta, outerBuf, aroundData] = await Promise.all([
    fetch("generated/ground_outer.json").then((r) => (r.ok ? r.json() : null)).catch(() => null),
    fetch("generated/ground_outer.bin").then((r) => (r.ok ? r.arrayBuffer() : null)).catch(() => null),
    fetch("data/around_1860.json").then((r) => (r.ok ? r.json() : null)).catch(() => null),
  ]);
  const modelIndex = await fetch("data/models.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const MODELS = (modelIndex && modelIndex.models) || {};
  const modelBoxIds = new Set(Object.values(MODELS).flatMap((c) => c.boxes || []));
  const drawnByModel = (p) => (p.kind === "steps" || p.kind === "gallery") && [p.from_at, p.to_at].some((at) => at && modelBoxIds.has(at.split(":")[0]));
  const a = meta.lonlat;
  const toXZ = ([lon, lat]) => [a.x[0] + a.x[1] * (lon - a.lon0) + a.x[2] * (lat - a.lat0), a.z[0] + a.z[1] * (lon - a.lon0) + a.z[2] * (lat - a.lat0)];
  const ground = buildGround({ meta, buf, gridBuf, levelBuf });
  const { groundAt, waterLevelAt } = ground;
  world.add(ground.group);
  const around = outerMeta && outerBuf ? buildAround({ meta: outerMeta, buf: outerBuf, data: aroundData, inner: ground, datum: meta.datum_m }) : null;
  if (around) { world.add(around.group); world.add(around.items); }
  const greens = buildGreens({ meta: greensMeta, buf: greensBuf, datum: meta.datum_m, toXZ });
  world.add(greens.group);
  greensUpdate = greens.update;
  meshes.structures = buildStructures(structures, new Set(Object.values(MODELS).flatMap((c) => c.bridges || [])), Object.values(MODELS).flatMap((c) => c.walls_cut || []));
  world.add(meshes.structures);
  const halls = buildHalls({ fc, toXZ, datum: meta.datum_m, kit: kitSpec });
  // Round 16: a raised floor a model draws (a terrace, models.json `decks`) carries the ways that cross it: they are laid on it, not on the ground under it
  const decks = Object.values(MODELS).flatMap((c) => c.decks || []);
  const inPoly = (x, z, poly) => { let ins = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, zi] = poly[i], [xj, zj] = poly[j]; if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) ins = !ins; } return ins; };
  const wayGroundAt = (x, z) => { for (const d of decks) if (inPoly(x, z, d.poly)) return d.y; return groundAt(x, z); };
  const ways = buildPaths({ paths: pathFc, landings: landingFc, toXZ, groundAt: wayGroundAt, waterLevelAt, base: meta.ground_m - meta.datum_m, skip: drawnByModel });
  for (const g of Object.values(ways.groups)) world.add(g);
  const kit = buildKit({ spec: kitSpec, halls, datum: meta.datum_m, groundAt, toXZ, paths: pathFc });
  await kit.courtsReady;
  halls.mesh.add(kit.group);
  kitUpdate = kit.update;
  meshes.halls = halls.mesh;
  world.add(meshes.halls);

  // Round 13: the detailed models, children of the halls' mesh so the halls toggle and the vertical exaggeration reach them. Until one has loaded its boxes show.
  const detailed = {}; // id -> { group, c }
  const modelOf = (id) => Object.entries(MODELS).find(([k, c]) => k === id || (c.aliases || []).includes(id));
  const MODEL_TINT = { fill: 0xe7e0d3, doc: HALL_COLOURS.conf.C, selected: 0x6a5000 };
  const modelsReady = Promise.all(Object.entries(MODELS).map(async ([id, c]) => {
    const g = await loadGLBLite(c.url);
    g.position.set(...c.position);
    g.rotation.y = c.rotationY;
    g.traverse((o) => {
      if (!o.isMesh) return;
      o.userData.fill = o.material.name.endsWith("~fill");
      o.userData.colour = o.material.color.clone();
      o.raycast = () => {}; // clicks go to the boxes (halls3d.js pick)
    });
    halls.mesh.add(g);
    if (params.get("plateonly") && params.get("plateonly") !== id) g.visible = false; // Round 16: &plateonly=<ID>, a development switch for the overlays: the other detailed models hidden (a niche before a hall)
    detailed[id] = { group: g, c };
  }).map((p) => p.catch((err) => console.warn("Detailed model not loaded, the boxes stay:", err)))).then(() => {
    if (Object.keys(detailed).length) halls.setModelled(true);
    applyModels();
    render();
    window.__modelsReady = true;
  });
  let modelSelected = new Set();
  function applyModels() {
    for (const [id, { group }] of Object.entries(detailed)) {
      const sel = modelSelected.has(id);
      group.traverse((o) => {
        if (!o.isMesh) return;
        o.visible = !(o.userData.fill && !state.assumed);
        if (state.conf) o.material.color.setHex(o.userData.fill ? MODEL_TINT.fill : MODEL_TINT.doc);
        else o.material.color.copy(o.userData.colour);
        o.material.emissive.setHex(sel ? MODEL_TINT.selected : 0);
      });
    }
  }
  const selectBoxes = halls.select;
  halls.select = (list) => {
    selectBoxes(list);
    modelSelected = new Set(Object.keys(detailed).filter((id) => list.some((b) => (MODELS[id].boxes || []).includes(b.id))));
    applyModels();
  };
  const modelFor = (id) => {
    const hit = modelOf(id);
    if (!hit || !detailed[hit[0]]) return null;
    const { group, c } = detailed[hit[0]];
    // a copy in the main scene's coordinates, baked into the geometry (model3d.js reads the raw positions for the footprint)
    const out = new THREE.Group(), mtx = new THREE.Matrix4().compose(group.position, group.quaternion, new THREE.Vector3(1, 1, 1));
    group.traverse((o) => { if (o.isMesh && !(o.userData.fill && !state.assumed)) { const m = new THREE.Mesh(o.geometry.clone().applyMatrix4(mtx), o.material.clone()); m.material.emissive.setHex(0); m.material.color.copy(o.userData.colour); out.add(m); } });
    out.userData = { ground: c.position[1], front: [Math.sin(c.rotationY), Math.cos(c.rotationY)], props: { ...c.caption, name: c.name } };
    return out;
  };
  const preview = createModelPreview({ modelFor, sunDir: sun.position.clone().normalize(), datum: meta.datum_m, busy: () => performance.now() - lastRender < 200 });
  labels = labelData.map((l) => {
    const s = labelSprite(l.zh, l.en, l.rank);
    const [x, z] = toXZ([l.lon, l.lat]);
    s.position.set(x, l.rank === 1 ? 42 : 20, z);
    s.userData = { rank: l.rank, id: l.id };
    world.add(s);
    return s;
  });

  if (around) for (const l of around.labels) {
    const s = labelSprite(l.text, l.sub, l.rank);
    s.position.set(l.x, l.y, l.z);
    s.userData = { rank: l.rank, id: l.id, around: true, assumed: l.assumed };
    world.add(s);
    labels.push(s);
  }

  let groundAssumed = true;
  function apply() {
    meshes.halls.visible = state.halls;
    meshes.structures.visible = state.walls;
    ways.groups.sure.visible = ways.groups.boat.visible = state.paths;
    ways.groups.assumed.visible = state.paths && state.assumed;
    ways.groups.gallery.visible = state.paths && !state.kit;
    halls.setView({ kitOn: state.kit, assumed: state.assumed });
    kit.setView({ kitOn: state.kit, assumed: state.assumed, paths: state.paths, conf: state.conf });
    ways.setConfMode(state.conf);
    ground.setConf(state.conf);
    if (groundAssumed !== state.assumed) { groundAssumed = state.assumed; ground.setAssumed(state.assumed); }
    ground.setContours(state.contours);
    greens.setView({ on: state.greens, assumed: state.assumed, conf: state.conf, season: state.season });
    if (around) { around.setView({ on: state.around, conf: state.conf, assumed: state.assumed, season: state.season }); for (const q of ground.farQuads) q.visible = !state.around; }
    document.getElementById("legend-greens").hidden = !state.greens;
    document.getElementById("legend-greens-conf").hidden = !state.conf;
    document.getElementById("legend-paths").hidden = !state.paths;
    world.scale.y = state.vx;
    world.updateMatrixWorld(true);
    halls.setConfMode(state.conf);
    applyModels();
    document.getElementById("legend-plain").hidden = state.conf;
    document.getElementById("legend-conf").hidden = !state.conf;
    render();
  }
  for (const key of ["kit", "halls", "walls", "labels", "conf", "paths", "assumed", "contours", "greens", "around"]) {
    const box = document.getElementById(key);
    if (!box) continue;
    box.checked = state[key];
    box.onchange = (e) => { state[key] = e.target.checked; apply(); };
  }
  const seasonSel = document.getElementById("season");
  seasonSel.value = state.season;
  seasonSel.onchange = (e) => { state.season = e.target.value; apply(); };
  const vxBox = document.getElementById("vx");
  vxBox.checked = state.vx === 2;
  vxBox.onchange = (e) => { state.vx = e.target.checked ? 2 : 1; apply(); };

  const byBuilding = new Map(), byParent = new Map(), byBoxId = new Map();
  for (const b of halls.info) {
    if (!byBuilding.has(b.bid)) byBuilding.set(b.bid, []);
    byBuilding.get(b.bid).push(b);
    byBoxId.set(b.id, b);
    for (const also of b.props.also || []) { if (!byBuilding.has(also)) byBuilding.set(also, []); byBuilding.get(also).push(b); }
    if (b.parent) {
      if (!byParent.has(b.parent)) byParent.set(b.parent, []);
      byParent.get(b.parent).push(b);
    }
  }
  for (const [rowId, target] of Object.entries(fc.shared_rows || {})) if (byBuilding.has(target)) byBuilding.set(rowId, byBuilding.get(target));
  const boxesOf = (id) => byBuilding.get(id) || byParent.get(id) || [];

  const panel = createBuildingPanel({ local, onClose: () => closeAll(), onOpen: (id) => open(id), onRoute: (id) => startTour(id, 0), onModel: (id, slot) => preview.show(id, slot) });
  const label = document.getElementById("hover");
  const ray = new THREE.Raycaster();
  const rayAt = (e) => {
    const r = renderer.domElement.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
    if (state.vx !== 1) { ray.ray.origin.y /= state.vx; ray.ray.direction.y /= state.vx; ray.ray.direction.normalize(); }
    return ray.ray;
  };
  const hitAt = (e) => (state.halls ? halls.pick(rayAt(e)) : null);
  const aroundAt = (e) => (around && state.around ? around.pick(rayAt(e)) : null); // Round 20: what stood round the gardens, when no hall is hit

  let home = null;
  const backBtn = document.getElementById("back");
  const setUrl = (id) => {
    const u = new URL(location.href);
    if (id) u.searchParams.set("b", id); else u.searchParams.delete("b");
    history.replaceState(null, "", u);
  };
  // Frames a list of boxes: from their front if there is one box, else from where the view already looks.
  const frameBoxes = (list, front) => {
    if (!home) { home = { pos: camera.position.toArray(), tgt: controls.target.toArray() }; backBtn.hidden = false; }
    const [ox, oy, fx, fy] = freeArea(!document.getElementById("bpanel").hidden);
    const lo = new THREE.Vector3(Infinity, Infinity, Infinity), hi = new THREE.Vector3(-Infinity, -Infinity, -Infinity);
    for (const b of list) {
      const r = Math.hypot(b.hf, b.hd);
      lo.min(new THREE.Vector3(b.cx - r, b.y0, b.cz - r));
      hi.max(new THREE.Vector3(b.cx + r, b.y1, b.cz + r));
    }
    const c = lo.clone().add(hi).multiplyScalar(0.5), size = hi.clone().sub(lo);
    const r = Math.max(size.x, size.y, size.z) / 2, tan = Math.tan((camera.fov * Math.PI) / 360);
    const d = 1.5 * Math.max(r / (tan * fy), r / (tan * camera.aspect * fx), 32); // the neighbours stay in view
    const look = front || (() => { const v = camera.position.clone().sub(controls.target); const l = Math.hypot(v.x, v.z) || 1; return [v.x / l, v.z / l]; })();
    const ELEV = 0.55;
    c.y *= state.vx;
    glideTo([c.x + look[0] * d * Math.cos(ELEV), c.y + d * Math.sin(ELEV), c.z + look[1] * d * Math.cos(ELEV)], c.toArray(), [ox, oy]);
  };
  const closeAll = () => {
    if (touring) { halls.select([]); panel.hide(); return; }
    glideId++;
    halls.select([]);
    panel.hide();
    setUrl(null);
    if (offset[0] || offset[1]) glideTo(camera.position.toArray(), controls.target.toArray(), [0, 0], 250);
    render();
  };
  backBtn.onclick = () => {
    if (!home) return;
    const h = home;
    home = null;
    backBtn.hidden = true;
    halls.select([]);
    panel.hide();
    setUrl(null);
    glideTo(h.pos, h.tgt, [0, 0]);
  };

  let openToken = 0;
  async function open(id, boxHit) {
    const token = ++openToken;
    try {
      const page = await panel.load(id);
      if (token !== openToken) return;
      const list = boxesOf(id);
      panel.show(page);
      setUrl(id);
      halls.select(list);
      if (!state.halls && list.length) { state.halls = true; document.getElementById("halls").checked = true; apply(); }
      if (list.length) {
        const front = list.length === 1 && !list[0].props.shape ? [list[0].a[0], list[0].a[1]] : null;
        frameBoxes(boxHit && !list.length ? [boxHit] : list, front);
      } else if (page.position) {
        const [x, z] = toXZ(page.position);
        const y = meta.ground_m - meta.datum_m;
        frameBoxes([{ cx: x, cz: z, hf: 25, hd: 25, y0: y, y1: y + 10 }], null);
      }
      render();
    } catch (err) {
      if (token === openToken) { console.warn(err); halls.select([]); panel.fail(id); }
    }
  }

  // Walk mode: the camera at eye height on the ground. Water and boxes stop you; bridges carry you. No physics, on purpose.
  const EYE = 1.6, SPEED = 5, HURRY = 18;
  const walkBtn = document.getElementById("walk"), walkExit = document.getElementById("walk-exit"), walkTip = document.getElementById("walk-tip");
  let yaw = 0, pitch = 0, walkHome = null, walkFrame = 0, lastT = 0, smoothY = 0;
  const keys = new Set();
  const nearestLand = (x, z) => {
    for (let r = 0; r < 300; r += 5) for (let k = 0; k < 12; k++) {
      const px = x + r * Math.cos((k * Math.PI) / 6), pz = z + r * Math.sin((k * Math.PI) / 6);
      if (groundAt(px, pz) !== null && !halls.blocked(px, pz, 1)) return [px, pz];
      if (r === 0) break;
    }
    return [x, z];
  };
  const applyWalkCamera = () => {
    const dir = new THREE.Vector3(Math.sin(yaw) * Math.cos(pitch), Math.sin(pitch), -Math.cos(yaw) * Math.cos(pitch));
    camera.lookAt(camera.position.clone().add(dir));
    if (kitUpdate) kitUpdate(camera, 2);
    if (greensUpdate) greensUpdate(camera, 2);
    renderer.render(scene, camera);
  };
  const walkStep = (now) => {
    if (!walking) return;
    const dt = Math.min((now - lastT) / 1000, 0.1);
    lastT = now;
    const speed = (keys.has("ShiftLeft") || keys.has("ShiftRight") ? HURRY : SPEED) * dt;
    let f = 0, s = 0;
    if (keys.has("KeyW") || keys.has("ArrowUp")) f += 1;
    if (keys.has("KeyS") || keys.has("ArrowDown")) f -= 1;
    if (keys.has("KeyD") || keys.has("ArrowRight")) s += 1;
    if (keys.has("KeyA") || keys.has("ArrowLeft")) s -= 1;
    if (f || s) {
      const dx = (Math.sin(yaw) * f + Math.cos(yaw) * s) * speed, dz = (-Math.cos(yaw) * f + Math.sin(yaw) * s) * speed;
      const try1 = (x, z) => groundAt(x, z) !== null && !halls.blocked(x, z);
      const p = camera.position;
      if (try1(p.x + dx, p.z + dz)) { p.x += dx; p.z += dz; } else if (try1(p.x + dx, p.z)) p.x += dx; else if (try1(p.x, p.z + dz)) p.z += dz;
      smoothY += ((groundAt(p.x, p.z) ?? smoothY) - smoothY) * Math.min(dt * 6, 1);
      p.y = (smoothY + EYE) * state.vx;
      applyWalkCamera();
    }
    walkFrame = requestAnimationFrame(walkStep);
  };
  const startWalk = () => {
    if (walking) return;
    closeAll();
    walkHome = { pos: camera.position.toArray(), tgt: controls.target.toArray() };
    const [x, z] = nearestLand(controls.target.x, controls.target.z);
    const v = controls.target.clone().sub(camera.position);
    yaw = Math.atan2(v.x, -v.z);
    pitch = 0;
    smoothY = groundAt(x, z) ?? meta.ground_m - meta.datum_m;
    controls.enabled = false;
    walking = true;
    glideId++;
    setOffset([0, 0]);
    camera.near = 0.3;
    camera.updateProjectionMatrix();
    camera.position.set(x, (smoothY + EYE) * state.vx, z);
    walkExit.hidden = walkTip.hidden = false;
    backBtn.hidden = true;
    updateLabels();
    applyWalkCamera();
    lastT = performance.now();
    walkFrame = requestAnimationFrame(walkStep);
  };
  const stopWalk = () => {
    if (!walking) return;
    walking = false;
    cancelAnimationFrame(walkFrame);
    keys.clear();
    controls.enabled = true;
    walkExit.hidden = walkTip.hidden = true;
    camera.position.set(...walkHome.pos);
    controls.target.set(...walkHome.tgt);
    controls.update();
    render();
  };
  walkBtn.onclick = startWalk;
  walkExit.onclick = () => (touring ? stopTour() : stopWalk());

  // Round 9: walk a route of data/routes_1860 at eye height (by boat 1.2 m above the water), pausing at its stops with their panel.
  // A camera fly-through along the line, no collision. Space pauses, the right arrow goes on to the next stop, Shift hurries, Esc stops.
  const TOUR_SPEED = { walk: 6, boat: 9 }, PAUSE_MS = 3500, BOAT_EYE = 1.2;
  const routeSel = document.getElementById("route");
  for (const f of routeFc.features) {
    const o = document.createElement("option");
    o.value = f.properties.id;
    o.textContent = f.properties.name_en;
    routeSel.append(o);
  }
  routeSel.onchange = () => { if (routeSel.value) startTour(routeSel.value, 0); };
  const lineOf = (f) => {
    const pts = f.geometry.coordinates.map(toXZ), cum = [0];
    for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    return { pts, cum, len: cum[cum.length - 1] };
  };
  const pointAt = (R, s) => {
    s = Math.max(0, Math.min(R.len, s));
    let i = 0;
    while (i < R.cum.length - 2 && R.cum[i + 1] < s) i++;
    const t = (s - R.cum[i]) / (R.cum[i + 1] - R.cum[i] || 1);
    return [R.pts[i][0] + (R.pts[i + 1][0] - R.pts[i][0]) * t, R.pts[i][1] + (R.pts[i + 1][1] - R.pts[i][1]) * t];
  };
  const eyeAt = (T, x, z) => (T.boat ? (waterLevelAt(x, z) ?? 0) + BOAT_EYE : (groundAt(x, z) ?? meta.ground_m - meta.datum_m) + EYE);
  const placeTour = (T) => {
    const [x, z] = pointAt(T.R, T.s);
    let ax = 0, az = 0;
    for (const d of [6, 10, 14, 18]) { const [px, pz] = pointAt(T.R, T.s + d); ax += px / 4; az += pz / 4; } // a smoothed look ahead
    if (Math.hypot(ax - x, az - z) < 1) [ax, az] = [x + Math.sin(T.yaw), z - Math.cos(T.yaw)];
    const y = eyeAt(T, x, z);
    let tx = ax, tz = az, ty = y;
    if (T.look) [tx, ty, tz] = T.look;
    T.yaw = Math.atan2(tx - x, -(tz - z));
    camera.position.set(x, y * state.vx, z);
    camera.lookAt(new THREE.Vector3(tx, ty * state.vx, tz));
    if (kitUpdate) kitUpdate(camera, shot ? 1e9 : 2);
    if (greensUpdate) greensUpdate(camera, shot ? 1e9 : 2);
    renderer.render(scene, camera);
  };
  const atStop = (T, st) => {
    T.look = null;
    const list = boxesOf(st.id);
    if (list.length) T.look = [list[0].cx, (list[0].y0 + list[0].y1) / 2, list[0].cz];
    else {
      const l = landingFc.features.find((f) => f.properties.id === st.id);
      if (l) { const [lx, lz] = toXZ(l.geometry.coordinates); T.look = [lx, eyeAt(T, lx, lz) - 0.5, lz]; }
    }
    walkTip.textContent = `${T.name} · ${st.name} · Space to pause · → next stop · Esc to stop`;
    if (shot) return;
    const id = st.id.startsWith("BR") ? null : st.id;
    if (id) panel.load(id).then((page) => { if (touring === T) { panel.show(page); halls.select(boxesOf(id)); } }).catch(() => {});
  };
  const tourStep = (now) => {
    const T = touring;
    if (!T) return;
    const dt = Math.min((now - T.last) / 1000, 0.1);
    T.last = now;
    if (!T.paused && now >= T.until) {
      if (T.look && now >= T.until) { T.look = null; walkTip.textContent = `${T.name} · Space to pause · → next stop · Esc to stop`; }
      T.s += TOUR_SPEED[T.boat ? "boat" : "walk"] * (keys.has("ShiftLeft") || keys.has("ShiftRight") ? 3 : 1) * dt;
      const st = T.stops.find((x) => !x.seen && x.along_m <= T.s);
      if (st) { st.seen = true; T.s = st.along_m; T.until = now + PAUSE_MS; atStop(T, st); }
      if (T.s >= T.R.len) { T.s = T.R.len; placeTour(T); walkTip.textContent = `${T.name} · the end · Esc to stop`; T.paused = true; }
    }
    placeTour(T);
    T.frame = requestAnimationFrame(tourStep);
  };
  function startTour(id, frac) {
    const f = routeFc.features.find((x) => x.properties.id === id);
    if (!f) return;
    if (walking) stopWalk();
    if (touring) stopTour(true);
    const home = touring ? touring.home : { pos: camera.position.toArray(), tgt: controls.target.toArray() };
    closeAll();
    const R = lineOf(f);
    const T = { id, name: f.properties.name_en, boat: f.properties.mode === "boat", R, s: R.len * (frac || 0), yaw: 0, look: null, paused: false, until: 0, last: performance.now(), home,
      stops: f.properties.stops.map((x) => ({ ...x, seen: x.along_m < R.len * (frac || 0) - 0.5 })) };
    touring = T;
    controls.enabled = false;
    glideId++;
    setOffset([0, 0]);
    camera.near = 0.3;
    camera.updateProjectionMatrix();
    walkExit.hidden = walkTip.hidden = false;
    backBtn.hidden = true;
    walkTip.textContent = `${T.name} · Space to pause · → next stop · Esc to stop`;
    routeSel.value = id;
    updateLabels();
    placeTour(T);
    if (!reduced()) T.frame = requestAnimationFrame(tourStep);
  }
  function stopTour(keepHome) {
    const T = touring;
    if (!T) return;
    cancelAnimationFrame(T.frame);
    touring = null;
    keys.clear();
    routeSel.value = "";
    walkExit.hidden = walkTip.hidden = true;
    panel.hide();
    halls.select([]);
    if (keepHome) return;
    controls.enabled = true;
    camera.position.set(...T.home.pos);
    controls.target.set(...T.home.tgt);
    controls.update();
    render();
  }
  const nextStop = () => {
    const T = touring, st = T && T.stops.find((x) => !x.seen);
    if (!T) return;
    if (!st) { T.s = T.R.len; placeTour(T); return; }
    st.seen = true;
    T.s = st.along_m;
    T.until = performance.now() + PAUSE_MS;
    atStop(T, st);
    placeTour(T);
  };
  addEventListener("keydown", (e) => {
    if (touring) {
      if (e.key === "Escape") { stopTour(); return; }
      if (e.code === "Space") { touring.paused = !touring.paused; touring.until = 0; e.preventDefault(); return; }
      if (e.code === "ArrowRight" || e.code === "KeyN") { nextStop(); e.preventDefault(); return; }
      keys.add(e.code);
      return;
    }
    if (!walking) return;
    if (e.key === "Escape") { stopWalk(); return; }
    keys.add(e.code);
    if (e.code.startsWith("Arrow")) e.preventDefault();
  });
  addEventListener("keyup", (e) => keys.delete(e.code));
  addEventListener("blur", () => keys.clear());

  let down = null;
  const el = renderer.domElement;
  el.addEventListener("pointerdown", (e) => { down = [e.clientX, e.clientY]; glideId++; label.hidden = true; });
  el.addEventListener("pointermove", (e) => {
    if (walking && e.buttons && down) {
      yaw += e.movementX * 0.003;
      pitch = Math.max(-1.2, Math.min(1.2, pitch - e.movementY * 0.003));
      applyWalkCamera();
    }
  });
  el.addEventListener("pointerup", (e) => {
    if (walking || touring || !down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4) return;
    const hit = hitAt(e);
    if (hit) open(hit.box.bid, hit.box);
    else { const ah = aroundAt(e); if (ah) open(ah.id); else { openToken++; closeAll(); } }
  });
  const labelOf = (b) => [b.props.name || "Hall without a name on the plan", b.props.assumed ? "(assumed)" : ""].filter(Boolean).join(" ");
  let hoverEvent = null;
  el.addEventListener("pointermove", (e) => {
    if (walking || touring || e.pointerType !== "mouse" || e.buttons) { label.hidden = true; return; }
    if (!hoverEvent) requestAnimationFrame(() => {
      const hit = hitAt(hoverEvent), ah = hit ? null : aroundAt(hoverEvent);
      el.style.cursor = hit || ah ? "pointer" : "";
      label.hidden = !hit && !ah;
      if (hit || ah) {
        label.textContent = hit ? labelOf(hit.box) : [ah.feature.name_zh, ah.feature.name_en || ah.feature.name_pinyin, ah.feature.assumed ? "(assumed)" : ""].filter(Boolean).join(" ");
        label.style.left = `${Math.min(hoverEvent.clientX + 14, innerWidth - label.offsetWidth - 8)}px`;
        label.style.top = `${hoverEvent.clientY + 16}px`;
      }
      hoverEvent = null;
    });
    hoverEvent = e;
  });
  el.addEventListener("pointerleave", () => { label.hidden = true; });

  const cam = (params.get("cam") || "30,1560,1980,30,0,-40").split(",").map(Number);
  camera.position.set(...cam.slice(0, 3));
  controls.target.set(...cam.slice(3, 6));
  controls.update();
  apply();
  const deep = params.get("b");
  if (deep) await open(deep.toUpperCase());
  await modelsReady;
  if (params.get("plate")) await plateMode(params.get("plate").toUpperCase(), params.get("platefit") || "all");
  { const ld = document.getElementById("loading"); if (ld && !window.__loaderOn) ld.hidden = true; } // loading.js (when on) closes its own card
  const routeParam = params.get("route");
  if (routeParam) startTour(routeParam.toUpperCase(), Number(params.get("routet") || 0));
  window.viewer = { around, detailed, preview, modelFor, kit, greens, state, apply, scene, camera, controls, render, open, close: closeAll, halls, byBuilding, byParent, byBoxId, boxesOf, groundAt, waterLevelAt, ground, meta, toXZ, renderer, walk: { start: startWalk, stop: stopWalk }, tour: { start: startTour, stop: stopTour, next: nextStop, get: () => touring }, keys, setOffset, ways };
  window.__ready = true;
}

// Round 13: ?plate=<photo id>. The canvas takes the picture's proportions in the top left of the window; the camera is the fitted one (tools/plate_overlay.py: pinhole, no roll; principal point offset as a view offset).
async function plateMode(pid, fit) {
  const data = await fetch("data/plates.json").then((r) => r.json());
  const e = data.plates[pid];
  if (!e || !e.fits[fit]) { console.warn("No fitted camera for", pid, fit); window.__plateReady = true; return; }
  const F = e.fits[fit], [W, H] = e.size;
  let w = innerWidth, h = Math.round((innerWidth * H) / W);
  if (h > innerHeight) { h = innerHeight; w = Math.round((innerHeight * W) / H); }
  renderer.setSize(w, h);
  camera.aspect = W / H;
  camera.fov = (2 * Math.atan(H / 2 / F.f_px) * 180) / Math.PI;
  camera.setViewOffset(W, H, -F.du_px, -F.dv_px, W, H);
  camera.updateProjectionMatrix();
  setOffset = () => {}; // the panel's offset would move the picture
  plateLock = true;
  const yaw = (F.yaw_deg * Math.PI) / 180, pitch = (F.pitch_deg * Math.PI) / 180;
  const dir = new THREE.Vector3(Math.sin(yaw) * Math.cos(pitch), Math.sin(pitch), -Math.cos(yaw) * Math.cos(pitch));
  const C = new THREE.Vector3(...F.position);
  controls.enabled = false;
  camera.position.copy(C);
  controls.target.copy(C.clone().add(dir.multiplyScalar(20)));
  camera.lookAt(controls.target);
  camera.near = 0.5;
  camera.updateProjectionMatrix();
  if (F.k_vertical && F.k_vertical !== 1) {
    // fit `stretch`: the plate draws heights k times its widths (tools/plate_overlay.py); kept until the next projection update
    camera.projectionMatrix.elements[5] *= F.k_vertical;
    camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
  }
  const img = document.getElementById("plate-img"), ui = document.getElementById("plate-ui");
  if (params.get("plateimg") !== "0") {
    img.src = e.image;
    Object.assign(img.style, { left: "0px", top: "0px", width: `${w}px`, height: `${h}px`, display: "block" });
    ui.style.display = "block";
    ui.innerHTML = `<b>${pid}</b>${e.plate ? ` (plate ${e.plate})` : ""}, ${e.object}: camera fitted to ${fit === "anchored" ? "the anchored points" : fit === "stretch" ? `every point, heights drawn ${F.k_vertical} times the widths` : "every point"}, ${F.rms_px} px rms (research/xiyanglou/plate_fit_${e.object}.csv)<br><label>Picture <input id="plate-op" type="range" min="0" max="100" value="50"></label><label><input id="plate-fit" type="checkbox" ${fit === "anchored" ? "checked" : ""}> anchored camera</label>`;
    document.getElementById("plate-op").oninput = (ev) => { img.style.opacity = ev.target.value / 100; };
    document.getElementById("plate-fit").onchange = (ev) => { const u = new URL(location.href); u.searchParams.set("platefit", ev.target.checked ? "anchored" : "all"); location.href = u; };
  }
  render();
  await new Promise((r) => requestAnimationFrame(r));
  render();
  window.__plateReady = true;
}

main();
