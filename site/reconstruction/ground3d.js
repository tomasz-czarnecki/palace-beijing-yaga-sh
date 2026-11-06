// Round 10: the ground of the 3D view, from generated/ground.json, ground.bin, ground_grid.i16 and ground_level.u8 (scripts/ground1860.py). Classic script, loaded before 3d.js; defines the global buildGround.
// Parts come in chunks of at most 65535 vertices: positions int16 (x and z in decimetres from the domain's corner, y in centimetres), indices uint16.
// Land: the plain, hills, banks and pads, coloured here from two bytes per vertex (what shaped it, and how much hill). Water: one level per body, a little see-through over its bed.
// Options: setConf (tint by what the ground rests on), setAssumed (false: the generated hills, assumed, flattened), setContours (a line every metre, every 5 m darker).
const GROUND_COLOURS = {
  outside: [170, 164, 124], inside: [137, 152, 98], hill: [78, 108, 62],
  water: 0x6f9fb0, paddy: 0xa8b98a, court: 0x9aa87a, bedShallow: [150, 142, 112], bedDeep: [58, 82, 88], ring: 0xaaa47c,
  // By what the ground rests on (codes in ground.json): level ground from the DEM's plain (C), hills by the grade of their height, generated hills, banks.
  conf: { 0: [205, 200, 182], 1: [217, 164, 65], 2: [196, 81, 58], 3: [216, 191, 174], 4: [150, 146, 136], 5: [126, 120, 108] },
};

