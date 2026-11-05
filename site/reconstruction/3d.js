// 3D preview of the three gardens before October 1860, real scale. A preview: not the project's final engine. Rendered on demand, not in a loop.
// Data: generated/ground.json + ground.bin (scripts/ground1860.py), generated/structures.json and data/halls_1860.geojson (scripts/boxes1860.py), data/buildings/<ID>.json (scripts/building_pages.py), data/labels_1860.json.
// World axes: x = east, z = south, y = height above the water, metres. Halls are one merged mesh (halls3d.js); a click tests rectangles, not triangles.
// URL: ?b=<ID> (opens that page and frames its object) &cam=x,y,z,tx,ty,tz &halls=0 &walls=0 &labels=0 &conf=1 &vx=2 &shot=1 (hides the panels, nothing animates, no labels) &public=1 (localhost: no research copy of the pages).
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
scene.fog = new THREE.Fog(SKY, 5000, 24000);
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
function fitNearPlane() {
  const room = camera.position.y - ABOVE_ALL_M * world.scale.y;
  const near = Math.max(0.5, Math.min(room * 0.6, camera.position.distanceTo(controls.target) * 0.4));
  if (Math.abs(near - camera.near) > 0.05 * camera.near) { camera.near = near; camera.updateProjectionMatrix(); }
}
let labels = [];
function updateLabels() {
  const on = state.labels && !shot && !walking && !touring;
  for (const l of labels) {
    const d = camera.position.distanceTo(l.position);
    l.visible = on && (l.userData.rank === 1 ? d > 700 : d < 1400);
  }
}
function render() {
  fitNearPlane();
  updateLabels();
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

const state = { halls: params.get("halls") !== "0", walls: params.get("walls") !== "0", labels: params.get("labels") !== "0", conf: params.get("conf") === "1", vx: Number(params.get("vx") || 1), paths: params.get("paths") !== "0", assumed: params.get("assumed") !== "0" };
const meshes = {};
let walking = false, touring = null;

// Ground, from the binary parts of ground1860.py.
function partGeometry(buf, part, withRgb) {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(buf, part.pos, part.verts * 3), 3));
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, part.idx, part.indices), 1));
  if (withRgb) {
    // Vertex colours are not colour-managed: the file's sRGB goes to linear here, as the hex colours of the materials do on their own.
    const toLinear = new Float32Array(256).map((_, i) => { const f = i / 255; return f <= 0.04045 ? f / 12.92 : ((f + 0.055) / 1.055) ** 2.4; });
    const raw = new Uint8Array(buf, part.rgb, part.verts * 3), rgb = new Float32Array(raw.length);
    for (let i = 0; i < raw.length; i++) rgb[i] = toLinear[raw[i]];
    g.setAttribute("color", new THREE.BufferAttribute(rgb, 3));
  }
  g.computeVertexNormals();
  return g;
}
function buildGround(meta, buf) {
  const group = new THREE.Group();
  const lam = (o) => new THREE.MeshLambertMaterial(o);
  group.add(new THREE.Mesh(partGeometry(buf, meta.parts.land, true), lam({ vertexColors: true })));
  group.add(new THREE.Mesh(partGeometry(buf, meta.parts.bank, false), lam({ color: 0x8b8474, side: THREE.DoubleSide })));
  group.add(new THREE.Mesh(partGeometry(buf, meta.parts.water, false), lam({ color: 0x6f9fb0 })));
  group.add(new THREE.Mesh(partGeometry(buf, meta.parts.paddy, false), lam({ color: 0xa8b98a })));
  // The plain past the modelled land: a ring round it, a hair lower so the seam never fights. Same colour as the land outside the walls.
  const base = meta.ground_m - meta.datum_m - 0.05, [x0, z0, x1, z1] = meta.domain, FAR = 45000;
  for (const [ax, az, bx, bz] of [[-FAR, -FAR, FAR, z0], [-FAR, z1, FAR, FAR], [-FAR, z0, x0, z1], [x1, z0, FAR, z1]]) {
    group.add(new THREE.Mesh(new THREE.PlaneGeometry(bx - ax, bz - az).rotateX(-Math.PI / 2).translate((ax + bx) / 2, base, (az + bz) / 2), lam({ color: 0xaaa47c })));
  }
  return group;
}

