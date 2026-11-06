// Round 11: the hall kit. Every Qing hall of data/halls_1860.geojson drawn from numbers: data/kit_1860.json (scripts/kit1860.py) gives bays, porches, columns, platform, steps, roof class, tiles and band; the box gives footprint and heights.
// Classic script, loaded after halls3d.js and stonekit3d.js, before 3d.js; defines KIT_COLOURS and buildKit. No textures, no model files: plain geometry, merged per tile of the gardens.
// Two levels of detail per tile (THREE.LOD): near, every column, door, window, band, step and ridge; far, the platform, a body block and the roof's shape. The box stays the click target (halls3d.js); the kit adds its ranges to the box's entry, so selection and the confidence tint reach it.
// Local frame as in halls3d.js: s along the frontage, q towards the front, y up. The roof's own frame: x along the ridge, z across it.
// Colours are chosen for the view, not read from a source, except the tile colours the data names (typology section 5, the album's readings in research/scenes/halls.csv).
const KIT_COLOURS = {
  lacquer: [0x8a2f22, 0x7a2c22, 0x94402b], lacquerPale: 0xb98b7c,
  wall: [0x8e8a84, 0x99948c, 0x837f79], wallAssumed: 0xe2dbcf, plaster: 0xd9cfbe, gateWall: 0x9b3d2c,
  pane: 0x2b3137, sill: 0x7d7973,
  band: 0x2e6a6c, bracket: 0x3b7b70, bandRed: 0x7d2c20,
  platform: 0xb7b0a1, coping: 0xd2ccbe, step: 0xc8c1b1, marble: 0xe9e5dc,
  underside: 0x4b453d, fascia: 0x3a2a22,
  court: 0xb9b2a2, post: 0x8a3b2a, ridgeDark: 0.78,
};