function buildGround({ meta, buf, gridBuf, levelBuf }) {
  const [x0, z0, x1, z1] = meta.domain;
  const datum = meta.datum_m;
  const pl = meta.plain;
  const plainAt = (x, z) => pl.a + (pl.bx * x) / 1000 + (pl.bz * z) / 1000 - datum;
  const toLinear = (v) => { const f = v / 255; return f <= 0.04045 ? f / 12.92 : ((f + 0.055) / 1.055) ** 2.4; };
  const lin = (rgb) => rgb.map(toLinear);
  const group = new THREE.Group();

  const decode = (c, extras = []) => {
    const q = new Int16Array(buf, c.pos, c.verts * 3), p = new Float32Array(c.verts * 3);
    for (let i = 0; i < c.verts; i++) { p[3 * i] = x0 + q[3 * i] / 10; p[3 * i + 1] = q[3 * i + 1] / 100; p[3 * i + 2] = z0 + q[3 * i + 2] / 10; }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(p, 3));
    g.setIndex(new THREE.BufferAttribute(new Uint16Array(buf, c.idx, c.indices), 1));
    const out = { g, p };
    for (const [name, Arr] of extras) out[name] = new Arr(buf, c[name], c.verts * (name === "rgb" ? 3 : 1));
    return out;
  };

  // Contour lines in the land's shader: model-space height + datum, so the 2x vertical option leaves them on whole metres.
  const contourUniform = { value: 0 };
  const withContours = (mat) => {
    mat.onBeforeCompile = (sh) => {
      sh.uniforms.uContours = contourUniform;
      sh.uniforms.uDatum = { value: datum };
      sh.vertexShader = sh.vertexShader.replace("#include <common>", "#include <common>\nvarying float vH;\nuniform float uDatum;").replace("#include <begin_vertex>", "#include <begin_vertex>\nvH = position.y + uDatum;");
      sh.fragmentShader = sh.fragmentShader.replace("#include <common>", "#include <common>\nvarying float vH;\nuniform float uContours;").replace(
        "#include <dithering_fragment>",
        "float w1 = fwidth(vH); float l1 = 1.0 - min(abs(fract(vH + 0.5) - 0.5) / max(w1, 1e-4), 1.0);\n" +
        "float w5 = fwidth(vH / 5.0); float l5 = 1.0 - min(abs(fract(vH / 5.0 + 0.5) - 0.5) / max(w5, 1e-4), 1.0);\n" +
        "gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.22, 0.18, 0.13), uContours * max(l1 * 0.4, l5 * 0.85));\n#include <dithering_fragment>");
    };
    return mat;
  };

  // Land.
  const landMat = withContours(new THREE.MeshLambertMaterial({ vertexColors: true }));
  const land = [], edgeVerts = [];
  const ins = lin(GROUND_COLOURS.inside), out = lin(GROUND_COLOURS.outside), hil = lin(GROUND_COLOURS.hill);
  const confLin = Object.fromEntries(Object.entries(GROUND_COLOURS.conf).map(([k, v]) => [k, lin(v)]));
  for (const c of meta.parts.land) {
    const d = decode(c, [["code", Uint8Array], ["hill", Uint8Array], ["yalt", Int16Array]]);
    const n = c.verts, plain = new Float32Array(n * 3), flat = new Float32Array(n * 3), conf = new Float32Array(n * 3), yFull = d.p.slice();
    for (let i = 0; i < n; i++) {
      const code = d.code[i], inside = code & 8 ? 1 : 0, t = d.hill[i] / 255;
      // a little seeded variation inside the walls, so large flats are not one colour
      const h = Math.sin(d.p[3 * i] * 12.9898 + d.p[3 * i + 2] * 78.233) * 43758.5453, noise = inside * ((h - Math.floor(h)) - 0.5) * 0.012;
      for (let k = 0; k < 3; k++) {
        const base = out[k] * (1 - inside) + ins[k] * inside;
        plain[3 * i + k] = Math.max(0, base * (1 - t) + hil[k] * t + noise);
        flat[3 * i + k] = (code & 7) === 3 ? Math.max(0, base + noise) : plain[3 * i + k]; // an assumed hill switched off: level ground's colour
        const cc = confLin[code & 7] || confLin[0];
        const tt = (code & 7) >= 1 && (code & 7) <= 3 ? Math.min(1, 0.35 + t * 2) : 1;
        conf[3 * i + k] = confLin[0][k] * (1 - tt) + cc[k] * tt;
      }
    }
    for (let i = 0; i < n; i++) { const x = d.p[3 * i], z = d.p[3 * i + 2]; if (Math.abs(x - x0) < 0.01 || Math.abs(x - x1) < 0.01 || Math.abs(z - z0) < 0.01 || Math.abs(z - z1) < 0.01) edgeVerts.push([x, d.p[3 * i + 1], z]); } // Round 20: the ring beyond meets these
    d.g.setAttribute("color", new THREE.BufferAttribute(plain.slice(), 3));
    d.g.computeVertexNormals();
    const m = new THREE.Mesh(d.g, landMat);
    group.add(m);
    land.push({ g: d.g, plain, flat, conf, yFull, yalt: d.yalt });
  }

  // Skirts: stone and rock banks, and the steps down into the paddy and the sunken court.
  for (const c of meta.parts.skirt) {
    const d = decode(c, [["rgb", Uint8Array]]);
    const col = new Float32Array(c.verts * 3);
    for (let i = 0; i < col.length; i++) col[i] = toLinear(d.rgb[i]);
    d.g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    d.g.computeVertexNormals();
    group.add(new THREE.Mesh(d.g, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide })));
  }

  // The water level of a point: 10 m cells naming the body (ground_level.u8), or null.
  const L = meta.levels, cells = new Uint8Array(levelBuf), levelOf = meta.bodies.map((b) => b.level);
  const waterLevelAt = (x, z) => {
    const i = Math.floor((x - L.x0) / L.cell_m), j = Math.floor((z - L.z0) / L.cell_m);
    if (i < 0 || j < 0 || i >= L.width || j >= L.height) return null;
    const v = cells[j * L.width + i];
    return v ? levelOf[v - 1] : null;
  };

  // Beds, tinted by depth below their body's level.
  const sh = lin(GROUND_COLOURS.bedShallow), dp = lin(GROUND_COLOURS.bedDeep);
  for (const c of meta.parts.bed) {
    const d = decode(c), col = new Float32Array(c.verts * 3);
    for (let i = 0; i < c.verts; i++) { const x = d.p[3 * i], z = d.p[3 * i + 2]; if (Math.abs(x - x0) < 0.01 || Math.abs(x - x1) < 0.01 || Math.abs(z - z0) < 0.01 || Math.abs(z - z1) < 0.01) edgeVerts.push([x, d.p[3 * i + 1], z]); }
    for (let i = 0; i < c.verts; i++) {
      const lev = waterLevelAt(d.p[3 * i], d.p[3 * i + 2]) ?? 0, t = Math.min(Math.max((lev - d.p[3 * i + 1]) / 2.2, 0), 1);
      for (let k = 0; k < 3; k++) col[3 * i + k] = sh[k] * (1 - t) + dp[k] * t;
    }
    d.g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    d.g.computeVertexNormals();
    group.add(new THREE.Mesh(d.g, new THREE.MeshLambertMaterial({ vertexColors: true })));
  }
  // Water: drawn after the bed, a little in front of it, so the shore never flickers.
  const waterMat = new THREE.MeshLambertMaterial({ color: GROUND_COLOURS.water, transparent: true, opacity: 0.84, polygonOffset: true, polygonOffsetFactor: -0.5, polygonOffsetUnits: -1 });
  for (const c of meta.parts.water) { const d = decode(c); d.g.computeVertexNormals(); const m = new THREE.Mesh(d.g, waterMat); m.renderOrder = 2; group.add(m); }
  for (const [key, hex] of [["paddy", GROUND_COLOURS.paddy], ["court", GROUND_COLOURS.court]]) {
    for (const c of meta.parts[key]) { const d = decode(c); d.g.computeVertexNormals(); group.add(new THREE.Mesh(d.g, withContours(new THREE.MeshLambertMaterial({ color: hex })))); }
  }

  // The plain past the modelled land: four quads on the plain's plane, a hair lower so the seam never fights.
  const FAR = 45000, ringMat = new THREE.MeshLambertMaterial({ color: GROUND_COLOURS.ring }), farQuads = []; // Round 20: hidden while around3d.js draws the ring and the backdrop
  for (const [ax, az, bx, bz] of [[-FAR, -FAR, FAR, z0], [-FAR, z1, FAR, FAR], [-FAR, z0, x0, z1], [x1, z0, FAR, z1]]) {
    const g = new THREE.BufferGeometry(), y = (x, z) => plainAt(x, z) - 0.05;
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array([ax, y(ax, az), az, bx, y(bx, az), az, bx, y(bx, bz), bz, ax, y(ax, bz), bz]), 3));
    g.setIndex([0, 2, 1, 0, 3, 2]);
    g.computeVertexNormals();
    const q = new THREE.Mesh(g, ringMat);
    farQuads.push(q);
    group.add(q);
  }

  // The surface one walks on: the land mesh on a 2.5 m lattice; water cells hold their bed; bridges count as land.
  const G = meta.grid, grid = new Int16Array(gridBuf);
  const cell = (i, j) => grid[j * G.width + i];
  const groundAt = (x, z) => {
    const u = (x - G.x0) / G.step_m, v = (z - G.z0) / G.step_m;
    if (u < 0 || v < 0 || u > G.width - 1 || v > G.height - 1) return plainAt(x, z);
    const i = Math.min(Math.floor(u), G.width - 2), j = Math.min(Math.floor(v), G.height - 2), a = u - i, b = v - j;
    let s = 0, wsum = 0;
    for (const [di, dj, w] of [[0, 0, (1 - a) * (1 - b)], [1, 0, a * (1 - b)], [0, 1, (1 - a) * b], [1, 1, a * b]]) {
      const c = cell(i + di, j + dj);
      if (c < G.water_below || w <= 0) continue;
      s += c * w; wsum += w;
    }
    return wsum > 1e-9 ? s / wsum / 100 : null; // null: water
  };

  let confOn = false, assumedOn = true;
  const recolour = () => { for (const l of land) { l.g.attributes.color.array.set(confOn ? l.conf : assumedOn ? l.plain : l.flat); l.g.attributes.color.needsUpdate = true; } };
  const setConf = (on) => { confOn = on; recolour(); };
  const setAssumed = (on) => {
    assumedOn = on;
    recolour();
    for (const l of land) {
      const p = l.g.attributes.position.array;
      for (let i = 0; i < l.yalt.length; i++) p[3 * i + 1] = on ? l.yFull[3 * i + 1] : l.yalt[i] / 100;
      l.g.attributes.position.needsUpdate = true;
      l.g.computeVertexNormals();
    }
  };
  const setContours = (on) => { contourUniform.value = on ? 1 : 0; };
  return { group, groundAt, waterLevelAt, plainAt, setConf, setAssumed, setContours, farQuads, edgeVerts };
}
