// Round 20: what lay round the gardens. Classic script, loaded after ground3d.js and halls3d.js, before 3d.js; defines AROUND_COLOURS and buildAround.
// The ground past the inner domain (generated/ground_outer.json + .bin, scripts/ground_outer1860.py): a ring of 20 m cells about 2 km past the walls and a backdrop of 200 m cells
// out to the Western Hills, both triangulated here on the diagonal (i,j)-(i+1,j+1) and merged where a block of cells is flat within a tolerance (the plain is one plane).
// On it data/around_1860.json (scripts/surroundings1860.py): patches (fields, paddies, villages ...) and strips (roads, canals) draped on heightAt, lakes at their level,
// massing blocks for the neighbouring gardens, villages and camps, plain halls for the offices, and labels. Muted on purpose: context, not reconstruction.
// Every item belongs to a feature (an OW id) with a grade: conf=1 tints it A/B/C as the halls are tinted; assumed=0 hides the features marked assumed.
const AROUND_COLOURS = {
  plain: [170, 164, 124], paddyGround: [150, 162, 108], fieldGround: [162, 160, 112], relief: [104, 116, 80], reliefHigh: [126, 128, 112], bed: [96, 104, 92], bank: [162, 156, 118],
  backLow: [168, 162, 126], backHill: [112, 122, 92], backHigh: [138, 140, 136],
  confGround: { 0: [205, 200, 182], 1: [217, 164, 65], 2: [205, 200, 182], 3: [205, 200, 182], 4: [205, 200, 182], 5: [205, 200, 182] },
  water: 0x6f9fb0, bank_edge: [92, 86, 66],
  patch: {
    paddy: { spring: [150, 172, 150], summer: [128, 154, 92], autumn: [190, 168, 96], winter: [150, 136, 104] },
    field: { spring: [164, 170, 110], summer: [146, 160, 86], autumn: [190, 168, 104], winter: [160, 146, 112] },
    orchard: { spring: [128, 150, 96], summer: [92, 124, 70], autumn: [140, 130, 72], winter: [134, 122, 100] },
    village: [178, 166, 138], town: [172, 160, 134], camp: [176, 168, 146], garden: [128, 146, 100], office: [184, 176, 158], temple: [180, 170, 148], tomb: [150, 150, 118], other: [170, 160, 130],
  },
  road: [196, 182, 148], canal: [111, 159, 176], river: [111, 159, 176],
  block: { village: [176, 164, 146], camp: [168, 160, 146], garden: [190, 180, 160], temple: [184, 150, 128], office: [182, 168, 150], wall: [170, 160, 146], stone: [196, 192, 180], tomb: [150, 140, 112], other: [176, 166, 150] },
  roof: [104, 106, 108], hallBody: [146, 92, 78], hallPlatform: [186, 180, 166],
  conf: { A: [47, 143, 78], B: [217, 164, 65], C: [196, 81, 58] },
};

