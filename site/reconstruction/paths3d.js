// Round 9: the ways of 1860 in the 3D view. data/paths_1860.geojson, landings_1860.geojson (scripts/paths1860.py). Classic script, loaded before 3d.js; defines the global buildPaths.
// Ways are flat strips a hand above the ground, coloured by kind; galleries not already standing as a box get a low roof on posts; landings are small platforms into the water; boat routes are dashed lines on the water.
// Assumed (C) ways sit in their own meshes, in a paler, warmer tint, so they can be switched off. Colours are chosen for the view, not read from a source.
const PATH_COLOURS = {
  imperial_road: 0xb8ab90, paved_way: 0xd8ccb0, courtyard_path: 0xcbbd9c, service_path: 0xae9e7c, gallery: 0xb3a68d, mountain_gallery: 0xb3a68d,
  causeway: 0xa79b78, dike: 0xa79b78, bridge_approach: 0xd2c7ad, steps: 0xe6dcc6,
  assumed: 0xd8bfae, post: 0x8a3b2a, roof: 0x5f6469, landing: 0xd3cab6, boat: 0x24566e,
  conf: { A: 0x2f8f4e, B: 0xd9a441, C: 0xc4513a },
};

function buildPaths({ paths, landings, toXZ, groundAt, waterLevelAt, base }) {
  const LIFT = 0.07, STEP_M = 4;
  const groups = { sure: new THREE.Group(), assumed: new THREE.Group(), boat: new THREE.Group() };
  const yAt = (x, z) => { const g = groundAt(x, z); return (g === null ? base : g) + LIFT; };
  const c = new THREE.Color();
  // One geometry per group, two colour sets: by kind and by confidence.
  const buf = { sure: { pos: [], kind: [], conf: [] }, assumed: { pos: [], kind: [], conf: [] } };
  const push = (b, pts, kindHex, confHex) => {
    for (const p of pts) b.pos.push(...p);
    c.setHex(kindHex); const k = [c.r, c.g, c.b];
    c.setHex(confHex); const q = [c.r, c.g, c.b];
    for (let i = 0; i < pts.length; i++) { b.kind.push(...k); b.conf.push(...q); }
  };
  const quad = (b, a1, a2, b2, b1, kh, ch) => push(b, [a1, a2, b2, a1, b2, b1], kh, ch);
  const posts = [], roofs = [];
  const box = (out, cx, cy, cz, sx, sy, sz, ux, uz) => {
    // an oriented box: u along (ux, uz), v across, y up
    const vx = -uz, vz = ux, hx = sx / 2, hy = sy / 2, hz = sz / 2;
    const P = (a, bb, d) => [cx + ux * a * hx + vx * d * hz, cy + bb * hy, cz + uz * a * hx + vz * d * hz];
    const f = [[P(-1, 1, -1), P(1, 1, -1), P(1, 1, 1), P(-1, 1, 1)], [P(-1, -1, -1), P(-1, -1, 1), P(1, -1, 1), P(1, -1, -1)],
      [P(-1, -1, -1), P(1, -1, -1), P(1, 1, -1), P(-1, 1, -1)], [P(-1, -1, 1), P(-1, 1, 1), P(1, 1, 1), P(1, -1, 1)],
      [P(-1, -1, -1), P(-1, 1, -1), P(-1, 1, 1), P(-1, -1, 1)], [P(1, -1, -1), P(1, -1, 1), P(1, 1, 1), P(1, 1, -1)]];
    for (const [a, bb, d, e] of f) out.push(...a, ...bb, ...d, ...a, ...d, ...e);
  };
  const boatPts = [];
  for (const f of paths.features) {
    const p = f.properties;
    const xz = f.geometry.coordinates.map(toXZ);
    if (p.kind === "boat_route") {
      for (let i = 0; i < xz.length - 1; i++) {
        // Round 10: 0.5 m above the level of the water under each end, drawn after the water
        const ya = (waterLevelAt(xz[i][0], xz[i][1]) ?? 0) + 0.5, yb = (waterLevelAt(xz[i + 1][0], xz[i + 1][1]) ?? 0) + 0.5;
        boatPts.push(new THREE.Vector3(xz[i][0], ya, xz[i][1]), new THREE.Vector3(xz[i + 1][0], yb, xz[i + 1][1]));
      }
      continue;
    }
    const b = p.assumed ? buf.assumed : buf.sure;
    const kh = p.assumed ? PATH_COLOURS.assumed : PATH_COLOURS[p.kind] ?? PATH_COLOURS.courtyard_path, ch = PATH_COLOURS.conf[p.confidence];
    const half = Math.max(p.width_m, 0.8) / 2;
    // resample so the strip follows the ground
    const pts = [];
    for (let i = 0; i < xz.length - 1; i++) {
      const [ax, az] = xz[i], [bx, bz] = xz[i + 1], L = Math.hypot(bx - ax, bz - az), n = Math.max(1, Math.ceil(L / STEP_M));
      for (let k = 0; k < n; k++) pts.push([ax + ((bx - ax) * k) / n, az + ((bz - az) * k) / n]);
    }
    pts.push(xz[xz.length - 1]);
    for (let i = 0; i < pts.length - 1; i++) {
      const [ax, az] = pts[i], [bx, bz] = pts[i + 1], L = Math.hypot(bx - ax, bz - az) || 1, nx = (-(bz - az) / L) * half, nz = ((bx - ax) / L) * half;
      const ya = yAt(ax, az), yb = yAt(bx, bz);
      quad(b, [ax + nx, ya, az + nz], [ax - nx, ya, az - nz], [bx - nx, yb, bz - nz], [bx + nx, yb, bz + nz], kh, ch);
    }
    if ((p.kind === "gallery" || p.kind === "mountain_gallery") && !p.in_box) {
      // a low roof on posts: posts every bay (2.88 m, params.json classes.gallery), eave 2.7 m, a slab of a roof. Simple, on purpose.
      for (let i = 0; i < xz.length - 1; i++) {
        const [ax, az] = xz[i], [bx, bz] = xz[i + 1], L = Math.hypot(bx - ax, bz - az);
        if (L < 0.5) continue;
        const ux = (bx - ax) / L, uz = (bz - az) / L, vx = -uz, vz = ux, n = Math.max(1, Math.round(L / 2.88));
        for (let k = 0; k <= n; k++) {
          const t = k / n, x = ax + (bx - ax) * t, z = az + (bz - az) * t, y = yAt(x, z);
          for (const s of [-1, 1]) box(posts, x + vx * s * (half - 0.15), y + 1.3, z + vz * s * (half - 0.15), 0.22, 2.6, 0.22, ux, uz);
        }
        const mx = (ax + bx) / 2, mz = (az + bz) / 2, y = Math.max(yAt(ax, az), yAt(bx, bz));
        box(roofs, mx, y + 2.75, mz, L + 0.3, 0.3, half * 2 + 0.9, ux, uz);
        box(roofs, mx, y + 3.15, mz, L + 0.3, 0.5, half * 1.1, ux, uz);
      }
    }
  }
  const meshes = {};
  for (const key of ["sure", "assumed"]) {
    const g = new THREE.BufferGeometry(), B = buf[key];
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(B.pos), 3));
    g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(B.kind), 3));
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
    m.userData = { kind: new Float32Array(B.kind), conf: new Float32Array(B.conf) };
    meshes[key] = m;
    groups[key].add(m);
  }
  const solid = (arr, hex) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(arr), 3));
    g.computeVertexNormals();
    return new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: hex }));
  };
  groups.sure.add(solid(posts, PATH_COLOURS.post), solid(roofs, PATH_COLOURS.roof));
  // landings: a platform 3 m along the shore and 2.5 m out over the water, top at the bank (a dock: 4 x 6 m)
  const plat = [];
  for (const f of landings.features) {
    const p = f.properties, [x, z] = toXZ(f.geometry.coordinates);
    if (p.facing_deg === null || p.facing_deg === undefined) continue;
    const r = (p.facing_deg * Math.PI) / 180, ux = Math.sin(r), uz = -Math.cos(r);
    const [w, d] = p.kind === "dock" ? [4, 6] : [3, 2.5];
    // Round 10: on the bank at its point, and at least 0.4 m above the water it serves
    const lev = waterLevelAt(x, z), top = Math.max(yAt(x, z) - LIFT + 0.05, lev === null ? -Infinity : lev + 0.4);
    box(plat, x + ux * d / 2, top - 0.6, z + uz * d / 2, d, 1.3, w, ux, uz);
  }
  groups.sure.add(solid(plat, PATH_COLOURS.landing));
  const bg = new THREE.BufferGeometry().setFromPoints(boatPts);
  const boat = new THREE.LineSegments(bg, new THREE.LineDashedMaterial({ color: PATH_COLOURS.boat, dashSize: 6, gapSize: 4 }));
  boat.computeLineDistances();
  boat.renderOrder = 3;
  groups.boat.add(boat);
  const setConfMode = (on) => {
    for (const m of [meshes.sure, meshes.assumed]) {
      m.geometry.attributes.color.array.set(on ? m.userData.conf : m.userData.kind);
      m.geometry.attributes.color.needsUpdate = true;
    }
  };
  return { groups, setConfMode };
}