function buildKit({ spec, halls, datum, groundAt, toXZ, paths }) {
  const TILE = 180, NEAR = 420;
  const tiles = new Map();
  const groups = {}; // key -> meshes
  const tileOf = (x, z) => {
    const i = Math.floor(x / TILE), j = Math.floor(z / TILE), k = i * 7919 + j;
    if (!tiles.has(k)) tiles.set(k, { cx: (i + 0.5) * TILE, cz: (j + 0.5) * TILE, near: null, far: null });
    return tiles.get(k);
  };
  const bufOf = (T, level, key) => (T[level][key] ||= new HallBuffer(key));
  const tileHex = (t) => HALL_COLOURS.tile[t] ?? HALL_COLOURS.tile.grey;
  const shade = (hex, k) => { const c = new THREE.Color(hex); c.multiplyScalar(k); return c.getHex(); };

  // ---- primitives in a local frame ----
  function prims(B, at) {
    const P = {};
    P.q = (a, b, c, d) => B.quad(a, b, c, d);
    P.t = (a, b, c) => B.tri(a, b, c);
    // an axis box in the local frame; faces: top, and the four sides; bottom only if asked
    P.box = (s0, s1, q0, q1, y0, y1, bottom) => {
      const c = [[s0, q1], [s1, q1], [s1, q0], [s0, q0]];
      for (let i = 0; i < 4; i++) { const [as, aq] = c[i], [bs, bq] = c[(i + 1) % 4]; B.quad(at(as, y1, aq), at(as, y0, aq), at(bs, y0, bq), at(bs, y1, bq)); }
      B.quad(at(s0, y1, q1), at(s1, y1, q1), at(s1, y1, q0), at(s0, y1, q0));
      if (bottom) B.quad(at(s0, y0, q0), at(s1, y0, q0), at(s1, y0, q1), at(s0, y0, q1));
    };
    // a post: four sides, no top
    P.post = (s0, s1, q0, q1, y0, y1) => {
      const c = [[s0, q1], [s1, q1], [s1, q0], [s0, q0]];
      for (let i = 0; i < 4; i++) { const [as, aq] = c[i], [bs, bq] = c[(i + 1) % 4]; B.quad(at(as, y1, aq), at(as, y0, aq), at(bs, y0, bq), at(bs, y1, bq)); }
    };
    // a vertical rectangle in the plane q = q0 (or s = s0 with `side`), from s0..s1, y0..y1
    P.panelQ = (s0, s1, q0, y0, y1) => B.quad(at(s0, y1, q0), at(s0, y0, q0), at(s1, y0, q0), at(s1, y1, q0));
    P.panelS = (q0, q1, s0, y0, y1) => B.quad(at(s0, y1, q0), at(s0, y0, q0), at(s0, y0, q1), at(s0, y1, q1));
    // a ring of four boxes along a rectangle's sides: a beam or a band
    P.ring = (hs, hq, t, y0, y1, out = 0) => {
      P.box(-hs - out, hs + out, hq - t + out, hq + out, y0, y1, true);
      P.box(-hs - out, hs + out, -hq - out, -hq + t - out, y0, y1, true);
      P.box(-hs - out, -hs + t - out, -hq + t - out, hq - t + out, y0, y1, true);
      P.box(hs - t + out, hs + out, -hq + t - out, hq - t + out, y0, y1, true);
    };
    return P;
  }

  // ---- the roof: slopes from the eave edge (v = 0) to the ridge (v = 1), a concave profile from the 举架 steps, corner lift 起翘 on hipped forms ----
  function profile(ju, curve) {
    const n = ju.length, ys = [0];
    for (let i = 0; i < n; i++) ys.push(ys[i] + ju[i] / n);
    const top = ys[n];
    return (v) => {
      const x = Math.min(Math.max(v, 0), 1) * n, i = Math.min(Math.floor(x), n - 1), f = x - i;
      const yv = (ys[i] + (ys[i + 1] - ys[i]) * f) / top;
      return Math.min(Math.max(v + (yv - v) * curve, 0), 1);
    };
  }

  // hx, hz half sizes of the roof's outline (x along the ridge); y0 eave edge, y1 ridge; o: options
  function roof(B, P, hx, hz, y0, y1, o) {
    const { form, rolled, prof, lift, near, tile, edge, gableHex, sides, bargeHex, ridgeHex, grade } = o;
    const Y = (v) => y0 + (yTop - y0) * prof(v);
    const band = rolled ? Math.min(0.12 * hz, 0.6) : 0;
    const yTop = rolled ? y1 - 0.6 * band : y1;
    const nv = near ? Math.max(3, (o.steps || 2) + 1) : 2;
    const vb = form === "xs" ? 0.4 : 1; // 歇山: the hip ends where the gable 山花 begins; 45 degrees in plan
    const q = (v) => hz - (hz - band) * v;
    const rHalf = Math.max(hx - 0.85 * (hz - band), 0.05 * hx); // 庑殿 with a little 推山: the ridge longer than 45-degree hips would leave
    const L = (v) => form === "wd" ? hx - (hx - rHalf) * v : form === "xs" ? hx - (hz - band) * Math.min(v, vb) : hx;
    const Lc = (form === "wd" || form === "xs") ? Math.min(0.55, 0.04 * (hx + hz)) * (o.liftK || 1) : 0;
    const up = (t, v) => Lc * Math.max(0, (Math.abs(t) - 0.45) / 0.55) ** 2 * (1 - v) ** 2;
    const nu = near ? Math.min(10, Math.max(4, Math.round(hx / 2.2))) : 2;
    const nw = near ? 4 : 2;
    const tileC = tileHex(tile), edgeC = edge ? tileHex(edge) : null;
    const colourAt = (v0) => B.set(edgeC && v0 === 0 ? edgeC : tileC, grade, true);
    // front and back slopes
    for (const sg of [1, -1]) {
      for (let j = 0; j < nv; j++) {
        const v0 = j / nv, v1 = (j + 1) / nv;
        colourAt(j);
        for (let i = 0; i < nu; i++) {
          const t0 = -1 + (2 * i) / nu, t1 = -1 + (2 * (i + 1)) / nu;
          const pt = (t, v) => P(t * L(v), Y(v) + up(t, v), sg * q(v));
          B.quad(pt(t0, v0), pt(t1, v0), pt(t1, v1), pt(t0, v1));
        }
      }
    }
    // hip ends
    if (form === "wd" || form === "xs") {
      for (const sx of [1, -1]) {
        const jMax = Math.round(nv * vb) || 1;
        for (let j = 0; j < jMax; j++) {
          const v0 = (j / jMax) * vb, v1 = ((j + 1) / jMax) * vb;
          colourAt(j);
          for (let i = 0; i < nw; i++) {
            const w0 = -1 + (2 * i) / nw, w1 = -1 + (2 * (i + 1)) / nw;
            const pt = (w, v) => P(sx * L(v), Y(v) + up(w, v), w * q(v));
            B.quad(pt(w0, v0), pt(w1, v0), pt(w1, v1), pt(w0, v1));
          }
        }
      }
    }
    // the rolled top 卷棚: an arc over the two ridge purlins
    const arc = [];
    if (rolled) for (let k = 0; k <= 4; k++) { const t = k / 4; arc.push([band * Math.cos(Math.PI * t), yTop + (y1 - yTop) * Math.sin(Math.PI * t)]); }
    if (rolled) {
      B.set(tileC, grade, true);
      const Lr = L(1);
      for (let k = 0; k < 4; k++) B.quad(P(-Lr, arc[k][1], arc[k][0]), P(Lr, arc[k][1], arc[k][0]), P(Lr, arc[k + 1][1], arc[k + 1][0]), P(-Lr, arc[k + 1][1], arc[k + 1][0]));
    }
    // gables: 歇山's 山花 above the hips; 硬山 and 悬山 ends
    const gable = (xg, vFrom) => {
      B.set(gableHex, grade);
      const pts = [];
      const nn = near ? nv : 2;
      for (let j = 0; j <= nn; j++) { const v = vFrom + ((1 - vFrom) * j) / nn; pts.push([q(v), Y(v)]); }
      const topPts = rolled ? arc : [[0, yTop]];
      for (const sx of [1, -1]) {
        const ring = pts.map(([z, y]) => [z, y]).concat(topPts.slice(rolled ? 1 : 0, rolled ? -1 : 1)).concat(pts.slice().reverse().map(([z, y]) => [-z, y]));
        const base = Y(vFrom);
        for (let k = 0; k < ring.length - 1; k++) B.quad(P(sx * xg, base, ring[k][0]), P(sx * xg, ring[k][1] - 0.02, ring[k][0]), P(sx * xg, ring[k + 1][1] - 0.02, ring[k + 1][0]), P(sx * xg, base, ring[k + 1][0]));
      }
    };
    if (form === "xs") gable(L(vb), vb);
    if (form === "ys" || form === "xu") gable(o.gableX ?? hx, o.gableFrom ?? 0);
    // 悬山: the barge board 博风 along each verge
    if (form === "xu" && near) {
      B.set(bargeHex, grade);
      for (const sx of [1, -1]) for (let j = 0; j < nv; j++) {
        const v0 = j / nv, v1 = (j + 1) / nv;
        for (const sg of [1, -1]) B.quad(P(sx * hx, Y(v0) - 0.32, sg * q(v0)), P(sx * hx, Y(v0) + 0.02, sg * q(v0)), P(sx * hx, Y(v1) + 0.02, sg * q(v1)), P(sx * hx, Y(v1) - 0.32, sg * q(v1)));
      }
    }
    // the eave's thickness and its underside: a fascia strip and a soffit copy of the lowest band
    if (near) {
      B.set(KIT_COLOURS.underside, grade, true);
      const v1 = 1 / nv;
      for (const sg of [1, -1]) for (let i = 0; i < nu; i++) {
        const t0 = -1 + (2 * i) / nu, t1 = -1 + (2 * (i + 1)) / nu;
        const pt = (t, v, dy) => P(t * L(v), Y(v) + up(t, v) - dy, sg * q(v));
        B.quad(pt(t0, 0, 0.22), pt(t1, 0, 0.22), pt(t1, v1, 0.22), pt(t0, v1, 0.22));
        B.quad(pt(t0, 0, 0), pt(t1, 0, 0), pt(t1, 0, 0.22), pt(t0, 0, 0.22));
      }
      if (form === "wd" || form === "xs") for (const sx of [1, -1]) for (let i = 0; i < nw; i++) {
        const w0 = -1 + (2 * i) / nw, w1 = -1 + (2 * (i + 1)) / nw;
        const pt = (w, v, dy) => P(sx * L(v), Y(v) + up(w, v) - dy, w * q(v));
        B.quad(pt(w0, 0, 0), pt(w1, 0, 0), pt(w1, 0, 0.22), pt(w0, 0, 0.22));
      }
    }
    // ridges: 正脊 with end blocks on a sharp ridge, 垂脊 and 戗脊 as raised strips
    if (near) {
      B.set(ridgeHex, grade, true);
      const Lr = L(1), hr = Math.min(0.9, Math.max(0.3, 0.1 + 0.06 * hz));
      if (!rolled && Lr > 0.3) {
        const r = [];
        r.push([-Lr, -0.16], [Lr, -0.16], [Lr, 0.16], [-Lr, 0.16]);
        const yb = y1 - 0.05;
        B.quad(P(-Lr, yb + hr, -0.16), P(Lr, yb + hr, -0.16), P(Lr, yb + hr, 0.16), P(-Lr, yb + hr, 0.16));
        B.quad(P(-Lr, yb, 0.16), P(Lr, yb, 0.16), P(Lr, yb + hr, 0.16), P(-Lr, yb + hr, 0.16));
        B.quad(P(Lr, yb, -0.16), P(-Lr, yb, -0.16), P(-Lr, yb + hr, -0.16), P(Lr, yb + hr, -0.16));
        if (form !== "cj") for (const sx of [1, -1]) {
          const x0 = sx * Lr, x1 = sx * (Lr - 0.5);
          B.quad(P(x0, yb, 0.2), P(x1, yb, 0.2), P(x1, yb + hr * 1.9, 0.2), P(x0, yb + hr * 1.7, 0.2));
          B.quad(P(x1, yb, -0.2), P(x0, yb, -0.2), P(x0, yb + hr * 1.7, -0.2), P(x1, yb + hr * 1.9, -0.2));
          B.quad(P(x0, yb + hr * 1.7, -0.2), P(x0, yb + hr * 1.7, 0.2), P(x1, yb + hr * 1.9, 0.2), P(x1, yb + hr * 1.9, -0.2));
        }
      }
      const strip = (pts, w) => {
        for (let k = 0; k < pts.length - 1; k++) {
          const [a, b] = [pts[k], pts[k + 1]];
          B.quad(P(a[0], a[1], a[2]), P(b[0], b[1], b[2]), P(b[0], b[1] + w, b[2]), P(a[0], a[1] + w, a[2]));
        }
      };
      const hipLine = (sx, sg, vEnd) => { const pts = []; for (let j = 0; j <= nv; j++) { const v = (vEnd * j) / nv; pts.push([sx * L(v), Y(v) + up(1, v), sg * q(v)]); } return pts; };
      if (form === "wd" || form === "xs") for (const sx of [1, -1]) for (const sg of [1, -1]) strip(hipLine(sx, sg, vb), 0.22);
      if (form === "xs" || form === "ys" || form === "xu") {
        const xv = form === "xs" ? L(vb) : hx;
        for (const sx of [1, -1]) for (const sg of [1, -1]) {
          const pts = []; const vf = form === "xs" ? vb : 0;
          for (let j = 0; j <= nv; j++) { const v = vf + ((1 - vf) * j) / nv; pts.push([sx * (xv - 0.15), Y(v), sg * q(v)]); }
          strip(pts, 0.2);
        }
      }
    }
  }

  // 攒尖: n sides about the centre (4: the rectangle itself), up to an apex
  function pyramid(B, at, hx, hz, y0, y1, o) {
    const { sides, prof, near, tile, edge, grade } = o;
    const Y = (v) => y0 + (y1 - y0) * prof(v);
    let C;
    if (sides === 4) C = [[-hx, hz], [hx, hz], [hx, -hz], [-hx, -hz]];
    else { const R = Math.min(hx, hz) / Math.cos(Math.PI / sides); C = []; for (let k = 0; k < sides; k++) { const t = Math.PI / 2 + (k + 0.5) * (2 * Math.PI / sides); C.push([R * Math.cos(t), R * Math.sin(t)]); } }
    const Lc = Math.min(0.5, 0.06 * (hx + hz)) * (o.liftK || 1);
    const up = (t, v) => Lc * Math.max(0, (Math.abs(t) - 0.4) / 0.6) ** 2 * (1 - v) ** 2;
    const nv = near ? 5 : 2, nu = near ? 4 : 1;
    const tileC = tileHex(tile), edgeC = edge ? tileHex(edge) : null;
    for (let k = 0; k < C.length; k++) {
      const a = C[k], b = C[(k + 1) % C.length];
      for (let j = 0; j < nv; j++) {
        B.set(edgeC && j === 0 ? edgeC : tileC, grade, true);
        const v0 = j / nv, v1 = (j + 1) / nv;
        for (let i = 0; i < nu; i++) {
          const t0 = -1 + (2 * i) / nu, t1 = -1 + (2 * (i + 1)) / nu;
          const pt = (t, v) => { const f = (t + 1) / 2, x = (a[0] + (b[0] - a[0]) * f) * (1 - v), z = (a[1] + (b[1] - a[1]) * f) * (1 - v); return at(x, Y(v) + up(t, v), z); };
          B.quad(pt(t0, v0), pt(t1, v0), pt(t1, v1), pt(t0, v1));
        }
      }
    }
    if (near) {
      B.set(KIT_COLOURS.underside, grade, true);
      for (let k = 0; k < C.length; k++) {
        const a = C[k], b = C[(k + 1) % C.length];
        B.quad(at(a[0], Y(0) + Lc, a[1]), at(b[0], Y(0) + Lc, b[1]), at(b[0], Y(0) - 0.2, b[1]), at(a[0], Y(0) - 0.2, a[1]));
      }
      // the finial 宝顶
      B.set(shade(tileC, 0.8), grade, true);
      const r = Math.min(0.45, 0.08 * (hx + hz)), yA = y1;
      const tip = at(0, yA + 3 * r, 0);
      const ring = [[r, 0], [0, r], [-r, 0], [0, -r]].map(([x, z]) => at(x, yA + r, z));
      for (let k = 0; k < 4; k++) { B.tri(ring[k], ring[(k + 1) % 4], tip); B.tri(at(0, yA - 0.1, 0), ring[(k + 1) % 4], ring[k]); }
      // hip strips
      B.set(shade(tileC, KIT_COLOURS.ridgeDark), grade, true);
      for (const a of C) for (let j = 0; j < nv; j++) {
        const v0 = j / nv, v1 = (j + 1) / nv;
        const p = (v, dy) => at(a[0] * (1 - v), Y(v) + up(1, v) + dy, a[1] * (1 - v));
        B.quad(p(v0, 0), p(v1, 0), p(v1, 0.2), p(v0, 0.2));
      }
    }
    return C;
  }

  // ---- a flight of steps 踏跺 out of a platform's side, centred `off` along it; left out where the ground under it is water; its blocks reach the lowest ground under it ----
  function along3(e, side) { return side === "front" || side === "back" ? Math.max(e.b ? e.b[Math.floor(e.b.length / 2)] : 3, 2.4) : 2.6; }
  function flight(B, K, at, side, off, hf, hd, plTop, o, width, g, near, base) {
    const dir = { front: [0, 1], back: [0, -1], right: [1, 0], left: [-1, 0] }[side];
    const along = dir[0] === 0, edgeD = along ? hd : hf;
    width = Math.min(width, (along ? hf : hd) * 1.6);
    const loc = (out, lat) => (along ? [off + lat, dir[1] * (edgeD + out)] : [dir[0] * (edgeD + out), off + lat]);
    const gAt = (out, lat) => { const [s0, q0] = loc(out, lat), w = at(s0, 0, q0, true); return groundAt ? groundAt(w[0], w[2]) : base; };
    const yFoot0 = gAt(o * 0.6, 0);
    if (yFoot0 === null) return null;
    const h0 = plTop - yFoot0;
    if (h0 < 0.12) return null;
    const n = Math.max(1, Math.round(h0 / 0.15)), tread = Math.min(0.3, o / Math.max(1, n - 1)), run = (n - 1) * tread;
    const samples = [gAt(0.05, -width / 2), gAt(0.05, width / 2), gAt(run + 0.05, -width / 2), gAt(run + 0.05, width / 2), gAt(run, 0), gAt(run + 0.4, 0)];
    if (samples.some((v) => v === null)) return null; // a side over the water gets no steps (a landing serves it)
    const yG = samples[4], yLow = Math.min(...samples), h = plTop - yG, rise = h / n;
    B.set(KIT_COLOURS.step, g);
    const span = (d0, d1, y1) => {
      const w = width / 2;
      if (along) { const q0 = dir[1] * (edgeD + d0), q1 = dir[1] * (edgeD + d1); K.box(off - w, off + w, Math.min(q0, q1), Math.max(q0, q1), yLow - 0.15, y1); }
      else { const s0 = dir[0] * (edgeD + d0), s1 = dir[0] * (edgeD + d1); K.box(Math.min(s0, s1), Math.max(s0, s1), off - w, off + w, yLow - 0.15, y1); }
    };
    if (near) for (let k = 1; k < n; k++) span((k - 1) * tread, k * tread, plTop - k * rise); // far beyond the near reach the steps are left out: under a pixel
    const [fs, fq] = loc(run, 0), fw = at(fs, 0, fq, true);
    return [side, +fw[0].toFixed(2), +fw[2].toFixed(2), +yG.toFixed(2), +plTop.toFixed(2), +run.toFixed(2), +width.toFixed(2)];
  }

  // ---- a Qing hall ----
  function drawHall(B, b, e, near, track) {
    const p = b.props, hf = b.hf, hd = b.hd, g = p.confidence, fg = e.g;
    let part = "body";
    const at = (s, y, q, probe) => {
      if (!probe) { const ex = Math.max(Math.abs(s) - hf, Math.abs(q) - hd, 0); if (ex > track[part]) track[part] = ex; }
      return [b.cx + b.u[0] * s + b.a[0] * q, y, b.cz + b.u[1] * s + b.a[1] * q];
    };
    const K = prims(B, at);
    const base = b.base, foot = b.foot, plTop = base + p.platform_m;
    const eave = base + p.eave_m, ridge = base + p.ridge_m;
    const CS = hf - e.e, CQ = hd - e.e, o = e.o;
    const lac = p.assumed ? KIT_COLOURS.lacquerPale : KIT_COLOURS.lacquer[e.sh[0]];
    const wallC = p.assumed ? KIT_COLOURS.wallAssumed : KIT_COLOURS.wall[e.sh[1]];
    const prof = profile(e.ju, e.v[0]);
    const tileC = tileHex(e.t);
    const roofOpts = { rolled: Boolean(e.rl), prof, liftK: e.v[1], near, tile: e.t, edge: e.te, gableHex: e.rf === "xs" ? lac : wallC, bargeHex: shade(lac, 0.6), ridgeHex: shade(tileC, KIT_COLOURS.ridgeDark), grade: fg, steps: e.ju.length };

    // 1. the platform 台基, its coping, the steps 踏跺, the balustrade
    part = "body";
    B.set(KIT_COLOURS.platform, g);
    K.box(-hf, hf, -hd, hd, foot, plTop);
    if (near && p.platform_m > 0.25) { B.set(KIT_COLOURS.coping, g); K.box(-hf - 0.03, hf + 0.03, -hd - 0.03, hd + 0.03, plTop - 0.14, plTop); }
    const stepsOut = [];
    part = "steps";
    for (const side of e.st || []) for (const off of [0, ...((e.so || {})[side] || [])]) {
      const fl = flight(B, K, at, side, off, hf, hd, plTop, o, along3(e, side), g, near, base);
      if (fl) stepsOut.push(fl);
    }
    part = "body";
    if (near && e.bal) {
      B.set(KIT_COLOURS.marble, g);
      const hb = 0.85, inset = 0.12, s0 = hf - inset, q0 = hd - inset;
      const gapsQ = (e.st || []).filter((x) => x === "front" || x === "back"), wF = Math.max(e.b[Math.floor(e.b.length / 2)] || 3, 2.4) / 2;
      const rail = (a0, a1, fixed, onS) => {
        if (a1 - a0 < 0.4) return;
        if (onS) K.box(fixed - 0.1, fixed + 0.1, a0, a1, plTop + hb - 0.12, plTop + hb); else K.box(a0, a1, fixed - 0.1, fixed + 0.1, plTop + hb - 0.12, plTop + hb);
        if (onS) K.box(fixed - 0.08, fixed + 0.08, a0, a1, plTop, plTop + 0.18); else K.box(a0, a1, fixed - 0.08, fixed + 0.08, plTop, plTop + 0.18);
        const np = Math.max(1, Math.round((a1 - a0) / 2.2));
        for (let k = 0; k <= np; k++) { const t = a0 + ((a1 - a0) * k) / np; if (onS) K.post(fixed - 0.11, fixed + 0.11, t - 0.11, t + 0.11, plTop, plTop + hb + 0.15); else K.post(t - 0.11, t + 0.11, fixed - 0.11, fixed + 0.11, plTop, plTop + hb + 0.15); }
      };
      for (const sg of [1, -1]) {
        const gap = gapsQ.includes(sg > 0 ? "front" : "back");
        if (gap) { rail(-s0, -wF, sg * q0, false); rail(wF, s0, sg * q0, false); } else rail(-s0, s0, sg * q0, false);
      }
      for (const sg of [1, -1]) {
        const gap = (e.st || []).includes(sg > 0 ? "right" : "left");
        if (gap) { rail(-q0, -1.3, sg * s0, true); rail(1.3, q0, sg * s0, true); } else rail(-q0, q0, sg * s0, true);
      }
    }

    // 2. the body by kind
    const bandH = e.bd === "br" ? 0.85 : 0.42; // beam 额枋, with bracket sets 斗拱 above it on 大式 halls
    const colTop = (top) => top - bandH;
    // bay boundaries along the frontage, and across the depth
    const xs = [-CS]; for (const w of e.b) xs.push(xs[xs.length - 1] + w);
    xs[xs.length - 1] = CS;
    const qs = [CQ]; for (const w of e.d) qs.push(qs[qs.length - 1] - w);
    qs[qs.length - 1] = -CQ;

    const columns = (hs, hq, y0, y1, xsL, qsL) => {
      if (!near) return;
      B.set(lac, g);
      const r = e.dia / 2;
      const seen = new Set();
      const put = (s, q) => { const k = `${s.toFixed(2)},${q.toFixed(2)}`; if (seen.has(k)) return; seen.add(k); K.post(s - r, s + r, q - r, q + r, y0, y1); };
      for (const s of xsL) { put(s, hq); put(s, -hq); }
      for (const q of qsL) { put(-hs, q); put(hs, q); }
    };
    // the roof's height above a point `out` beyond the column line (the main roof's profile), so that nothing below the eave pokes through it
    const RSq = Math.min(CS, CQ) + o, bandR = e.rl ? Math.min(0.12 * RSq, 0.6) : 0, yTopR = e.rl ? ridge - 0.6 * bandR : ridge, profR = profile(e.ju, e.v[0]);
    const roofAbove = (out) => (eave - o * 0.5) + (yTopR - (eave - o * 0.5)) * profR(Math.max(0, o - out) / Math.max(RSq - bandR, 0.5));
    const bands = (hs, hq, top, out = 0, cap = Infinity) => {
      // the beam ring at the column line, and on 大式 halls the bracket band above it, stepping out; each under the roof
      const lim = (d) => Math.min(top, cap, roofAbove(d) - 0.06);
      B.set(KIT_COLOURS.band, fg);
      const bt = Math.max(e.dia * 0.9, 0.22);
      if (e.bd === "br") {
        const y3 = lim(0.22), y2 = Math.min(lim(0.12), y3 - 0.1), y1 = Math.min(top - 0.5, y2 - 0.15);
        K.ring(hs, hq, bt, top - bandH, y1, out);
        B.set(KIT_COLOURS.bracket, fg);
        K.ring(hs + 0.12, hq + 0.12, bt + 0.12, y1, y2, out);
        B.set(KIT_COLOURS.bandRed, fg);
        K.ring(hs + 0.22, hq + 0.22, bt + 0.22, y2, y3, out);
      } else K.ring(hs, hq, bt, top - bandH, Math.max(top - bandH + 0.15, lim(bt / 2)), out);
    };
    // one bay of a façade: a door 隔扇 or a window 槛窗 over a sill wall 槛墙, the pane set back behind its frame, with reveals; lattice bars and the transom 横披 above. Faces, not boxes: each part one quad.
    const opening = (sa, sb, qf, sgn, y0, y1, door, onS) => {
      const w = sb - sa;
      if (!near || w < 0.6 || y1 - y0 < 1.2) return;
      const F = (a0, a1, yy0, yy1, d) => { const f = qf - sgn * d; if (onS) K.panelS(a0, a1, f, yy0, yy1); else K.panelQ(a0, a1, f, yy0, yy1); };
      const R = (a, yy0, yy1, d0, d1) => { const f0 = qf - sgn * d0, f1 = qf - sgn * d1; if (onS) B.quad(at(f0, yy1, a), at(f0, yy0, a), at(f1, yy0, a), at(f1, yy1, a)); else B.quad(at(a, yy1, f0), at(a, yy0, f0), at(a, yy0, f1), at(a, yy1, f1)); };
      const Rh = (a0, a1, yy, d0, d1) => { const f0 = qf - sgn * d0, f1 = qf - sgn * d1; if (onS) B.quad(at(f0, yy, a0), at(f0, yy, a1), at(f1, yy, a1), at(f1, yy, a0)); else B.quad(at(a0, yy, f0), at(a1, yy, f0), at(a1, yy, f1), at(a0, yy, f1)); };
      const H = y1 - y0, sill = door ? 0 : Math.min(0.9, 0.3 * H), lint = y0 + Math.max(H * 0.8, sill + 1.2), fr = 0.1;
      if (door && e.k === "gate") {
        // a gate's plank doors 板门, set back in the opening, with the frame and a transom
        B.set(lac, fg);
        F(sa + fr, sb - fr, y0, lint, 0.3);
        R(sa + fr, y0, y1, 0, 0.3); R(sb - fr, y0, y1, 0, 0.3);
        F(sa, sa + fr, y0, y1, 0); F(sb - fr, sb, y0, y1, 0); F(sa, sb, lint - 0.08, lint + 0.08, 0); F(sa, sb, y1 - 0.12, y1, 0);
        B.set(shade(lac, 0.75), fg);
        F((sa + sb) / 2 - 0.03, (sa + sb) / 2 + 0.03, y0, lint, 0.28);
        B.set(KIT_COLOURS.pane, fg);
        F(sa + fr, sb - fr, lint, y1, 0.12);
        return;
      }
      if (sill > 0) { B.set(wallC, g); F(sa, sb, y0, y0 + sill, -0.04); Rh(sa, sb, y0 + sill, -0.04, 0.12); }
      B.set(KIT_COLOURS.pane, fg);
      F(sa + fr, sb - fr, y0 + sill, y1, 0.12);
      B.set(lac, fg);
      F(sa, sa + fr, y0 + sill, y1, 0);
      F(sb - fr, sb, y0 + sill, y1, 0);
      F(sa, sb, lint - 0.06, lint + 0.06, 0);
      F(sa, sb, y1 - 0.1, y1, 0);
      if (sill > 0) F(sa, sb, y0 + sill, y0 + sill + 0.08, 0);
      R(sa + fr, y0 + sill, y1, 0, 0.12);
      R(sb - fr, y0 + sill, y1, 0, 0.12);
      Rh(sa + fr, sb - fr, y1 - 0.1, 0, 0.12);
      const leaves = door ? 4 : Math.max(2, Math.round(w / 1.1));
      for (let k = 1; k < leaves; k++) { const s = sa + (w * k) / leaves; F(s - 0.04, s + 0.04, y0 + sill, lint, 0.04); }
      const yk = y0 + (lint - y0) * 0.42;
      if (door) { F(sa + fr, sb - fr, y0, yk, 0.03); F(sa + fr, sb - fr, yk + (lint - yk) * 0.12, yk + (lint - yk) * 0.17, 0.02); }
      const yL0 = door ? yk : y0 + sill;
      for (let k = 1; k < 3; k++) { const yy = yL0 + ((lint - yL0) * k) / 3; F(sa + fr, sb - fr, yy - 0.025, yy + 0.025, 0.06); }
      const nvb = Math.max(2, Math.round(w / 0.55));
      for (let k = 1; k < nvb; k++) { const s = sa + (w * k) / nvb; F(s - 0.022, s + 0.022, yL0, lint, 0.07); }
      const nt = Math.max(2, Math.round(w / 0.7));
      for (let k = 1; k < nt; k++) { const s = sa + (w * k) / nt; F(s - 0.02, s + 0.02, lint, y1, 0.07); }
    };

    const body = (hs, hq, pf, pb, ps, y0, y1, firstFloor, xsL, qsL) => {
      // hs, hq: the column line; walls at the porch lines inside it; y1 the eave (top of the band)
      const top = colTop(y1);
      const qw = hq - pf, qr = -(hq - pb), sw = hs - ps;
      if (!near) {
        // far: a body block and the eave's colour band
        B.set(e.rf === "ys" ? wallC : shade(lac, 0.75), g);
        K.box(-sw, sw, qr, qw, y0, y1);
        return;
      }
      columns(hs, hq, y0, top, xsL, qsL);
      bands(hs, hq, y1, 0, y1 >= eave - 0.01 ? Infinity : y1);
      // the ceiling over the porches and the rooms, at the beam's foot
      B.set(KIT_COLOURS.underside, g, true);
      B.quad(at(-hs, top, hq), at(hs, top, hq), at(hs, top, -hq), at(-hs, top, -hq));
      // front and back
      const doorAt = new Set(e.dr || []);
      for (const [qf, sgn, isFront] of [[qw, 1, true], [qr, -1, false]]) {
        for (let i = 0; i < xsL.length - 1; i++) {
          const sa = Math.max(xsL[i], -sw), sb = Math.min(xsL[i + 1], sw);
          if (sb - sa < 0.5) continue;
          const door = firstFloor && (isFront ? doorAt.has(i) : e.rr === "d" && i === Math.floor((xsL.length - 1) / 2));
          if (e.k === "gate" && !door) { B.set(KIT_COLOURS.gateWall, g); K.box(sa, sb, Math.min(qf, qf - sgn * 0.5), Math.max(qf, qf - sgn * 0.5), y0, top); continue; }
          opening(sa, sb, qf, sgn, y0, top, door, false);
          // a red post at the wall line's columns (金柱) behind a porch
          if ((isFront ? pf : pb) > 0) { B.set(lac, g); K.post(sa - e.dia / 2, sa + e.dia / 2, qf - e.dia / 2, qf + e.dia / 2, y0, top); }
        }
      }
      // the sides
      if (e.rf === "ys") {
        // 硬山: the gable walls, brick, with a plaster panel and the 墀头 at the front
        B.set(wallC, g);
        for (const sg of [1, -1]) K.box(sg > 0 ? hs - 0.2 : -hs - 0.42, sg > 0 ? hs + 0.42 : -hs + 0.2, -hq - 0.42, hq + 0.42, y0, y1 + 0.1);
        B.set(KIT_COLOURS.plaster, g);
        for (const sg of [1, -1]) K.panelS(-hq + 0.6, hq - 0.6, sg * (hs + 0.44), y0 + 0.9, y1 - 0.5);
      } else {
        const qsIn = qsL.filter((q) => q <= qw + 0.01 && q >= qr - 0.01);
        for (const sg of [1, -1]) {
          for (let i = 0; i < qsIn.length - 1; i++) {
            const qa = qsIn[i + 1], qb = qsIn[i];
            if (qb - qa < 0.6) continue;
            opening(qa, qb, sg * sw, sg, y0, top, false, true);
          }
          if (qsIn.length < 2) { B.set(wallC, g); K.box(sg > 0 ? sw - 0.3 : -sw, sg > 0 ? sw : -sw + 0.3, qr, qw, y0, top); }
        }
      }
      // the walls' inner volume closes the openings from behind: one dark box inside, never seen except through the panes' gaps
      B.set(KIT_COLOURS.pane, fg);
      K.box(-sw + 0.15, sw - 0.15, qr + 0.15, qw - 0.15, y0, top - 0.05);
    };

    const roofOver = (hs, hq, y0, y1, extra = {}) => {
      part = "roof";
      const along = hs >= hq || extra.alongS;
      const P = (x, y, z) => (along ? at(x, y, z) : at(z, y, -x));
      const hx = along ? hs : hq, hz = along ? hq : hs;
      const opts = Object.assign({}, roofOpts, extra);
      if (opts.form === "cj") pyramid(B, at, hs, hq, y0, y1, opts);
      else {
        const res = Object.assign({}, opts);
        let hxr = hx;
        if (opts.form === "ys" && !extra.keepX) { hxr = Math.min(hx, hx - o + 0.45); res.gableX = hxr; }
        if (opts.form === "xu") { res.gableX = hx - Math.min(0.6, o * 0.5); }
        roof(B, P, hxr, hz, y0, y1, res);
      }
      part = "body";
    };

    const RS = CS + o, RQ = CQ + o, tip = eave - o * 0.5;
    const form = e.rf;
    if (e.k === "pavilion") {
      // open: columns, a bench rail 坐凳 between them but on the step sides, a hanging fascia 倒挂楣子, the beam
      const sides = e.sd || 4;
      const top = colTop(eave);
      if (sides === 4) {
        if (near) {
          columns(CS, CQ, plTop, top, xs, [CQ, -CQ]);
          bands(CS, CQ, eave);
          B.set(lac, fg);
          const fasc = (a0, a1, f, onS) => { if (onS) K.box(f - 0.05, f + 0.05, a0, a1, top - 0.32, top); else K.box(a0, a1, f - 0.05, f + 0.05, top - 0.32, top); };
          const bench = (a0, a1, f, onS) => { if (onS) K.box(f - 0.18, f + 0.18, a0, a1, plTop, plTop + 0.48); else K.box(a0, a1, f - 0.18, f + 0.18, plTop, plTop + 0.48); };
          for (const sg of [1, -1]) { fasc(-CS, CS, sg * CQ, false); fasc(-CQ, CQ, sg * CS, true); }
          for (const [side, sg] of [["front", 1], ["back", -1]]) if (!(e.st || []).includes(side)) bench(-CS, CS, sg * CQ, false);
          for (const [side, sg] of [["right", 1], ["left", -1]]) if (!(e.st || []).includes(side)) bench(-CQ, CQ, sg * CS, true);
        } else { B.set(lac, g); for (const [s, q] of [[-CS, -CQ], [CS, -CQ], [CS, CQ], [-CS, CQ]]) K.box(s - 0.2, s + 0.2, q - 0.2, q + 0.2, plTop, top); }
      } else {
        // a polygonal pavilion: columns on the polygon
        const R = Math.min(CS, CQ) / Math.cos(Math.PI / sides), pts = [];
        for (let k = 0; k < sides; k++) { const t = Math.PI / 2 + (k + 0.5) * (2 * Math.PI / sides); pts.push([R * Math.cos(t), R * Math.sin(t)]); }
        B.set(lac, g);
        const r = near ? e.dia / 2 : 0.2;
        for (const [s, q] of pts) K.box(s - r, s + r, q - r, q + r, plTop, top);
        if (near) {
          for (let k = 0; k < sides; k++) {
            const a = pts[k], c = pts[(k + 1) % sides];
            B.set(KIT_COLOURS.band, fg);
            B.quad(at(a[0], eave, a[1]), at(c[0], eave, c[1]), at(c[0], top, c[1]), at(a[0], top, a[1]));
            B.set(lac, fg);
            B.quad(at(a[0], top, a[1]), at(c[0], top, c[1]), at(c[0], top - 0.3, c[1]), at(a[0], top - 0.3, a[1]));
            if (k !== Math.floor(sides / 2) - 1 && k !== sides - 1) B.quad(at(a[0], plTop + 0.48, a[1]), at(c[0], plTop + 0.48, c[1]), at(c[0], plTop, c[1]), at(a[0], plTop, a[1]));
          }
        }
      }
      if (e.db) doubleRoof(); else roofOver(RS, RQ, tip, ridge, { form: form === "cj" ? "cj" : form, sides: e.sd || 4 });
    } else if (e.k === "pailou") {
      // a 牌楼: posts with stone clamps, two beams, a small roof over each bay, the middle one higher
      const n = e.b.length, top = eave;
      B.set(lac, g);
      const r = Math.min(0.28, CQ * 0.6);
      for (const s of xs) {
        K.box(s - r, s + r, -r, r, plTop, top + 0.3);
        if (near) { B.set(KIT_COLOURS.step, g); K.box(s - r - 0.25, s + r + 0.25, -r - 0.45, r + 0.45, plTop, plTop + 1.1); B.set(lac, g); }
      }
      if (near) {
        B.set(KIT_COLOURS.band, fg);
        K.box(-CS, CS, -0.18, 0.18, top - 1.4, top - 1.05);
        K.box(-CS, CS, -0.18, 0.18, top - 0.55, top - 0.2);
        B.set(KIT_COLOURS.bandRed, fg);
        const mid = Math.floor(n / 2);
        K.box(xs[mid] + 0.4, xs[mid + 1] - 0.4, -0.12, 0.12, top - 1.05, top - 0.55);
      }
      for (let i = 0; i < n; i++) {
        const lift = n > 1 && i === Math.floor(n / 2) ? Math.min(0.8, (ridge - top) * 0.35) : 0;
        const hx = (xs[i + 1] - xs[i]) / 2 + 0.3, cxs = (xs[i] + xs[i + 1]) / 2;
        const hz = Math.min(hd, 0.9);
        part = "roof";
        const P = (x, y, z) => at(cxs + x, y, z);
        roof(B, P, hx, hz, top + lift, Math.min(ridge, top + lift + 1.2 * hz + 0.3), Object.assign({}, roofOpts, { form: "wd", rolled: false, steps: 2 }));
        part = "body";
      }
    } else if (e.k === "tower" && p.tiers_m) {
      let y = plTop, s = CS, q = CQ;
      p.tiers_m.forEach((tier, i) => {
        const yTop = base + tier, last = i === p.tiers_m.length - 1;
        const xsT = xs.map((x) => (x * s) / CS), qsT = [q, -q];
        body(s, q, 0, 0, 0, y, yTop, i === 0, xsT, qsT);
        if (last) roofOver(s + o, q + o, yTop - o * 0.5, ridge, { form: form === "cj" ? "cj" : form });
        else {
          const ns = s * 0.86, nq = q * 0.86;
          skirt(s + o, q + o, ns, nq, yTop - o * 0.5, yTop + 0.9);
          if (near) balcony(ns + 0.4, nq + 0.4, yTop + 0.9);
          y = yTop + 0.9; s = ns; q = nq;
        }
      });
    } else if (p.mid_eave_m) {
      const mid = base + p.mid_eave_m;
      body(CS, CQ, e.pf, e.pb, e.ps, plTop, mid, true, xs, qs);
      skirt(CS + o * 0.8, CQ + o * 0.8, CS - 0.1, CQ - 0.1, mid - o * 0.4, mid + 0.5);
      if (near) balcony(CS - 0.05, CQ - 0.05, mid + 0.5);
      body(CS - 0.1, CQ - 0.1, 0, 0, 0, mid + 0.5, eave, false, xs.map((x) => (x * (CS - 0.1)) / CS), [CQ - 0.1, -(CQ - 0.1)]);
      roofOver(RS, RQ, tip, ridge, { form });
    } else if (e.db) {
      body(CS, CQ, e.pf, e.pb, e.ps, plTop, eave, true, xs, qs);
      doubleRoof();
    } else if (p.rolls > 1) {
      body(CS, CQ, e.pf, e.pb, e.ps, plTop, eave, true, xs, qs);
      const n = p.rolls, w = (2 * RQ) / n;
      for (let i = 0; i < n; i++) {
        const q0 = -RQ + i * w, q1 = q0 + w, mid = (q0 + q1) / 2;
        part = "roof";
        const P = (x, y, z) => at(x, y, mid + z);
        roof(B, P, RS, w / 2, tip, ridge, Object.assign({}, roofOpts, { form: form === "wd" || form === "cj" ? "xs" : form, gableX: form === "xu" ? RS - Math.min(0.6, o * 0.5) : RS }));
        part = "body";
      }
    } else {
      body(CS, CQ, e.k === "gate" ? 0 : e.pf, e.k === "gate" ? 0 : e.pb, e.k === "gate" ? 0 : e.ps, plTop, eave, true, xs, qs);
      roofOver(RS, RQ, tip, ridge, { form, sides: e.sd || 4 });
    }

    // a skirt roof 腰檐 from the outer rectangle at y0 up to the inner one at y1, with corner lift
    function skirt(os, oq, is, iq, y0, y1) {
      part = "roof";
      B.set(tileC, fg, true);
      const n0 = [[-os, oq], [os, oq], [os, -oq], [-os, -oq]], n1 = [[-is, iq], [is, iq], [is, -iq], [-is, -iq]];
      const lift = near ? Math.min(0.35, 0.03 * (os + oq)) : 0;
      for (let k = 0; k < 4; k++) {
        const a0 = n0[k], b0 = n0[(k + 1) % 4], a1 = n1[k], b1 = n1[(k + 1) % 4];
        if (e.te) B.set(tileHex(e.te), fg, true); else B.set(tileC, fg, true);
        B.quad(at(a0[0], y0 + lift, a0[1]), at(b0[0], y0 + lift, b0[1]), at(b1[0], y1, b1[1]), at(a1[0], y1, a1[1]));
        if (near) { B.set(KIT_COLOURS.underside, fg, true); B.quad(at(a0[0], y0 + lift, a0[1]), at(b0[0], y0 + lift, b0[1]), at(b0[0], y0 - 0.2, b0[1]), at(a0[0], y0 - 0.2, a0[1])); }
      }
      part = "body";
    }
    function balcony(hs, hq, y) {
      B.set(lac, fg);
      K.ring(hs, hq, 0.08, y + 0.85, y + 0.95);
      K.ring(hs, hq, 0.06, y, y + 0.12);
      for (const [s0, q0, s1, q1] of [[-hs, hq, hs, hq], [-hs, -hq, hs, -hq], [-hs, -hq, -hs, hq], [hs, -hq, hs, hq]]) {
        const L = Math.hypot(s1 - s0, q1 - q0), n = Math.max(1, Math.round(L / 1.5));
        for (let k = 0; k <= n; k++) { const s = s0 + ((s1 - s0) * k) / n, q = q0 + ((q1 - q0) * k) / n; K.box(s - 0.06, s + 0.06, q - 0.06, q + 0.06, y, y + 0.95); }
      }
    }
    // 重檐: the lower skirt over the porch, a short upper wall set in, the main roof
    function doubleRoof() {
      const inS = CS * 0.74, inQ = CQ * 0.74, yUp = eave + (ridge - eave) * 0.3;
      skirt(RS, RQ, inS, inQ, tip, eave + 0.8);
      B.set(e.k === "pavilion" ? lac : wallC, g);
      K.box(-inS, inS, -inQ, inQ, eave + 0.2, yUp - 0.3);
      if (near) bands(inS, inQ, yUp);
      const lip = o * 0.75;
      roofOver(inS + lip, inQ + lip, yUp - lip * 0.5, ridge, { form: form === "cj" ? "cj" : form, sides: e.sd || 4 });
    }
    return stepsOut;
  }

  // ---- the galleries of Round 9 that no box holds: posts, bench, fascia and a rolled 悬山 roof per straight run ----
  function drawGallery(B, pts, width, near, grade) {
    const G = spec.gallery, half = Math.max(width, 1.6) / 2;
    for (let i = 0; i < pts.length - 1; i++) {
      const [ax, az] = pts[i], [bx, bz] = pts[i + 1], L = Math.hypot(bx - ax, bz - az);
      if (L < 0.8) continue;
      const ux = (bx - ax) / L, uz = (bz - az) / L, mx = (ax + bx) / 2, mz = (az + bz) / 2;
      const y0 = Math.max(groundAt(ax, az) ?? 0, groundAt(bx, bz) ?? 0, groundAt(mx, mz) ?? 0) + 0.07;
      const at = (s, y, q) => [mx + ux * s - uz * q, y, mz + uz * s + ux * q];
      const K = prims(B, at);
      const top = y0 + G.eave_m, hl = L / 2 + 0.05;
      if (near) {
        B.set(KIT_COLOURS.post, grade);
        const n = Math.max(1, Math.round(L / G.bay_m.central));
        for (let k = 0; k <= n; k++) { const s = -L / 2 + (L * k) / n; for (const q of [-half + 0.15, half - 0.15]) K.box(s - 0.11, s + 0.11, q - 0.11, q + 0.11, y0 - 0.3, top - 0.3); }
        B.set(KIT_COLOURS.band, grade);
        for (const q of [-half + 0.15, half - 0.15]) K.box(-hl, hl, q - 0.1, q + 0.1, top - 0.3, top);
        B.set(KIT_COLOURS.lacquer[0], grade);
        K.box(-hl, hl, half - 0.35, half - 0.05, y0, y0 + 0.45);
      }
      const P = (x, y, z) => at(x, y, z);
      roof(B, P, hl + 0.1, half + 0.55, top - 0.35, y0 + G.ridge_m, { form: "xu", rolled: true, prof: profile(spec.gallery.ju, 1), near, tile: "grey", gableHex: KIT_COLOURS.plaster, bargeHex: 0x4a2a20, ridgeHex: shade(tileHex("grey"), 0.8), grade, steps: 2, gableX: hl });
    }
  }

  // ---- build: the far level of every tile at once; the near level of a tile when the camera comes within reach of it (update), dropped again when the camera has gone far (MAX_NEAR) ----
  const reportOf = {};
  for (const b of halls.info) {
    const e = b.spec;
    if (!e || e.k === "shape" || e.src === "model") continue;
    (tileOf(b.cx, b.cz).boxes ||= []).push(b);
  }
  for (const f of paths.features) {
    const p = f.properties;
    if (!(p.kind === "gallery" || p.kind === "mountain_gallery") || p.in_box) continue;
    if ([p.from_at, p.to_at].some((at) => at && (spec.halls[at.split(":")[0]] || {}).src === "model")) continue; // Round 13: the model draws its own colonnades
    const pts = f.geometry.coordinates.map(toXZ);
    (tileOf(pts[0][0], pts[0][1]).galleries ||= []).push({ p, pts });
  }
  const group = new THREE.Group();
  const count = { near: 0, far: 0, gallery: 0 };
  let view = { kitOn: true, assumed: true, paths: true, conf: false };
  const showKey = (k) => ({ kA: view.assumed, kK: view.assumed, kS: true, gS: view.paths, gA: view.paths && view.assumed })[k];
  const drawTile = (T, level) => {
    const near = level === "near", bufs = {};
    for (const b of T.boxes || []) {
      const e = b.spec, key = b.props.assumed ? "kA" : e.a ? "kK" : "kS";
      const B = (bufs[key] ||= new HallBuffer(key)), start = B.count;
      const track = { body: 0, roof: 0, steps: 0 };
      const steps = (e.k === "stone" || e.k === "stoneshape") ? drawStoneKit({ B, b, e, near, track, prims, roof, pyramid, profile, tileHex, shade, groundAt, flight }) || [] : drawHall(B, b, e, near, track);
      b.ranges.push({ buf: B, start, count: B.count - start });
      const rep = (reportOf[b.id] ||= { rf: e.rf, k: e.k, tris: {} });
      rep.tris[level] = (B.count - start) / 3;
      if (near) { rep.out = track; rep.steps = steps; }
    }
    for (const { p, pts } of T.galleries || []) {
      const B = (bufs[p.assumed ? "gA" : "gS"] ||= new HallBuffer(p.assumed ? "gA" : "gS")), s0 = B.count;
      drawGallery(B, pts, p.width_m, near, p.assumed ? "C" : p.confidence);
      if (near) count.gallery += (B.count - s0) / 3;
    }
    const g = new THREE.Group();
    g.position.set(-T.cx, 0, -T.cz);
    const list = [];
    let tris = 0;
    for (const B of Object.values(bufs)) {
      if (!B.count) continue;
      tris += B.count / 3;
      const m = B.finish();
      m.visible = showKey(B.key);
      g.add(m);
      list.push(B);
    }
    count[level] += tris;
    T[level] = { group: g, buffers: list, tris };
    T.lod.addLevel(g, near ? 0 : NEAR);
    halls.addBuffers(list);
    return tris;
  };
  const dropNear = (T) => {
    const n = T.near;
    if (!n) return;
    for (const B of n.buffers) B.dispose();
    for (const b of T.boxes || []) b.ranges = b.ranges.filter((r) => !r.buf.dead);
    T.lod.removeLevel(0);
    T.far.group.visible = true;
    count.near -= n.tris;
    T.near = null;
  };
  for (const T of tiles.values()) {
    T.lod = new THREE.LOD();
    T.lod.position.set(T.cx, 0, T.cz);
    drawTile(T, "far");
    group.add(T.lod);
  }
  const MAX_NEAR = 48;
  const _cp = new THREE.Vector3();
  // Builds the near level of the tiles within reach, nearest first, at most `budget` at a time; true if more wait.
  const update = (camera, budget = 6) => {
    if (!view.kitOn) return false;
    camera.getWorldPosition(_cp);
    const want = [];
    for (const T of tiles.values()) {
      T.d = Math.hypot(_cp.x - T.cx, _cp.y, _cp.z - T.cz);
      if (!T.near && T.d < NEAR + 0.75 * TILE) want.push(T);
    }
    want.sort((a, b) => a.d - b.d);
    let built = 0;
    for (const T of want) { if (built >= budget) break; drawTile(T, "near"); built++; }
    const live = [...tiles.values()].filter((T) => T.near && T.d > NEAR * 1.6).sort((a, b) => b.d - a.d);
    const nLive = [...tiles.values()].filter((T) => T.near).length;
    for (const T of live.slice(0, Math.max(0, nLive - MAX_NEAR))) dropNear(T);
    if (built) halls.repaint();
    return want.length > built;
  };

  // the courts: generated/courts.bin (scripts/kit1860.py), split by tile so the view leaves out what it does not see
  const courtGroup = new THREE.Group();
  const loadCourts = (buf) => {
    const a = new Int16Array(buf), C = spec.courts, s = C.scale_xz_m, byTile = new Map();
    for (let i = 0; i < a.length; i += 9) {
      const k = Math.floor(a[i] * s / 400) * 7919 + Math.floor(a[i + 2] * s / 400);
      if (!byTile.has(k)) byTile.set(k, []);
      byTile.get(k).push(i);
    }
    const plainC = new THREE.Color(KIT_COLOURS.court), confC = new THREE.Color(HALL_COLOURS.conf.C);
    const meshes = [];
    for (const list of byTile.values()) {
      const pos = new Float32Array(list.length * 9), col = new Float32Array(list.length * 9);
      list.forEach((i, n) => { for (let k = 0; k < 3; k++) { pos[n * 9 + k * 3] = a[i + k * 3] * s; pos[n * 9 + k * 3 + 1] = a[i + k * 3 + 1] / 100; pos[n * 9 + k * 3 + 2] = a[i + k * 3 + 2] * s; } });
      for (let k = 0; k < col.length; k += 3) { col[k] = plainC.r; col[k + 1] = plainC.g; col[k + 2] = plainC.b; }
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      g.setAttribute("color", new THREE.BufferAttribute(col, 3));
      g.computeVertexNormals();
      const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ vertexColors: true, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 }));
      m.userData = { plain: col.slice(), conf: col.map((v, k) => [confC.r, confC.g, confC.b][k % 3] * 0.9 + v * 0.1) };
      meshes.push(m);
      courtGroup.add(m);
    }
    return meshes;
  };
  let courtMeshes = [];
  const courtsReady = fetch(spec.courts.file).then((r) => r.arrayBuffer()).then((buf) => { courtMeshes = loadCourts(buf); });
  group.add(courtGroup);

  const setView = ({ kitOn, assumed, paths: pathsOn, conf }) => {
    view = { kitOn, assumed, paths: pathsOn, conf };
    group.visible = kitOn;
    for (const T of tiles.values()) for (const L of [T.near, T.far]) if (L) for (const B of L.buffers) B.mesh.visible = showKey(B.key);
    courtGroup.visible = assumed;
    for (const m of courtMeshes) { m.geometry.attributes.color.array.set(conf ? m.userData.conf : m.userData.plain); m.geometry.attributes.color.needsUpdate = true; }
  };
  // For tools/check_kit.py: every tile's near level built once (and dropped again unless in reach), its figures read.
  const report = () => {
    let nearAll = 0;
    for (const T of tiles.values()) {
      const had = Boolean(T.near);
      if (!had) drawTile(T, "near");
      nearAll += T.near.tris;
      if (!had) dropNear(T);
    }
    halls.repaint();
    return { boxes: reportOf, tiles: tiles.size, near_triangles_all: nearAll, far_triangles: count.far, gallery_near_triangles: count.gallery, court_triangles: spec.courts.triangles, lod_m: NEAR, tile_m: TILE, max_near_tiles: MAX_NEAR };
  };
  return { group, setView, report, update, courtsReady, tiles };
}