function buildAround({ meta, buf, data, inner, datum }) {
  const toLinear = (v) => { const f = v / 255; return f <= 0.04045 ? f / 12.92 : ((f + 0.055) / 1.055) ** 2.4; };
  const lin = (rgb) => rgb.map(toLinear);
  const group = new THREE.Group(); // the ground: ring, backdrop, lakes, the far skirt
  const items = new THREE.Group(); // what data/around_1860.json draws
  const R = meta.ring, B = meta.back, [dx0, dz0, dx1, dz1] = meta.domain;
  const rh = new Int16Array(buf, R.off_h, R.nx * R.nz), rc = new Uint8Array(buf, R.off_c, R.nx * R.nz), bh = new Int16Array(buf, B.off_h, B.nx * B.nz);
  const ringH = new Float32Array(rh.length), backH = new Float32Array(bh.length);
  for (let i = 0; i < rh.length; i++) ringH[i] = rh[i] / 100;
  for (let i = 0; i < bh.length; i++) backH[i] = bh[i] / 10;

  // The mesh's own surface on a lattice: the triangle (0,0),(1,0),(1,1) when a >= b, else (0,0),(1,1),(0,1).
  const triAt = (H, G, x, z) => {
    const u = (x - G.x0) / G.step, v = (z - G.z0) / G.step;
    const i = Math.max(0, Math.min(Math.floor(u), G.nx - 2)), j = Math.max(0, Math.min(Math.floor(v), G.nz - 2)), a = u - i, b = v - j;
    const h00 = H[j * G.nx + i], h10 = H[j * G.nx + i + 1], h01 = H[(j + 1) * G.nx + i], h11 = H[(j + 1) * G.nx + i + 1];
    return a >= b ? h00 + a * (h10 - h00) + b * (h11 - h10) : h00 + b * (h01 - h00) + a * (h11 - h01);
  };
  const inDomain = (x, z) => x >= dx0 && x <= dx1 && z >= dz0 && z <= dz1;
  const inRing = (x, z) => x >= R.x0 && x <= R.x1 && z >= R.z0 && z <= R.z1;
  // The ground under a point: the inner ground inside its domain (water: its level), the ring, the backdrop.
  const heightAt = (x, z) => {
    if (inDomain(x, z)) {
      const g = inner.groundAt(x, z);
      return g !== null ? g : inner.waterLevelAt(x, z) ?? inner.plainAt(x, z);
    }
    return inRing(x, z) ? triAt(ringH, R, x, z) : triAt(backH, B, x, z);
  };

  // A lattice meshed by a quadtree: a block of cells becomes one leaf when every vertex in it lies within tol of its two triangles, all share one colour key and none of its cells is in the hole.
  // Watertight: a leaf whose edges carry finer vertices (a smaller neighbour's corners, the lattice's own outer edge, the hole's edge points `holePts` from the mesh beside it) is drawn as a fan from its centre through all of them.
  function latticeMesh(H, G, hole, tol, colourOf, confOf, colourKey, holePts, keepEdge) {
    const pos = [], col = [], cf = [], idx = [], vmap = new Map(), xmap = new Map();
    const cellIn = (i, j) => { const x = G.x0 + (i + 0.5) * G.step, z = G.z0 + (j + 0.5) * G.step; return x > hole[0] && x < hole[2] && z > hole[1] && z < hole[3]; };
    const interp = (i0, j0, i1, j1, i, j) => {
      const h00 = H[j0 * G.nx + i0], h10 = H[j0 * G.nx + i1], h01 = H[j1 * G.nx + i0], h11 = H[j1 * G.nx + i1], a = (i - i0) / (i1 - i0), b = (j - j0) / (j1 - j0);
      return a >= b ? h00 + a * (h10 - h00) + b * (h11 - h10) : h00 + b * (h01 - h00) + a * (h11 - h01);
    };
    const vert = (i, j) => {
      const k = j * G.nx + i;
      let v = vmap.get(k);
      if (v === undefined) { v = pos.length / 3; vmap.set(k, v); pos.push(G.x0 + i * G.step, H[k], G.z0 + j * G.step); col.push(...colourOf(k, H[k])); cf.push(...confOf(k)); }
      return v;
    };
    const vertXYZ = (x, y, z, k) => {
      const key = `${Math.round(x * 100)},${Math.round(z * 100)}`;
      let v = xmap.get(key);
      if (v === undefined) { v = pos.length / 3; xmap.set(key, v); pos.push(x, y, z); col.push(...colourOf(k, y)); cf.push(...confOf(k)); }
      return v;
    };
    const flat = (i0, j0, i1, j1) => {
      const c0 = colourKey(j0 * G.nx + i0), tolAt = typeof tol === "function" ? tol(G.x0 + ((i0 + i1) / 2) * G.step, G.z0 + ((j0 + j1) / 2) * G.step) : tol;
      for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
        const k = j * G.nx + i;
        if (Math.abs(H[k] - interp(i0, j0, i1, j1, i, j)) > tolAt || colourKey(k) !== c0) return false;
        if (i < i1 && j < j1 && cellIn(i, j)) return false;
      }
      return true;
    };
    const anyOut = (i0, j0, i1, j1) => { for (let j = j0; j < j1; j++) for (let i = i0; i < i1; i++) if (!cellIn(i, j)) return true; return false; };
    const leaves = [];
    const walk = (i0, j0, i1, j1) => {
      if (i1 - i0 === 1 && j1 - j0 === 1) { if (!cellIn(i0, j0)) leaves.push([i0, j0, i1, j1]); return; }
      if (!anyOut(i0, j0, i1, j1)) return;
      if (i1 - i0 === j1 - j0 && flat(i0, j0, i1, j1)) { leaves.push([i0, j0, i1, j1]); return; }
      const im = i1 - i0 > 1 ? (i0 + i1) >> 1 : i1, jm = j1 - j0 > 1 ? (j0 + j1) >> 1 : j1;
      for (const [a, b, c, d] of [[i0, j0, im, jm], [im, j0, i1, jm], [i0, jm, im, j1], [im, jm, i1, j1]]) if (c > a && d > b) walk(a, b, c, d);
    };
    const S = 32;
    for (let j = 0; j < G.nz - 1; j += S) for (let i = 0; i < G.nx - 1; i += S) walk(i, j, Math.min(i + S, G.nx - 1), Math.min(j + S, G.nz - 1));
    const used = new Uint8Array(G.nx * G.nz);
    for (const [i0, j0, i1, j1] of leaves) for (const [i, j] of [[i0, j0], [i1, j0], [i0, j1], [i1, j1]]) used[j * G.nx + i] = 1;
    if (keepEdge) { for (let i = 0; i < G.nx; i++) used[i] = used[(G.nz - 1) * G.nx + i] = 1; for (let j = 0; j < G.nz; j++) used[j * G.nx] = used[j * G.nx + G.nx - 1] = 1; }
    const [hx0, hz0, hx1, hz1] = hole, E = 1e-3;
    let fans = 0;
    for (const [i0, j0, i1, j1] of leaves) {
      const ring = []; // [v, angle]
      const X0 = G.x0 + i0 * G.step, X1 = G.x0 + i1 * G.step, Z0 = G.z0 + j0 * G.step, Z1 = G.z0 + j1 * G.step, cx = (X0 + X1) / 2, cz = (Z0 + Z1) / 2;
      const add = (v) => ring.push([v, Math.atan2(pos[3 * v + 2] - cz, pos[3 * v] - cx)]);
      for (let i = i0; i <= i1; i++) { if (i === i0 || i === i1 || used[j0 * G.nx + i]) add(vert(i, j0)); if (used[j1 * G.nx + i] && i !== i0 && i !== i1) add(vert(i, j1)); }
      add(vert(i0, j1)); add(vert(i1, j1));
      for (let j = j0 + 1; j < j1; j++) { if (used[j * G.nx + i0]) add(vert(i0, j)); if (used[j * G.nx + i1]) add(vert(i1, j)); }
      // points of the mesh beside the hole that fall inside this leaf's edges
      const onHole = (Math.abs(X0 - hx1) < E || Math.abs(X1 - hx0) < E || Math.abs(Z0 - hz1) < E || Math.abs(Z1 - hz0) < E);
      if (onHole && holePts) for (const [x, y, z] of holePts) {
        const onV = (Math.abs(x - X0) < E || Math.abs(x - X1) < E) && z > Z0 + E && z < Z1 - E, onH = (Math.abs(z - Z0) < E || Math.abs(z - Z1) < E) && x > X0 + E && x < X1 - E;
        if (onV || onH) add(vertXYZ(x, y, z, j0 * G.nx + i0));
      }
      if (ring.length === 4) {
        const a = vert(i0, j0), b = vert(i1, j0), c = vert(i1, j1), d = vert(i0, j1);
        idx.push(a, c, b, a, d, c); // the diagonal (i,j)-(i+1,j+1); counter-clockwise seen from above (y up, z south)
        continue;
      }
      fans++;
      ring.sort((p, q) => p[1] - q[1]);
      const kc = j0 * G.nx + i0, yc = interp(i0, j0, i1, j1, (i0 + i1) / 2, (j0 + j1) / 2);
      const c = pos.length / 3;
      pos.push(cx, yc, cz); col.push(...colourOf(kc, yc)); cf.push(...confOf(kc));
      for (let t = 0; t < ring.length; t++) idx.push(c, ring[(t + 1) % ring.length][0], ring[t][0]);
    }
    return { pos, col, cf, idx, leaves: leaves.length, fans };
  }
  const meshOf = ({ pos, col, cf, idx }) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
    const plain = new Float32Array(col), conf = new Float32Array(cf);
    g.setAttribute("color", new THREE.BufferAttribute(plain.slice(), 3));
    g.setIndex(pos.length / 3 > 65535 ? new THREE.BufferAttribute(new Uint32Array(idx), 1) : new THREE.BufferAttribute(new Uint16Array(idx), 1));
    g.computeVertexNormals();
    return { g, plain, conf };
  };
  const lands = [];

  // Ring.
  const C = Object.fromEntries(Object.entries(AROUND_COLOURS).filter(([, v]) => Array.isArray(v)).map(([k, v]) => [k, lin(v)]));
  const confG = Object.fromEntries(Object.entries(AROUND_COLOURS.confGround).map(([k, v]) => [k, lin(v)]));
  const plainAt = inner.plainAt;
  const ringColour = (k, h) => {
    const c = rc[k];
    if (c === 2) return C.bed;
    if (c === 1) {
      const x = R.x0 + (k % R.nx) * R.step, z = R.z0 + Math.floor(k / R.nx) * R.step, t = Math.min(Math.max((h - plainAt(x, z)) / 12, 0), 1), t2 = Math.min(Math.max((h - plainAt(x, z) - 60) / 120, 0), 1);
      return [0, 1, 2].map((q) => (C.plain[q] * (1 - t) + C.relief[q] * t) * (1 - t2) + C.reliefHigh[q] * t2);
    }
    return c === 3 ? C.bank : c === 4 ? C.paddyGround : c === 5 ? C.fieldGround : C.plain;
  };
  const ringMesh = meshOf(latticeMesh(ringH, R, meta.domain, 0.05, ringColour, (k) => confG[rc[k]] || confG[0], (k) => rc[k], inner.edgeVerts || [], true));
  const landMat = new THREE.MeshLambertMaterial({ vertexColors: true });
  group.add(new THREE.Mesh(ringMesh.g, landMat));
  lands.push(ringMesh);

  // Backdrop, by height above the plain.
  const backColour = (k, h) => {
    const x = B.x0 + (k % B.nx) * B.step, z = B.z0 + Math.floor(k / B.nx) * B.step, r = h - plainAt(x, z);
    const t = Math.min(Math.max(r / 60, 0), 1), t2 = Math.min(Math.max((r - 300) / 600, 0), 1);
    return [0, 1, 2].map((q) => (C.backLow[q] * (1 - t) + C.backHill[q] * t) * (1 - t2) + C.backHigh[q] * t2);
  };
  const ringEdge = [];
  for (let i = 0; i < R.nx; i++) for (const j of [0, R.nz - 1]) ringEdge.push([R.x0 + i * R.step, ringH[j * R.nx + i], R.z0 + j * R.step]);
  for (let j = 1; j < R.nz - 1; j++) for (const i of [0, R.nx - 1]) ringEdge.push([R.x0 + i * R.step, ringH[j * R.nx + i], R.z0 + j * R.step]);
  const backMesh = meshOf(latticeMesh(backH, B, [R.x0, R.z0, R.x1, R.z1], (x, z) => 2 + Math.hypot(x, z) / 700 /* far and fogged: 16 m at 10 km */, backColour, () => confG[0], () => 0, ringEdge, false));
  group.add(new THREE.Mesh(backMesh.g, landMat));
  lands.push(backMesh);
  // Past the backdrop: the plain's colour to the horizon, under the fog, just below the backdrop's lowest edge.
  let edgeMin = Infinity;
  for (let i = 0; i < B.nx; i++) edgeMin = Math.min(edgeMin, backH[i], backH[(B.nz - 1) * B.nx + i]);
  for (let j = 0; j < B.nz; j++) edgeMin = Math.min(edgeMin, backH[j * B.nx], backH[j * B.nx + B.nx - 1]);
  const FAR = 120000, fy = edgeMin - 2, farMat = new THREE.MeshLambertMaterial({ color: new THREE.Color().setRGB(...C.backLow) });
  for (const [ax, az, bx, bz] of [[-FAR, -FAR, FAR, B.z0], [-FAR, B.z1, FAR, FAR], [-FAR, B.z0, B.x0, B.z1], [B.x1, B.z0, FAR, B.z1]]) {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array([ax, fy, az, bx, fy, az, bx, fy, bz, ax, fy, bz]), 3));
    g.setIndex([0, 2, 1, 0, 3, 2]);
    g.computeVertexNormals();
    group.add(new THREE.Mesh(g, farMat));
  }

  // Lakes past the domain, flat at their level.
  const waterMat = new THREE.MeshLambertMaterial({ color: AROUND_COLOURS.water, transparent: true, opacity: 0.84, polygonOffset: true, polygonOffsetFactor: -0.5, polygonOffsetUnits: -1 });
  const flatPoly = (outer, holes, y) => {
    const v2 = (p) => new THREE.Vector2(p[0], p[1]);
    const contour = outer.map(v2), hs = (holes || []).map((h) => h.map(v2));
    const tris = THREE.ShapeUtils.triangulateShape(contour, hs), all = contour.concat(...hs);
    const pos = new Float32Array(all.length * 3);
    all.forEach((p, i) => { pos[3 * i] = p.x; pos[3 * i + 1] = typeof y === "function" ? y(p.x, p.y) : y; pos[3 * i + 2] = p.y; });
    const idx = [];
    for (const [a, b, c] of tris) {
      // face up
      const cr = (all[b].x - all[a].x) * (all[c].y - all[a].y) - (all[b].y - all[a].y) * (all[c].x - all[a].x);
      if (cr > 0) idx.push(a, c, b); else idx.push(a, b, c);
    }
    return { pos, idx, all };
  };
  for (const L of meta.lakes || []) for (const p of L.polys) {
    const { pos, idx } = flatPoly(p.outer, p.holes, L.level);
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, waterMat);
    m.renderOrder = 2;
    group.add(m);
  }

  // ---- the items of data/around_1860.json ----
  const feats = new Map(((data && data.features) || []).map((f) => [f.id, f]));
  const confLin = Object.fromEntries(Object.entries(AROUND_COLOURS.conf).map(([k, v]) => [k, lin(v)]));
  const ids = []; // item index -> feature id
  const idIndex = (id) => { let k = ids.indexOf(id); if (k < 0) { k = ids.length; ids.push(id); } return k; };
  // Buckets: one merged mesh per layer and assumed flag, two colour sets (season-dependent ones are filled by recolour), a feature index per triangle for picking.
  const buckets = new Map();
  const bucket = (layer, assumed) => {
    const key = `${layer}|${assumed ? 1 : 0}`;
    if (!buckets.has(key)) buckets.set(key, { layer, assumed, pos: [], kind: [], fid: [], tri: [], shadeK: [] });
    return buckets.get(key);
  };
  const addTri = (bk, pts, kind, fid, shade = 1) => { for (const p of pts) { bk.pos.push(p[0], p[1], p[2]); bk.kind.push(kind); bk.fid.push(fid); bk.shadeK.push(shade); } bk.tri.push(fid); };
  const featOf = (id) => feats.get(id) || { id, conf: "C", assumed: true };

  // Draped triangles: split until no edge is longer than MAXE, every vertex on heightAt plus a lift.
  const MAXE = 30; // the ring is a 20 m lattice and mostly one plane: a draped vertex every 30 m or less
  const drape = (bk, a, b, c, lift, kind, fid, depth = 0) => {
    const d = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1]);
    const lab = d(a, b), lbc = d(b, c), lca = d(c, a), m = Math.max(lab, lbc, lca);
    // On a plane (most of the ring) a large triangle lies on the ground already: split only where the ground departs from it (15 points tested), and on bent ground (over 0.1 m) down to 18 m.
    let bend = 0;
    if (m > 18) {
      const ya = heightAt(a[0], a[1]), yb = heightAt(b[0], b[1]), yc = heightAt(c[0], c[1]);
      for (let p = 0; p <= 4 && bend <= 0.1; p++) for (let q = 0; q <= 4 - p; q++) {
        const u = p / 4, v = q / 4, w = 1 - u - v;
        bend = Math.max(bend, Math.abs(heightAt(a[0] * u + b[0] * v + c[0] * w, a[1] * u + b[1] * v + c[1] * w) - (ya * u + yb * v + yc * w)));
      }
    }
    if ((m > 400 || (bend > 0.1 && m > 18)) && depth < 14) { // the lift is 0.2 m, with a polygon offset
      if (m === lab) { const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]; drape(bk, a, mid, c, lift, kind, fid, depth + 1); drape(bk, mid, b, c, lift, kind, fid, depth + 1); }
      else if (m === lbc) { const mid = [(b[0] + c[0]) / 2, (b[1] + c[1]) / 2]; drape(bk, a, b, mid, lift, kind, fid, depth + 1); drape(bk, a, mid, c, lift, kind, fid, depth + 1); }
      else { const mid = [(c[0] + a[0]) / 2, (c[1] + a[1]) / 2]; drape(bk, a, b, mid, lift, kind, fid, depth + 1); drape(bk, mid, b, c, lift, kind, fid, depth + 1); }
      return;
    }
    addTri(bk, [a, b, c].map((p) => [p[0], heightAt(p[0], p[1]) + lift, p[1]]), kind, fid);
  };
  const densify = (ring, step) => {
    const out = [];
    for (let i = 0; i < ring.length; i++) {
      const p = ring[i], q = ring[(i + 1) % ring.length], n = Math.max(1, Math.ceil(Math.hypot(q[0] - p[0], q[1] - p[1]) / step));
      for (let k = 0; k < n; k++) out.push([p[0] + ((q[0] - p[0]) * k) / n, p[1] + ((q[1] - p[1]) * k) / n]);
    }
    return out;
  };
  // Patches.
  for (const P of (data && data.patches) || []) {
    const f = featOf(P.id), fid = idIndex(P.id), bk = bucket("patch", f.assumed || P.assumed);
    const outer = densify(P.ring, 60), holes = (P.holes || []).map((h) => densify(h, 60));
    const v2 = (p) => new THREE.Vector2(p[0], p[1]);
    const all = outer.concat(...holes);
    const tris = THREE.ShapeUtils.triangulateShape(outer.map(v2), holes.map((h) => h.map(v2)));
    for (const [a, b, c] of tris) {
      const A = all[a], Bp = all[b], Cp = all[c], cr = (Bp[0] - A[0]) * (Cp[1] - A[1]) - (Bp[1] - A[1]) * (Cp[0] - A[0]);
      if (cr > 0) drape(bk, A, Cp, Bp, 0.2, P.kind, fid); else drape(bk, A, Bp, Cp, 0.2, P.kind, fid);
    }
  }
  // Strips: a ribbon of width w, its vertices every 10 m or less; a canal or river gets a darker bank ribbon under it.
  const ribbon = (bk, pts, w, lift, kind, fid) => {
    const P = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const p = pts[i], q = pts[i + 1], n = Math.max(1, Math.ceil(Math.hypot(q[0] - p[0], q[1] - p[1]) / 10));
      for (let k = 0; k < n; k++) P.push([p[0] + ((q[0] - p[0]) * k) / n, p[1] + ((q[1] - p[1]) * k) / n]);
    }
    P.push(pts[pts.length - 1]);
    if (P.length < 2) return;
    const L = [], Rr = [];
    for (let i = 0; i < P.length; i++) {
      const a = P[Math.max(i - 1, 0)], b = P[Math.min(i + 1, P.length - 1)];
      let tx = b[0] - a[0], tz = b[1] - a[1];
      const l = Math.hypot(tx, tz) || 1;
      tx /= l; tz /= l;
      const nx = -tz * (w / 2), nz = tx * (w / 2);
      L.push([P[i][0] + nx, P[i][1] + nz]); Rr.push([P[i][0] - nx, P[i][1] - nz]);
    }
    const y = (p) => [p[0], heightAt(p[0], p[1]) + lift, p[1]];
    for (let i = 0; i < P.length - 1; i++) {
      const a = y(L[i]), b = y(Rr[i]), c = y(Rr[i + 1]), d = y(L[i + 1]);
      // face up (y): order by the cross product of the plan
      const up = (u, v, s) => (v[0] - u[0]) * (s[2] - u[2]) - (v[2] - u[2]) * (s[0] - u[0]) < 0;
      addTri(bk, up(a, b, c) ? [a, b, c] : [a, c, b], kind, fid);
      addTri(bk, up(a, c, d) ? [a, c, d] : [a, d, c], kind, fid);
    }
  };
  for (const S of (data && data.strips) || []) {
    const f = featOf(S.id), fid = idIndex(S.id), bk = bucket("strip", f.assumed || S.assumed);
    if (S.kind === "canal" || S.kind === "river") ribbon(bk, S.pts, S.w + 2.4, 0.1, "bank_edge", fid);
    ribbon(bk, S.pts, S.w, S.kind === "road" ? 0.16 : 0.2, S.kind, fid);
  }
  // Waters given in the data, flat.
  for (const Wt of (data && data.waters) || []) {
    const f = featOf(Wt.id), fid = idIndex(Wt.id), bk = bucket("water", f.assumed || Wt.assumed);
    const { pos, idx } = flatPoly(Wt.ring, Wt.holes, Wt.level);
    for (let t = 0; t < idx.length; t += 3) addTri(bk, [idx[t], idx[t + 1], idx[t + 2]].map((v) => [pos[3 * v], pos[3 * v + 1], pos[3 * v + 2]]), "water", fid);
  }
  // Blocks and halls: boxes in a local frame (w along the angle rot, degrees clockwise from east seen from above, i.e. from +x towards +z), sunk to the lowest ground under them.
  const SINK = 0.3;
  const boxTris = (bk, x, z, w, d, rot, y0, y1, kind, fid, shade = 1, topFace = true) => {
    const c = Math.cos((rot * Math.PI) / 180), s = Math.sin((rot * Math.PI) / 180);
    const P = (u, v, y) => [x + u * c - v * s, y, z + u * s + v * c];
    const hw = w / 2, hd = d / 2;
    const q = [[-hw, -hd], [hw, -hd], [hw, hd], [-hw, hd]];
    const top = q.map(([u, v]) => P(u, v, y1)), bot = q.map(([u, v]) => P(u, v, y0));
    const quad = (a, b, cc, dd, k = shade) => { addTri(bk, [a, b, cc], kind, fid, k); addTri(bk, [a, cc, dd], kind, fid, k); };
    if (topFace) quad(top[0], top[3], top[2], top[1], shade);
    for (let i = 0; i < 4; i++) { const j = (i + 1) % 4; quad(bot[i], bot[j], top[j], top[i], shade * (i % 2 ? 0.86 : 0.94)); }
    return P;
  };
  const baseOf = (x, z, w, d, rot) => {
    const c = Math.cos((rot * Math.PI) / 180), s = Math.sin((rot * Math.PI) / 180);
    let lo = Infinity, hi = -Infinity;
    for (const [u, v] of [[0, 0], [-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]]) { const h = heightAt(x + u * c - v * s, z + u * s + v * c); lo = Math.min(lo, h); hi = Math.max(hi, h); }
    return [lo, hi];
  };
  const roofTris = (bk, x, z, w, d, rot, y0, rise, type, kind, fid) => {
    const c = Math.cos((rot * Math.PI) / 180), s = Math.sin((rot * Math.PI) / 180), ov = 0.6;
    const P = (u, v, y) => [x + u * c - v * s, y, z + u * s + v * c];
    const hw = w / 2 + ov, hd = d / 2 + ov, y1 = y0 + rise;
    const e = [P(-hw, -hd, y0), P(hw, -hd, y0), P(hw, hd, y0), P(-hw, hd, y0)];
    if (type === "flat") { addTri(bk, [e[0], e[2], e[1]], kind, fid); addTri(bk, [e[0], e[3], e[2]], kind, fid); return; }
    const r = type === "gable" ? hw : type === "mound" ? 0.05 : Math.max(hw - hd * 0.9, 0.2);
    const r0 = P(-r, 0, y1), r1 = P(r, 0, y1);
    addTri(bk, [e[0], r0, r1], kind, fid, 0.95); addTri(bk, [e[0], r1, e[1]], kind, fid, 0.95);
    addTri(bk, [e[2], r1, r0], kind, fid, 0.8); addTri(bk, [e[2], r0, e[3]], kind, fid, 0.8);
    if (type === "gable") { addTri(bk, [e[1], r1, e[2]], kind, fid, 0.7); addTri(bk, [e[3], r0, e[0]], kind, fid, 0.7); }
    else { addTri(bk, [e[1], r1, e[2]], kind, fid, 0.88); addTri(bk, [e[3], r0, e[0]], kind, fid, 0.88); }
  };
  for (const K of (data && data.blocks) || []) {
    const f = featOf(K.id), fid = idIndex(K.id), bk = bucket("block", f.assumed || K.assumed); // a feature marked assumed, or a block generated for it (`assumed` on the block)
    const [lo, hi] = baseOf(K.x, K.z, K.w, K.d, K.rot || 0), top = hi + K.h;
    boxTris(bk, K.x, K.z, K.w, K.d, K.rot || 0, lo - SINK, top, `block_${K.tint || "other"}`, fid, 1, !K.roof || K.roof === "none");
    if (K.roof === "mound") roofTris(bk, K.x, K.z, K.w - 1.2, K.d - 1.2, K.rot || 0, top, Math.min(K.w, K.d) * 0.4, "mound", "block_tomb", fid); // an earth mound: a low pyramid, inside the box's outline
    else if (K.roof && K.roof !== "none") roofTris(bk, K.x, K.z, K.w, K.d, K.rot || 0, top, K.roof === "flat" ? 0 : Math.min(K.d * 0.32, 4), K.roof, "roof", fid);
  }
  for (const Hl of (data && data.halls) || []) {
    const f = featOf(Hl.id), fid = idIndex(Hl.id), bk = bucket("block", f.assumed || Hl.assumed);
    const rot = Hl.rot || 0, [lo, hi] = baseOf(Hl.x, Hl.z, Hl.w + 1.6, Hl.d + 1.6, rot), plat = hi + 0.45, eave = plat + Math.max(3.2, Math.min(Hl.d * 0.55, 4.6));
    boxTris(bk, Hl.x, Hl.z, Hl.w + 1.6, Hl.d + 1.6, rot, lo - SINK, plat, "hallPlatform", fid);
    boxTris(bk, Hl.x, Hl.z, Hl.w, Hl.d, rot, plat, eave, "hallBody", fid, 1, false);
    roofTris(bk, Hl.x, Hl.z, Hl.w, Hl.d, rot, eave, Hl.d * 0.42, Hl.roof || "gable", "roof", fid);
  }

  // Colours of a bucket's vertices for the view (by kind, season) and by confidence.
  const meshes = [];
  for (const bk of buckets.values()) {
    const n = bk.pos.length / 3;
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(bk.pos), 3));
    g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    g.computeVertexNormals();
    const isWater = bk.layer === "water";
    const mat = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide, transparent: isWater, opacity: isWater ? 0.84 : 1, polygonOffset: bk.layer !== "block", polygonOffsetFactor: bk.layer === "strip" ? -2 : -1, polygonOffsetUnits: bk.layer === "strip" ? -4 : -2 });
    const m = new THREE.Mesh(g, mat);
    m.renderOrder = isWater ? 2 : 1;
    m.userData = { tri: bk.tri, assumed: bk.assumed };
    items.add(m);
    meshes.push({ m, bk, n });
  }
  const colourOfKind = (kind, season) => {
    const P = AROUND_COLOURS.patch[kind];
    if (P) return Array.isArray(P) ? P : P[season] || P.summer;
    if (kind.startsWith("block_")) return AROUND_COLOURS.block[kind.slice(6)] || AROUND_COLOURS.block.other;
    const v = AROUND_COLOURS[kind];
    return Array.isArray(v) ? v : kind === "water" ? AROUND_COLOURS.canal : AROUND_COLOURS.patch.other;
  };
  const recolour = (conf, season) => {
    for (const { m, bk, n } of meshes) {
      const a = m.geometry.attributes.color.array, cache = new Map();
      for (let i = 0; i < n; i++) {
        let rgb;
        if (conf) rgb = confLin[featOf(ids[bk.fid[i]]).conf] || confLin.C;
        else { const k = bk.kind[i]; if (!cache.has(k)) cache.set(k, lin(colourOfKind(k, season))); rgb = cache.get(k); }
        const s = conf ? 1 : bk.shadeK[i];
        a[3 * i] = rgb[0] * s; a[3 * i + 1] = rgb[1] * s; a[3 * i + 2] = rgb[2] * s;
      }
      m.geometry.attributes.color.needsUpdate = true;
    }
  };

  // Labels: specs for 3d.js's labelSprite, at a height over the ground.
  const labels = ((data && data.labels) || []).map((l) => ({ ...l, y: heightAt(l.x, l.z) + (l.rank === 1 ? 40 : 18), assumed: featOf(l.id).assumed }));

  let view = { on: true, conf: false, assumed: true, season: "summer" };
  const setView = (v) => {
    const prev = view;
    view = { ...view, ...v };
    group.visible = items.visible = view.on;
    for (const { m } of meshes) m.visible = !(m.userData.assumed && !view.assumed);
    for (const L of lands) { L.g.attributes.color.array.set(view.conf ? L.conf : L.plain); L.g.attributes.color.needsUpdate = true; }
    if (prev.conf !== view.conf || prev.season !== view.season || !recolour.done) { recolour(view.conf, view.season); recolour.done = true; }
  };
  // Picking: the nearest item hit by a ray (in world units of the scaled world: the caller passes the unscaled ray, as for the halls).
  const raycaster = new THREE.Raycaster();
  const pick = (ray) => {
    if (!view.on) return null;
    raycaster.ray.copy(ray);
    const hits = raycaster.intersectObjects(meshes.map((x) => x.m).filter((m) => m.visible), false);
    if (!hits.length) return null;
    const h = hits[0], id = ids[h.object.userData.tri[h.faceIndex]];
    return { id, feature: featOf(id), point: h.point, distance: h.distance };
  };
  const triangles = () => {
    let t = 0;
    for (const L of lands) t += L.g.index.count / 3;
    for (const { n } of meshes) t += n / 3;
    return t;
  };
  return { group, items, heightAt, setView, pick, labels, features: feats, triangles };
}
