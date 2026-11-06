// Round 12: the planting of 1860 and the rockeries, from data/greens_1860.json and generated/greens_1860.bin (scripts/greens1860.py). Classic script, loaded before 3d.js; defines the global buildGreens.
// Plants: one record of 14 bytes each (see the json's note). The places are generated, never surveyed (no plan draws a plant); each area keeps a grade for its extent and one for its species.
// Drawn as instances by form: a far level for the whole site (one InstancedMesh per form, a few triangles a plant, no trunks), and a near level built for the tiles within NEAR_M of the camera
// (crowns of several lobes, trunks, lotus pads and flowers); a tile drawn near hides its plants in the far level. Plants stand on the walk surface they were placed on (ground1860.py's lattice);
// a trunk goes TRUNK_SINK_M into the ground, so a slope under it shows no gap. Rockeries: lumpy masses from their base (the lowest ground or bed under them, so a shore rockery runs into the water) to their top.
// Options: setSeason(spring|summer|autumn|winter), setView({ on, assumed, conf }): assumed=false hides the generated fill and lowers plants on generated hills by what the hill adds; conf tints by the species' grade.
const GREENS_TILE = 200, GREENS_NEAR = 260; // shrubs and floating leaves have no far level: past the near tiles they are under a pixel
const GREEN_BASE = { pine: 0x3c5a34, cypress: 0x3e5537, willow: 0x89a35a, broad: 0x5b7a3f, blossom: 0x6f8a49, bamboo: 0x6a8e3d, shrub: 0x5d7b3e, topiary: 0x48683a, hedge: 0x46633a, lotus: 0x5b8c44, floating: 0x6a8b49, reed: 0x7b8f50 };
const GREEN_BLOOM = { pink: 0xeeb2c2, pale: 0xf1d9d6, white: 0xf3efe4, red: 0xc0485e };
const GREEN_AUTUMN = { yellow: 0xc4a23f, red: 0xaa4a2d, gold: 0xd0a13a, brown: 0x8c7448, straw: 0xc0aa6c };
const GREEN_SPRING = { willow: 0xa6c266, broad: 0x7c9e4d, reed: 0x8da35a, lotus: 0x6f9b4c, floating: 0x76964f };
const GREEN_WINTER = { willow: 0x9a8f62, broad: 0x7e7062, blossom: 0x7a6b5d, shrub: 0x7d6f5a, reed: 0xb6a173, floating: null, lotus: null, pine: 0x37522f, cypress: 0x3a4f34, bamboo: 0x5f7f3a };
const GREEN_CONF = { 0: 0x2f8f4e, 1: 0xd9a441, 2: 0xc4513a, assumed: 0xd8bfae };
const GREEN_TRUNK = 0x5a4a3a, ROCK_COLOURS = { standing: 0xaaa79d, screen: 0xa3a197, shore: 0x9e9b90, hill: 0xa09888 };
const GREEN_TREES = new Set(["pine", "cypress", "willow", "broad", "blossom", "topiary"]);
const GREEN_WATER = new Set(["lotus", "floating", "reed"]);
// Where the trunk stops (share of the height) and its girth (share of the height): a pine shows a long trunk under its tiers, a blossom tree a short one.
const GREEN_TRUNKS = { pine: [0.7, 0.035], cypress: [0.3, 0.03], willow: [0.45, 0.05], broad: [0.5, 0.04], blossom: [0.4, 0.05], topiary: [0.2, 0.05] };