// Walls as thin solids, bridges as decks. One mesh each. Bridges with a row in buildings.csv are clickable through `bridgeBoxes`.
function buildStructures(data) {
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
  for (const [ax, az, bx, bz, y0, y1] of data.wall.segments) pushBox(wall, ax, az, bx, bz, half, y0, y1);
  const wallGeo = new THREE.BufferGeometry();
  wallGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(wall), 3));
  wallGeo.computeVertexNormals();
  group.add(new THREE.Mesh(wallGeo, new THREE.MeshLambertMaterial({ color: 0x8c8378, side: THREE.DoubleSide })));
  const deck = [];
  for (const b of data.bridges) {
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
  const [meta, buf, gridBuf, fc, structures, labelData, pathFc, landingFc, routeFc] = await Promise.all([
    fetch("generated/ground.json").then((r) => r.json()),
    fetch("generated/ground.bin").then((r) => r.arrayBuffer()),
    fetch("generated/ground_grid.i16").then((r) => r.arrayBuffer()),
    fetch("data/halls_1860.geojson").then((r) => r.json()),
    fetch("generated/structures.json").then((r) => r.json()),
    fetch("data/labels_1860.json").then((r) => r.json()),
    fetch("data/paths_1860.geojson").then((r) => r.json()),
    fetch("data/landings_1860.geojson").then((r) => r.json()),
    fetch("data/routes_1860.geojson").then((r) => r.json()),
  ]);
  const a = meta.lonlat;
  const toXZ = ([lon, lat]) => [a.x[0] + a.x[1] * (lon - a.lon0) + a.x[2] * (lat - a.lat0), a.z[0] + a.z[1] * (lon - a.lon0) + a.z[2] * (lat - a.lat0)];
  const grid = new Int16Array(gridBuf), G = meta.grid;
  const groundAt = (x, z) => {
    const i = Math.round((x - G.x0) / G.step_m), j = Math.round((z - G.z0) / G.step_m);
    if (i < 0 || j < 0 || i >= G.width || j >= G.height) return meta.ground_m - meta.datum_m;
    const v = grid[j * G.width + i];
    return v === G.no_land ? null : v / 100;
  };

  world.add(buildGround(meta, buf));
  meshes.structures = buildStructures(structures);
  world.add(meshes.structures);
  const halls = buildHalls({ fc, toXZ, datum: meta.datum_m });
  const ways = buildPaths({ paths: pathFc, landings: landingFc, toXZ, groundAt, base: meta.ground_m - meta.datum_m });
  for (const g of Object.values(ways.groups)) world.add(g);
  meshes.halls = halls.mesh;
  world.add(meshes.halls);
  labels = labelData.map((l) => {
    const s = labelSprite(l.zh, l.en, l.rank);
    const [x, z] = toXZ([l.lon, l.lat]);
    s.position.set(x, l.rank === 1 ? 42 : 20, z);
    s.userData = { rank: l.rank, id: l.id };
    world.add(s);
    return s;
  });

  function apply() {
    meshes.halls.visible = state.halls;
    meshes.structures.visible = state.walls;
    ways.groups.sure.visible = ways.groups.boat.visible = state.paths;
    ways.groups.assumed.visible = state.paths && state.assumed;
    ways.setConfMode(state.conf);
    document.getElementById("legend-paths").hidden = !state.paths;
    world.scale.y = state.vx;
    world.updateMatrixWorld(true);
    halls.setConfMode(state.conf);
    document.getElementById("legend-plain").hidden = state.conf;
    document.getElementById("legend-conf").hidden = !state.conf;
    render();
  }
  for (const key of ["halls", "walls", "labels", "conf", "paths", "assumed"]) {
    const box = document.getElementById(key);
    box.checked = state[key];
    box.onchange = (e) => { state[key] = e.target.checked; apply(); };
  }
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

  const panel = createBuildingPanel({ local, onClose: () => closeAll(), onOpen: (id) => open(id), onRoute: (id) => startTour(id, 0) });
  const label = document.getElementById("hover");
  const ray = new THREE.Raycaster();
  const rayAt = (e) => {
    const r = renderer.domElement.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
    if (state.vx !== 1) { ray.ray.origin.y /= state.vx; ray.ray.direction.y /= state.vx; ray.ray.direction.normalize(); }
    return ray.ray;
  };
  const hitAt = (e) => (state.halls ? halls.pick(rayAt(e)) : null);

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
  const eyeAt = (T, x, z) => (T.boat ? BOAT_EYE : (groundAt(x, z) ?? meta.ground_m - meta.datum_m) + EYE);
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
    else { openToken++; closeAll(); }
  });
  const labelOf = (b) => [b.props.name || "Hall without a name on the plan", b.props.assumed ? "(assumed)" : ""].filter(Boolean).join(" ");
  let hoverEvent = null;
  el.addEventListener("pointermove", (e) => {
    if (walking || touring || e.pointerType !== "mouse" || e.buttons) { label.hidden = true; return; }
    if (!hoverEvent) requestAnimationFrame(() => {
      const hit = hitAt(hoverEvent);
      el.style.cursor = hit ? "pointer" : "";
      label.hidden = !hit;
      if (hit) {
        label.textContent = labelOf(hit.box);
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
  document.getElementById("loading").hidden = true;
  const routeParam = params.get("route");
  if (routeParam) startTour(routeParam.toUpperCase(), Number(params.get("routet") || 0));
  window.viewer = { state, apply, scene, camera, controls, render, open, close: closeAll, halls, byBuilding, byParent, byBoxId, boxesOf, groundAt, toXZ, renderer, walk: { start: startWalk, stop: stopWalk }, tour: { start: startTour, stop: stopTour, next: nextStop, get: () => touring }, keys, setOffset, ways };
  window.__ready = true;
}

main();