// Unit plants: base at y = 0, 1 high (the plant's height) and 1 across (its crown). Faceted on purpose: flat-shaded, a model not a photo.
function greenGeometries() {
  const merge = (parts) => {
    const pos = [];
    for (const g0 of parts) { const g = g0.index ? g0.toNonIndexed() : g0, a = g.getAttribute("position"); for (let i = 0; i < a.count; i++) pos.push(a.getX(i), a.getY(i), a.getZ(i)); }
    const out = new THREE.BufferGeometry();
    out.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
    out.computeVertexNormals();
    return out;
  };
  const lobe = (x, y, z, sx, sy, sz, detail = 0, Geo = THREE.IcosahedronGeometry) => { const g = new Geo(0.5, detail); g.scale(sx, sy, sz); g.translate(x, y, z); return g; };
  const disc = (x, y, z, r, tilt, seg = 7) => { const g = new THREE.CircleGeometry(r, seg); g.rotateX(-Math.PI / 2 + tilt); g.translate(x, y, z); return g; };
  const blades = (n) => {
    const out = [];
    for (let i = 0; i < n; i++) {
      const a = (i * 2.399) % (2 * Math.PI), r = 0.12 + 0.3 * ((i * 0.618) % 1), lean = 0.12 + 0.1 * ((i * 0.37) % 1), h = 0.7 + 0.3 * ((i * 0.53) % 1);
      const x = Math.cos(a) * r, z = Math.sin(a) * r, w = 0.05;
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array([x - w * Math.sin(a), 0, z + w * Math.cos(a), x + w * Math.sin(a), 0, z - w * Math.cos(a), x + Math.cos(a) * lean, h, z + Math.sin(a) * lean]), 3));
      out.push(g);
    }
    return out;
  };
  const near = {
    pine: merge([lobe(0, 0.68, 0, 1.0, 0.22, 0.92), lobe(0.08, 0.88, -0.05, 0.62, 0.18, 0.58)]),
    cypress: merge([lobe(0, 0.55, 0, 1.0, 0.9, 1.0), lobe(0, 0.92, 0, 0.5, 0.2, 0.5, 0, THREE.OctahedronGeometry)]),
    willow: merge([lobe(0, 0.84, 0, 0.82, 0.3, 0.82, 0, THREE.OctahedronGeometry), ...[0, 1, 2, 3].map((k) => { const a = k * 1.5708 + 0.4; return lobe(Math.cos(a) * 0.28, 0.6, Math.sin(a) * 0.28, 0.4, 0.62, 0.4, 0, THREE.OctahedronGeometry); })]),
    broad: merge([lobe(0, 0.7, 0, 0.92, 0.55, 0.9), lobe(0.2, 0.84, 0.12, 0.55, 0.36, 0.55)]),
    blossom: merge([lobe(0, 0.66, 0, 1.0, 0.62, 0.95), lobe(0.15, 0.82, -0.1, 0.55, 0.4, 0.55)]),
    bamboo: merge([lobe(0, 0.5, 0, 0.42, 1.0, 0.42, 0, THREE.OctahedronGeometry), lobe(0.28, 0.45, 0.12, 0.36, 0.88, 0.36, 0, THREE.OctahedronGeometry), lobe(-0.22, 0.44, 0.2, 0.34, 0.86, 0.34, 0, THREE.OctahedronGeometry), lobe(-0.05, 0.42, -0.3, 0.36, 0.84, 0.36, 0, THREE.OctahedronGeometry)]),
    shrub: merge([lobe(0, 0.45, 0, 1.0, 0.95, 1.0)]),
    topiary: merge([lobe(0, 0.38, 0, 1.0, 0.36, 1.0, 0, THREE.OctahedronGeometry), lobe(0, 0.68, 0, 0.72, 0.3, 0.72, 0, THREE.OctahedronGeometry), lobe(0, 0.9, 0, 0.42, 0.22, 0.42, 0, THREE.OctahedronGeometry)]),
    hedge: (() => { const g = new THREE.BoxGeometry(1, 1, 1); g.translate(0, 0.5, 0); return g.index ? g.toNonIndexed() : g; })(),
    lotus: merge([disc(0, 0.06, 0, 0.27, 0.1, 6), disc(0.3, 0.03, 0.12, 0.21, -0.08, 5), disc(-0.26, 0.15, 0.2, 0.22, 0.2, 5)]),
    floating: merge([disc(0, 0.02, 0, 0.18, 0, 5), disc(0.28, 0.02, 0.15, 0.14, 0, 5), disc(-0.18, 0.02, 0.24, 0.13, 0, 5)]),
    reed: merge(blades(6)),
  };
  // The far level: a blunt four-sided lump of 8 triangles (a ring low in the crown, a short top, a point below), turned per plant, so a far crown reads round, not as a diamond.
  const lump = (y0, yMid, y1) => {
    // a square ring low in the crown, a smaller square top turned 45 degrees, a point below: 14 triangles, wound outwards; an octagon's outline from most sides
    const ring = [[0.5, 0], [0, 0.5], [-0.5, 0], [0, -0.5]].map(([a, b]) => [a, yMid, b]), top = [[0.25, 0.25], [-0.25, 0.25], [-0.25, -0.25], [0.25, -0.25]].map(([a, b]) => [a, y1, b]);
    const bot = [0, y0, 0], c = [0, (y0 + y1) / 2, 0], pos = [];
    const t3 = (p, q, r) => {
      const u = [q[0] - p[0], q[1] - p[1], q[2] - p[2]], v = [r[0] - p[0], r[1] - p[1], r[2] - p[2]], n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      const m = [(p[0] + q[0] + r[0]) / 3 - c[0], (p[1] + q[1] + r[1]) / 3 - c[1], (p[2] + q[2] + r[2]) / 3 - c[2]];
      if (n[0] * m[0] + n[1] * m[1] + n[2] * m[2] < 0) pos.push(...p, ...r, ...q); else pos.push(...p, ...q, ...r);
    };
    t3(top[0], top[1], top[2]); t3(top[0], top[2], top[3]);
    for (let k = 0; k < 4; k++) { const j = (k + 1) % 4; t3(ring[k], top[k], ring[j]); t3(top[(k + 3) % 4], top[k], ring[k]); t3(ring[k], ring[j], bot); }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
    return g;
  };
  const tri = (r, y) => { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array([0, y, -r, -r * 0.87, y, r * 0.5, r * 0.87, y, r * 0.5]), 3)); g.computeVertexNormals(); return g; };
  const far = {
    pine: lump(0.55, 0.82, 1.0),
    cypress: lump(0.1, 0.55, 1.0),
    willow: lump(0.25, 0.78, 1.0),
    broad: lump(0.3, 0.76, 1.0),
    blossom: lump(0.3, 0.74, 1.0),
    bamboo: lump(0.0, 0.6, 1.0),
    shrub: lump(0.0, 0.6, 1.0),
    topiary: lump(0.0, 0.5, 1.0),
    hedge: near.hedge,
    lotus: tri(0.62, 0.04),
    floating: tri(0.5, 0.02),
    reed: merge([(() => { const g = new THREE.PlaneGeometry(0.9, 1); g.translate(0, 0.5, 0); return g; })()]),
  };
  const flat = (g) => (g.index ? g.toNonIndexed() : g);
  const trunk = flat(new THREE.CylinderGeometry(0.42, 0.5, 1, 4, 1, true));
  trunk.translate(0, 0.5, 0);
  const flower = flat(lobe(0, 0.34, 0, 0.16, 0.16, 0.16, 0, THREE.OctahedronGeometry));
  flower.computeVertexNormals();
  return { near, far, trunk, flower };
}

function buildGreens({ meta, buf, datum, toXZ }) {
  const group = new THREE.Group();
  const N = meta.count, dv = new DataView(buf), [X0, Z0] = meta.domain, SINK = meta.trunk_sink_m;
  const P = { x: new Float32Array(N), z: new Float32Array(N), y: new Float32Array(N), area: new Uint16Array(N), sp: new Uint8Array(N), h: new Float32Array(N), c: new Float32Array(N), f: new Uint8Array(N), lift: new Float32Array(N) };
  for (let i = 0, o = 0; i < N; i++, o += meta.record_bytes) {
    P.x[i] = X0 + dv.getUint16(o, true) / 10; P.z[i] = Z0 + dv.getUint16(o + 2, true) / 10; P.y[i] = dv.getInt16(o + 4, true) / 100;
    P.area[i] = dv.getUint16(o + 6, true); P.sp[i] = dv.getUint8(o + 8); P.h[i] = dv.getUint8(o + 9) / 10; P.c[i] = dv.getUint8(o + 10) / 10; P.f[i] = dv.getUint8(o + 11); P.lift[i] = dv.getUint8(o + 12) / 10;
  }
  const species = meta.species, formOf = (i) => species[P.sp[i]].form;
  const geos = greenGeometries();
  // Baked, not instanced: software WebGL draws a merged mesh several times faster than the same triangles instanced. No normal attribute: flat shading takes it from the faces.
  const mat = new THREE.MeshLambertMaterial({ flatShading: true, vertexColors: true });
  const waterMat = new THREE.MeshLambertMaterial({ flatShading: true, vertexColors: true, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
  const view = { on: true, assumed: true, conf: false, season: "summer" };
  const tileOf = (i) => Math.floor((P.x[i] - X0) / GREENS_TILE) * 1000 + Math.floor((P.z[i] - Z0) / GREENS_TILE);
  const unit = (g) => g.getAttribute("position").array;
  const U = { near: Object.fromEntries(Object.entries(geos.near).map(([k, g]) => [k, unit(g)])), far: Object.fromEntries(Object.entries(geos.far).map(([k, g]) => [k, unit(g)])), trunk: unit(geos.trunk), flower: unit(geos.flower) };

  // Per plant: hidden (the fill with assumed off, lotus in winter), its height on the view's ground, its colour.
  const hidden = (i) => (!view.assumed && P.f[i] & 1) || (view.season === "winter" && (formOf(i) === "lotus" || formOf(i) === "floating"));
  const baseY = (i) => P.y[i] - (!view.assumed && P.f[i] & 32 ? P.lift[i] : 0);
  const col = new THREE.Color(), jitter = (i) => 0.94 + 0.12 * (((i * 2654435761) >>> 0) / 4294967296);
  const colourOf = (i) => {
    const s = species[P.sp[i]], form = s.form;
    if (view.conf) return col.set(P.f[i] & 1 ? GREEN_CONF.assumed : GREEN_CONF[(P.f[i] >> 1) & 3]);
    let hex = GREEN_BASE[form];
    if (view.season === "spring") hex = (s.bloom && (form === "blossom" || form === "shrub")) ? GREEN_BLOOM[s.bloom] : (GREEN_SPRING[form] ?? hex);
    else if (view.season === "summer" && form === "shrub" && s.bloom) hex = GREEN_BLOOM[s.bloom];
    else if (view.season === "autumn" && s.autumn && !["pine", "cypress", "bamboo", "topiary", "hedge"].includes(form)) hex = GREEN_AUTUMN[s.autumn];
    else if (view.season === "winter") hex = GREEN_WINTER[form] ?? hex;
    return col.set(hex).multiplyScalar(jitter(i));
  };
  const tiles = new Map(); // tile -> { list, far, near }
  for (let i = 0; i < N; i++) { const t = tileOf(i); if (!tiles.has(t)) tiles.set(t, { list: [], far: null, near: null }); tiles.get(t).list.push(i); }

  // One tile at one level: a land mesh and a water mesh, every plant's unit form turned, scaled and moved into place, with its colour.
  const bake = (list, near) => {
    const parts = { land: [], water: [] };
    let nLand = 0, nWater = 0;
    const jobs = [];
    for (const i of list) {
      if (hidden(i)) continue;
      const form = formOf(i), water = GREEN_WATER.has(form);
      if (!near && (form === "shrub" || form === "floating")) continue; // under a pixel past the near tiles
      const crown = (near ? U.near : U.far)[form];
      const job = { i, form, water, crown, trunk: near && GREEN_TREES.has(form), flower: near && form === "lotus" && view.season === "summer" && i % 3 === 0 };
      const n = crown.length / 3 + (job.trunk ? U.trunk.length / 3 : 0) + (job.flower ? U.flower.length / 3 : 0);
      if (water) nWater += n; else nLand += n;
      jobs.push(job);
    }
    const buf = { land: { pos: new Float32Array(nLand * 3), col: new Uint8Array(nLand * 3), k: 0 }, water: { pos: new Float32Array(nWater * 3), col: new Uint8Array(nWater * 3), k: 0 } };
    const put = (B, src, x, y, z, sx, sy, sz, cosA, sinA, r, g, b) => {
      for (let v = 0; v < src.length; v += 3) {
        const ux = src[v] * sx, uy = src[v + 1] * sy, uz = src[v + 2] * sz, k = B.k;
        B.pos[3 * k] = x + ux * cosA + uz * sinA; B.pos[3 * k + 1] = y + uy; B.pos[3 * k + 2] = z - ux * sinA + uz * cosA;
        B.col[3 * k] = r; B.col[3 * k + 1] = g; B.col[3 * k + 2] = b;
        B.k++;
      }
    };
    const trunkC = new THREE.Color(GREEN_TRUNK), flowerC = new THREE.Color(GREEN_BLOOM.pink);
    for (const j of jobs) {
      const i = j.i, B = j.water ? buf.water : buf.land, a = (i * 2.399) % (2 * Math.PI), cosA = Math.cos(a), sinA = Math.sin(a);
      const w = P.c[i] * (view.season === "winter" && ["broad", "blossom", "willow", "shrub"].includes(j.form) ? 0.82 : 1), h = j.water && j.form !== "reed" ? 1 : P.h[i], y = baseY(i) + (j.water ? 0.01 : 0);
      const c = colourOf(i), r = Math.round(c.r * 255), g = Math.round(c.g * 255), b = Math.round(c.b * 255);
      put(B, j.crown, P.x[i], y, P.z[i], w, h, w, cosA, sinA, r, g, b);
      if (j.trunk) {
        const [top, girth] = GREEN_TRUNKS[j.form], d = Math.max(P.h[i] * girth, 0.18);
        const tc = view.conf ? c : trunkC;
        put(B, U.trunk, P.x[i], y - SINK, P.z[i], d, P.h[i] * top + SINK, d, cosA, sinA, Math.round(tc.r * 255), Math.round(tc.g * 255), Math.round(tc.b * 255));
      }
      if (j.flower) { const fc = view.conf ? c : flowerC; put(B, U.flower, P.x[i], y, P.z[i], w, 1, w, cosA, sinA, Math.round(fc.r * 255), Math.round(fc.g * 255), Math.round(fc.b * 255)); }
    }
    const g = new THREE.Group();
    for (const [key, m] of [["land", mat], ["water", waterMat]]) {
      const B = buf[key];
      if (!B.k) continue;
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.BufferAttribute(B.pos, 3));
      geo.setAttribute("color", new THREE.BufferAttribute(B.col, 3, true));
      geo.computeBoundingSphere();
      const mesh = new THREE.Mesh(geo, m);
      mesh.raycast = () => {};
      g.add(mesh);
    }
    return g;
  };
  const dispose = (g) => g && g.traverse((o) => { if (o.isMesh) o.geometry.dispose(); });
  const buildFar = () => {
    for (const T of tiles.values()) {
      if (T.far) { group.remove(T.far); dispose(T.far); }
      T.far = bake(T.list, false);
      T.far.visible = !T.near;
      group.add(T.far);
    }
  };
  const dropNear = (T) => { if (!T.near) return; group.remove(T.near); dispose(T.near); T.near = null; T.far.visible = true; };

  // Called before each frame: the tiles within reach drawn near, at most `budget` new ones a frame. True while some still wait.
  const centre = (t) => [X0 + (Math.floor(t / 1000) + 0.5) * GREENS_TILE, Z0 + ((t % 1000) + 0.5) * GREENS_TILE];
  const update = (camera, budget = 3) => {
    if (!view.on) return false;
    const cx = camera.position.x, cz = camera.position.z, want = [];
    for (const t of tiles.keys()) {
      const [x, z] = centre(t), d = Math.max(Math.abs(x - cx), Math.abs(z - cz)) - GREENS_TILE / 2;
      if (d < GREENS_NEAR && camera.position.y < 1600) want.push([d, t]);
    }
    const keep = new Set(want.map((w) => w[1]));
    for (const [t, T] of tiles) if (T.near && !keep.has(t)) dropNear(T);
    want.sort((a, b) => a[0] - b[0]);
    let built = 0;
    for (const [, t] of want) {
      const T = tiles.get(t);
      if (T.near) continue;
      if (built >= budget) return true;
      T.near = bake(T.list, true);
      group.add(T.near);
      T.far.visible = false;
      built++;
    }
    return false;
  };
  const rebuildAll = () => {
    for (const T of tiles.values()) dropNear(T);
    buildFar();
  };
  buildFar();

  // Rockeries: lumps from base to top, seeded per rockery.
  const rocks = new THREE.Group(), rockMeshes = [];
  {
    const pos = [], cols = [], grades = [];
    const rnd = (s) => { let x = s >>> 0; return () => ((x = (x * 1664525 + 1013904223) >>> 0) / 4294967296); };
    const inside = (ring, x, z) => { let on = false; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) if ((ring[i][1] > z) !== (ring[j][1] > z) && x < ((ring[j][0] - ring[i][0]) * (z - ring[i][1])) / (ring[j][1] - ring[i][1]) + ring[i][0]) on = !on; return on; };
    for (const r of meta.rocks) {
      const ring = r.ring.map(([x, z]) => [X0 + x / 10, Z0 + z / 10]), y0 = r.y0 / 100, y1 = r.y1 / 100, R = rnd(r.s + 7);
      let area = 0; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) area += (ring[j][0] + ring[i][0]) * (ring[j][1] - ring[i][1]); area = Math.abs(area / 2);
      const xs = ring.map((p) => p[0]), zs = ring.map((p) => p[1]), bx0 = Math.min(...xs), bx1 = Math.max(...xs), bz0 = Math.min(...zs), bz1 = Math.max(...zs);
      const n = r.k === "standing" ? 1 : Math.max(2, Math.min(40, Math.round(area / (r.k === "hill" ? 9 : 5))));
      const rad = r.k === "standing" ? Math.sqrt(area / Math.PI) : Math.sqrt(area / n) * 0.72;
      const cx = (bx0 + bx1) / 2, cz = (bz0 + bz1) / 2, span = Math.max(bx1 - bx0, bz1 - bz0) / 2;
      const hex = ROCK_COLOURS[r.k] || ROCK_COLOURS.standing;
      for (let k = 0, tries = 0; k < n && tries < n * 40; tries++) {
        const x = r.k === "standing" ? cx : bx0 + R() * (bx1 - bx0), z = r.k === "standing" ? cz : bz0 + R() * (bz1 - bz0);
        const rr = rad * (0.75 + 0.5 * R());
        if (r.k !== "standing" && ![[0, 0], [0.7, 0], [-0.7, 0], [0, 0.7], [0, -0.7]].every(([a, b]) => inside(ring, x + a * rr, z + b * rr))) continue;
        k++;
        // taller towards the middle of a hill, a standing stone its full height, shore work low
        const centreK = r.k === "hill" ? 1 - 0.6 * Math.min(1, Math.hypot(x - cx, z - cz) / (span || 1)) : 1;
        const top = y0 + (y1 - y0) * (r.k === "standing" ? 1 : (0.55 + 0.45 * R()) * centreK);
        const g0 = new THREE.IcosahedronGeometry(1, r.k === "standing" || r.k === "screen" ? 1 : 0), g = g0.index ? g0.toNonIndexed() : g0, a = g.getAttribute("position");
        const pinch = r.k === "standing" ? 0.55 : 0.85;
        for (let v = 0; v < a.count; v++) {
          let px = a.getX(v), py = a.getY(v), pz = a.getZ(v);
          const kx = Math.sin(px * 3.1 + r.s + k) * 0.18 + Math.sin(pz * 2.3 + k * 1.7) * 0.14, ky = Math.sin(py * 2.7 + k) * 0.12;
          const waist = 1 - (1 - pinch) * Math.exp(-((py - 0.1) ** 2) * 6);
          px *= (1 + kx) * waist; pz *= (1 - kx * 0.6) * waist; py *= 1 + ky;
          // y in [-1, 1] mapped from the base (buried) to the top
          const yy = y0 + ((py + 1) / 2) * (top - y0);
          a.setXYZ(v, x + px * rr, yy, z + pz * rr * (r.k === "standing" ? 0.7 : 1));
        }
        for (let v = 0; v < a.count; v++) pos.push(a.getX(v), a.getY(v), a.getZ(v));
        const c = new THREE.Color(hex).multiplyScalar(0.9 + 0.2 * R());
        for (let v = 0; v < a.count; v++) { cols.push(c.r, c.g, c.b); grades.push(r.g === "A" ? 0 : r.g === "B" ? 1 : 2); }
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
    const plain = new Float32Array(cols), conf = new Float32Array(cols.length);
    for (let v = 0; v < grades.length; v++) { col.set(GREEN_CONF[grades[v]]); conf[3 * v] = col.r; conf[3 * v + 1] = col.g; conf[3 * v + 2] = col.b; }
    geo.setAttribute("color", new THREE.BufferAttribute(plain.slice(), 3));
    geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true }));
    m.raycast = () => {};
    m.userData = { plain, conf };
    rocks.add(m);
    rockMeshes.push(m);
  }
  group.add(rocks);

  const setView = (o) => {
    const before = { ...view };
    Object.assign(view, o);
    group.visible = view.on;
    if (before.conf !== view.conf) for (const m of rockMeshes) { m.geometry.attributes.color.array.set(view.conf ? m.userData.conf : m.userData.plain); m.geometry.attributes.color.needsUpdate = true; }
    if (before.assumed !== view.assumed || before.conf !== view.conf || before.season !== view.season) rebuildAll();
  };
  const setSeason = (s) => setView({ season: s });
  const tris = (g) => { let n = 0; if (g) g.traverse((o) => { if (o.isMesh) n += o.geometry.attributes.position.count / 3; }); return n; };
  const report = () => {
    let farTris = 0, farShown = 0, nearTris = 0, nearN = 0, nearTiles = 0;
    for (const T of tiles.values()) {
      const f = tris(T.far);
      farTris += f;
      if (T.far.visible) farShown += f;
      if (T.near) { nearTiles++; nearTris += tris(T.near); nearN += T.list.length; }
    }
    const byForm = {};
    for (let i = 0; i < N; i++) byForm[formOf(i)] = (byForm[formOf(i)] || 0) + 1;
    return { plants: N, by_form: byForm, tiles: tiles.size, rocks: meta.rocks.length, rock_triangles: rockMeshes.reduce((s, m) => s + m.geometry.attributes.position.count / 3, 0), far_triangles_all: farTris, far_triangles_shown: farShown, near_tiles: nearTiles, near_instances: nearN, near_triangles: nearTris, season: view.season };
  };
  return { group, update, setView, setSeason, report, view, P };
}
