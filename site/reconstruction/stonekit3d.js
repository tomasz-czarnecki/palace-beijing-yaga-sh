// Round 11: the stone kit for the Xiyang Lou 西洋楼. Every European box of data/halls_1860.geojson drawn as simple Baroque geometry from data/kit_1860.json (scripts/kit1860.py, from research/xiyanglou/boxes.csv and the dossiers' dimensions.json):
// a rusticated ground storey, pilasters at the bays with capitals, arched openings, an entablature at each storey, a balustrade at the roof's foot, a pediment on the main fronts, curved double stairs where the plan or the ruin has them,
// fountain basins with a jet, the 13-tier fountain towers and the niche of 大水法 with its stepped cascade, and the glazed roofs of Chinese form in the colours the dossiers name (materials.csv; the rule there where none is named).
// It is a kit, not a model: 谐奇趣 XY01 gets its detailed pass next. Every part here is the kit's reading of the plates of the 1780s: C. Classic script, loaded before kit3d.js; defines drawStoneKit, called by buildKit.
const STONE_COLOURS = {
  marble: 0xebe7dd, brick: 0x9c968d, rustic: 0xcfc8ba, rusticDark: 0xb3ab9c, pane: 0x2e3a40, water: 0x6f9fb0, jet: 0xd8ecf2, hedge: 0x3f5a35, bamboo: 0x98a35c, painted: 0xd9c49a, niche: 0x8e8778,
};

function drawStoneKit({ B, b, e, near, track, prims, roof, pyramid, profile, tileHex, shade, groundAt, flight }) {
  const p = b.props, hf = b.hf, hd = b.hd, g = p.confidence, fg = "C";
  let part = "body";
  const at = (s, y, q, probe) => {
    const ex = probe ? 0 : Math.max(Math.abs(s) - hf, Math.abs(q) - hd, 0);
    if (ex > track[part]) track[part] = ex;
    return [b.cx + b.u[0] * s + b.a[0] * q, y, b.cz + b.u[1] * s + b.a[1] * q];
  };
  const K = prims(B, at);
  const base = b.base, foot = b.foot, plTop = base + p.platform_m, eave = base + p.eave_m, ridge = base + p.ridge_m;
  const shape = p.shape, k2 = e.k2;
  const steps = [];
  const marble = (gr = g) => B.set(STONE_COLOURS.marble, gr);
  // straight flights where the ways of Round 9 reach the box (kit3d.js flight()); the run kept within 1.5 m
  const waySteps = (yTop) => {
    part = "steps";
    for (const side of e.st || []) for (const off of (e.so || {})[side] || [0]) {
      const fl = flight(B, K, at, side, off, hf, hd, yTop, 1.5, 3.0, fg, near, base);
      if (fl) steps.push(fl);
    }
    part = "body";
  };

  // an arch-headed opening on a façade plane: dark pane recessed, a marble surround; (a0, a1) along the plane, y0..y1 to the arch's springing, the half circle above
  const archOpening = (a0, a1, y0, y1, plane, sgn, onS) => {
    const w = a1 - a0, r = w / 2, mid = (a0 + a1) / 2;
    const P = (a, y, d) => (onS ? at(plane - sgn * d, y, a) : at(a, y, plane - sgn * d));
    B.set(STONE_COLOURS.pane, fg);
    B.quad(P(a0, y1, 0.14), P(a0, y0, 0.14), P(a1, y0, 0.14), P(a1, y1, 0.14));
    const n = near ? 6 : 2;
    for (let k = 0; k < n; k++) {
      const t0 = Math.PI * k / n, t1 = Math.PI * (k + 1) / n;
      B.tri(P(mid, y1, 0.14), P(mid + r * Math.cos(t0), y1 + r * Math.sin(t0), 0.14), P(mid + r * Math.cos(t1), y1 + r * Math.sin(t1), 0.14));
    }
    if (!near) return;
    marble(fg);
    // jambs and the arch's ring, standing a little proud
    const box = (s0, s1, yy0, yy1, d0, d1) => { const f0 = plane - sgn * d0, f1 = plane - sgn * d1; if (onS) K.box(Math.min(f0, f1), Math.max(f0, f1), s0, s1, yy0, yy1); else K.box(s0, s1, Math.min(f0, f1), Math.max(f0, f1), yy0, yy1); };
    box(a0 - 0.14, a0, y0, y1, -0.08, 0.14);
    box(a1, a1 + 0.14, y0, y1, -0.08, 0.14);
    box(a0 - 0.14, a1 + 0.14, y0 - 0.12, y0, -0.1, 0.14);
    for (let k = 0; k < n; k++) {
      const t0 = Math.PI * k / n, t1 = Math.PI * (k + 1) / n;
      const o = (t, rr) => [mid + rr * Math.cos(t), y1 + rr * Math.sin(t)];
      const [x0, z0] = o(t0, r), [x1, z1] = o(t1, r), [x2, z2] = o(t1, r + 0.16), [x3, z3] = o(t0, r + 0.16);
      B.quad(P(x0, z0, -0.08), P(x1, z1, -0.08), P(x2, z2, -0.08), P(x3, z3, -0.08));
    }
    // the keystone
    box(mid - 0.12, mid + 0.12, y1 + r - 0.05, y1 + r + 0.3, -0.12, 0.1);
    // glazing bars
    B.set(shade(STONE_COLOURS.marble, 0.85), fg);
    box(mid - 0.03, mid + 0.03, y0, y1 + r * 0.9, 0.02, 0.13);
    box(a0, a1, (y0 + y1) / 2 - 0.03, (y0 + y1) / 2 + 0.03, 0.02, 0.13);
  };

  // one façade: pilasters at the bays, arched openings per storey, entablature bands; the plane at q = plane (or s = plane with onS), a0..a1 along it
  const facade = (a0, a1, plane, sgn, onS, nb, yb, storeys, hS, doorMid) => {
    const w = (a1 - a0) / nb;
    for (let st = 0; st < storeys; st++) {
      const y0 = yb + st * hS, y1 = y0 + hS - 0.9;
      for (let i = 0; i < nb; i++) {
        const s0 = a0 + i * w, s1 = s0 + w, m = (s0 + s1) / 2, ow = Math.min(w * 0.5, 2.6);
        const tall = st === 0 && doorMid && i === Math.floor(nb / 2);
        const yo0 = y0 + (tall ? 0.1 : Math.min(1.0, hS * 0.18)), r = ow / 2, yo1 = Math.max(yo0 + 0.8, y1 - r - 0.35);
        if (yo1 > yo0 + 0.5) archOpening(m - ow / 2, m + ow / 2, yo0, yo1, plane, sgn, onS);
      }
      if (!near) continue;
      // pilasters with base and capital
      marble(fg);
      for (let i = 0; i <= nb; i++) {
        const s = a0 + i * w, pw = 0.28;
        const bx = (s0, s1, yy0, yy1, d0, d1) => { const f0 = plane + sgn * d0, f1 = plane + sgn * d1; if (onS) K.box(Math.min(f0, f1), Math.max(f0, f1), s0, s1, yy0, yy1); else K.box(s0, s1, Math.min(f0, f1), Math.max(f0, f1), yy0, yy1); };
        bx(s - pw, s + pw, y0, y0 + hS - 0.9, -0.02, 0.16);
        bx(s - pw - 0.08, s + pw + 0.08, y0, y0 + 0.4, -0.02, 0.22);
        bx(s - pw - 0.12, s + pw + 0.12, y0 + hS - 1.25, y0 + hS - 0.9, -0.02, 0.26);
      }
      // the entablature: architrave, frieze, cornice
      const bx = (yy0, yy1, d) => { const f0 = plane - sgn * 0.02, f1 = plane + sgn * d; if (onS) K.box(Math.min(f0, f1), Math.max(f0, f1), a0 - d, a1 + d, yy0, yy1); else K.box(a0 - d, a1 + d, Math.min(f0, f1), Math.max(f0, f1), yy0, yy1); };
      const yt = y0 + hS;
      bx(yt - 0.9, yt - 0.6, 0.22);
      B.set(shade(STONE_COLOURS.marble, 0.93), fg);
      bx(yt - 0.6, yt - 0.3, 0.16);
      marble(fg);
      bx(yt - 0.3, yt, st === storeys - 1 ? 0.45 : 0.3);
    }
  };

  // ---- shapes ----
  if (shape === "pool" || shape === "basin") {
    const rim = 0.6, h = base + p.eave_m, r = Math.min(hf, hd);
    marble(g);
    if (shape === "basin") {
      const n = near ? 16 : 8, pts = [];
      for (let k = 0; k < n; k++) { const t = (2 * Math.PI * k) / n; pts.push([r * Math.cos(t), r * Math.sin(t)]); }
      for (let k = 0; k < n; k++) { const a = pts[k], c = pts[(k + 1) % n]; B.quad(at(a[0], h, a[1]), at(a[0], foot, a[1]), at(c[0], foot, c[1]), at(c[0], h, c[1])); B.quad(at(a[0], h, a[1]), at(c[0], h, c[1]), at(c[0] * 0.9, h, c[1] * 0.9), at(a[0] * 0.9, h, a[1] * 0.9)); }
      B.set(STONE_COLOURS.water, g);
      for (let k = 0; k < n; k++) { const a = pts[k], c = pts[(k + 1) % n]; B.tri(at(0, h - 0.12, 0), at(a[0] * 0.9, h - 0.12, a[1] * 0.9), at(c[0] * 0.9, h - 0.12, c[1] * 0.9)); }
    } else {
      for (const [cs, cq, hs, hq] of [[0, hd - rim / 2, hf, rim / 2], [0, -hd + rim / 2, hf, rim / 2], [hf - rim / 2, 0, rim / 2, hd], [-hf + rim / 2, 0, rim / 2, hd]]) K.box(cs - hs, cs + hs, cq - hq, cq + hq, foot, h);
      B.set(STONE_COLOURS.water, g);
      B.quad(at(-hf + rim, h - 0.12, hd - rim), at(hf - rim, h - 0.12, hd - rim), at(hf - rim, h - 0.12, -hd + rim), at(-hf + rim, h - 0.12, -hd + rim));
    }
    if (e.jet && near) {
      // a pedestal and a jet: 'jets about 6 chi' at 大水法 (S06 through params.json xiyang_lou XY10); the form is the kit's
      marble(fg);
      K.box(-0.6, 0.6, -0.6, 0.6, h - 0.2, h + 0.9);
      B.set(STONE_COLOURS.jet, fg);
      const top = at(0, h + 0.9 + 2.0, 0);
      const ring = [[0.25, 0], [0, 0.25], [-0.25, 0], [0, -0.25]].map(([x, z]) => at(x, h + 0.9, z));
      for (let k = 0; k < 4; k++) B.tri(ring[k], ring[(k + 1) % 4], top);
    }
    return steps;
  }
  if (shape === "terrace") {
    // a terrace: rusticated face, a marble coping and a balustrade round its top; with curved stairs, these take the front of the box (the plan draws them in it) and the terrace stands behind them
    const D = e.stair ? Math.min(0.3 * 2 * hd, 7) : 0, qT = hd - D, hq = (qT + hd) / 2, qc0 = (qT - hd) / 2;
    B.set(STONE_COLOURS.rustic, g);
    K.box(-hf, hf, -hd, qT, foot, eave);
    if (near) {
      B.set(STONE_COLOURS.rusticDark, fg);
      for (let y = base + 0.45; y < eave - 0.3; y += 0.6) { K.box(-hf - 0.02, hf + 0.02, qT, qT + 0.03, y, y + 0.08); K.box(-hf - 0.02, hf + 0.02, -hd - 0.03, -hd, y, y + 0.08); }
      marble(fg);
      K.box(-hf, hf, qT - 0.4, qT + 0.06, eave - 0.2, eave);
      balustrade(hf - 0.2, (qT + hd) / 2 - 0.2, eave, qc0);
    }
    if (e.stair) steps.push(...curvedStairs(0, qT, eave, D, 1));
    else waySteps(eave);
    return steps;
  }
  if (shape === "court") {
    B.set(HALL_COLOURS.court, g);
    K.box(-hf, hf, -hd, hd, foot, base + p.eave_m);
    return steps;
  }
  if (shape === "wall") {
    const top = eave;
    if (k2 === "hedgewall") {
      // the maze: brick walls about shoulder high topped with little trimmed pines (S02 p.145); the pines as a dark green strip
      B.set(STONE_COLOURS.brick, g); K.box(-hf, hf, -hd, hd, foot, top);
      if (near) { B.set(STONE_COLOURS.hedge, fg); K.box(-hf, hf, -hd * 0.7, hd * 0.7, top, top + 0.45); }
      return steps;
    }
    B.set(k2 === "niche" ? STONE_COLOURS.rustic : STONE_COLOURS.marble, g);
    K.box(-hf, hf, -hd, hd, foot, top);
    if (!near) return steps;
    if (k2 === "niche") {
      // the niche of 大水法: a great arch recessed in the front, pilasters either side, a crest; the cascade steps down inside it
      const w = Math.min(hf * 0.55, 6.5), yS = plTop + (top - plTop) * 0.45;
      B.set(STONE_COLOURS.niche, fg);
      B.quad(at(-w, yS, hd + 0.01), at(-w, plTop, hd + 0.01), at(w, plTop, hd + 0.01), at(w, yS, hd + 0.01));
      for (let k = 0; k < 8; k++) { const t0 = Math.PI * k / 8, t1 = Math.PI * (k + 1) / 8; B.tri(at(0, yS, hd + 0.01), at(w * Math.cos(t0), yS + w * Math.sin(t0), hd + 0.01), at(w * Math.cos(t1), yS + w * Math.sin(t1), hd + 0.01)); }
      marble(fg);
      for (const s of [-w - 0.6, w + 0.6, -hf + 0.6, hf - 0.6]) K.box(s - 0.35, s + 0.35, hd - 0.1, hd + 0.15, plTop, top - 0.6);
      K.box(-hf, hf, hd - 0.2, hd + 0.2, top - 0.6, top);
      const crest = at(0, top + 1.8, hd);
      B.tri(at(-w - 1, top, hd), at(w + 1, top, hd), crest);
      if (e.cascade) {
        B.set(STONE_COLOURS.water, fg);
        const n = 7, d = Math.min(2 * hd - 0.4, 3.6);
        for (let k = 0; k < n; k++) {
          const yy = yS - ((yS - plTop) * (k + 1)) / (n + 1), q0 = hd - d + (d * k) / n;
          K.box(-w * 0.6, w * 0.6, q0, q0 + d / n, yy - 0.15, yy);
        }
      }
    } else if (k2 === "screen" || k2 === "gatewall") {
      // screens: framed panels, painted 线法画 or marble trophies; a triple gate: three arches through
      if (k2 === "gatewall") {
        for (const s of [-hf * 0.6, 0, hf * 0.6]) archOpening(s - 1.2, s + 1.2, plTop, plTop + (top - plTop) * 0.5, hd, 1, false);
      } else {
        const n = /five/.test(p.part || "") ? 5 : Math.max(1, Math.round(hf / 2.5));
        const w = (2 * hf) / n;
        for (let i = 0; i < n; i++) {
          const s0 = -hf + i * w + 0.35, s1 = s0 + w - 0.7;
          B.set(/painted/.test(p.part || "") || /far wall/.test(p.part || "") ? STONE_COLOURS.painted : shade(STONE_COLOURS.marble, 0.95), fg);
          for (const sg of [1, -1]) B.quad(at(s0, top - 0.8, sg * (hd + 0.02)), at(s0, plTop + 0.6, sg * (hd + 0.02)), at(s1, plTop + 0.6, sg * (hd + 0.02)), at(s1, top - 0.8, sg * (hd + 0.02)));
        }
        marble(fg);
        K.box(-hf - 0.1, hf + 0.1, -hd - 0.1, hd + 0.1, top - 0.35, top);
      }
    }
    return steps;
  }
  if (shape === "octagon") {
    const r = Math.min(hf, hd);
    if (p.ridge_m <= p.eave_m + 0.01) {
      // a stepped round base: three rings
      marble(g);
      for (let k = 0; k < 3; k++) { const rr = r * (1 - k * 0.12), yy = foot + ((eave - foot) * (k + 1)) / 3; octPrism(rr, foot, yy); }
      return steps;
    }
    marble(g);
    octPrism(r, foot, plTop);
    waySteps(plTop);
    const rb = r - 0.5, sto = Math.max(1, e.sto || 1), hS = (eave - plTop) / sto;
    B.set(e.bamboo ? STONE_COLOURS.bamboo : STONE_COLOURS.brick, g);
    octPrism(rb, plTop, eave);
    if (near) {
      const pts = octPts(rb);
      for (let k = 0; k < 8; k++) {
        const a = pts[k], c = pts[(k + 1) % 8], mx = (a[0] + c[0]) / 2, mz = (a[1] + c[1]) / 2, L = Math.hypot(c[0] - a[0], c[1] - a[1]);
        const nx = mx / Math.hypot(mx, mz), nz = mz / Math.hypot(mx, mz);
        for (let st = 0; st < sto; st++) {
          const y0 = plTop + st * hS + 0.5, y1 = plTop + (st + 1) * hS - 0.9 - L * 0.22;
          if (y1 - y0 < 0.6) continue;
          const w = L * 0.22, P = (t, y) => at(mx + nx * 0.03 + (c[0] - a[0]) / L * t, y, mz + nz * 0.03 + (c[1] - a[1]) / L * t);
          B.set(STONE_COLOURS.pane, fg);
          B.quad(P(-w, y1), P(-w, y0), P(w, y0), P(w, y1));
          for (let j = 0; j < 4; j++) { const t0 = Math.PI * j / 4, t1 = Math.PI * (j + 1) / 4; B.tri(P(0, y1), P(w * Math.cos(t0), y1 + w * Math.sin(t0)), P(w * Math.cos(t1), y1 + w * Math.sin(t1))); }
        }
        marble(fg);
        K.box(a[0] - 0.25, a[0] + 0.25, a[1] - 0.25, a[1] + 0.25, plTop, eave);
      }
      for (let st = 1; st <= sto; st++) { const yy = plTop + st * hS; marble(fg); octPrism(rb + 0.3, yy - 0.5, yy); }
    }
    part = "roof";
    const opts = { sides: 8, prof: profile([0.5, 0.7, 0.9], 1), near, tile: e.t, edge: e.te, grade: fg, liftK: 0.3 };
    if (e.db) { skirtOct(rb + 0.9, rb * 0.7, eave - 0.3, eave + 0.8); pyramid(B, at, rb * 0.7 + 0.6, rb * 0.7 + 0.6, eave + (ridge - eave) * 0.35, ridge, opts); }
    else pyramid(B, at, rb + 0.8, rb + 0.8, eave - 0.3, ridge, opts);
    return steps;
  }

  // ---- the 13-tier fountain towers of 大水法 ----
  if (k2 === "obelisk") {
    marble(g);
    K.box(-hf, hf, -hd, hd, foot, eave);
    const n = e.tiers || 13, h = (ridge - eave) / (n + 1);
    for (let k = 0; k < n; k++) {
      const f = 1 - (0.75 * (k + 1)) / n, y0 = eave + k * h;
      K.box(-hf * f, hf * f, -hd * f, hd * f, y0, y0 + h * (near ? 0.82 : 1));
      if (near) { B.set(STONE_COLOURS.water, fg); K.box(-hf * f - 0.05, hf * f + 0.05, -hd * f - 0.05, hd * f + 0.05, y0 + h * 0.82, y0 + h); marble(g); }
    }
    K.box(-0.15, 0.15, -0.15, 0.15, ridge - h, ridge);
    return steps;
  }

  // ---- a palace block, a gate, an arcade, a pavilion ----
  const sto = Math.max(1, e.sto || 1);
  const stairD = e.stair ? Math.min(2 * hd * 0.3, 6) : 0;
  const qF = hd - stairD - 0.3, qB = -hd + 0.3, sF = hf - 0.3;
  const hS = (eave - plTop) / sto;
  marble(g);
  K.box(-hf, hf, -hd, hd, foot, plTop);
  // the walls: grey brick (S02 on two buildings; materials.csv rule), the ground storey rusticated
  B.set(e.bamboo ? STONE_COLOURS.bamboo : STONE_COLOURS.brick, g);
  K.box(-sF, sF, qB, qF, plTop, eave);
  if (k2 === "arcade") {
    // a corridor: piers and arches on both long sides
    const nb = Math.max(2, Math.round((2 * sF) / 3.4));
    for (const [pl, sg] of [[qF, 1], [qB, -1]]) facade(-sF, sF, pl, sg, false, nb, plTop, 1, eave - plTop, false);
  } else {
    if (near) {
      B.set(STONE_COLOURS.rustic, fg);
      const yR = plTop + Math.min(hS, 4.5);
      K.box(-sF - 0.06, sF + 0.06, qB - 0.06, qF + 0.06, plTop, yR);
      B.set(STONE_COLOURS.rusticDark, fg);
      for (let y = plTop + 0.5; y < yR - 0.2; y += 0.5) {
        K.box(-sF - 0.08, sF + 0.08, qF + 0.03, qF + 0.08, y, y + 0.07);
        K.box(-sF - 0.08, sF + 0.08, qB - 0.08, qB - 0.03, y, y + 0.07);
        K.box(sF + 0.03, sF + 0.08, qB, qF, y, y + 0.07);
        K.box(-sF - 0.08, -sF - 0.03, qB, qF, y, y + 0.07);
      }
    }
    const nb = e.nb || 3, ns = e.ns || 1;
    facade(-sF, sF, qF, 1, false, nb, plTop, sto, hS, true);
    facade(-sF, sF, qB, -1, false, nb, plTop, sto, hS, true);
    facade(qB, qF, sF, 1, true, ns, plTop, sto, hS, false);
    facade(qB, qF, -sF, -1, true, ns, plTop, sto, hS, false);
  }
  if (near) balustrade(sF, (qF - qB) / 2, eave, (qF + qB) / 2);
  // the pediment over the middle bays of the front
  if (e.ped && near) {
    marble(fg);
    const w = Math.min(sF * 0.45, 7), h = Math.min(2.4, w * 0.4);
    for (const d of [0, -0.4]) B.tri(at(-w, eave, qF + 0.3 + d), at(w, eave, qF + 0.3 + d), at(0, eave + h, qF + 0.3 + d));
    B.quad(at(-w, eave, qF + 0.3), at(0, eave + h, qF + 0.3), at(0, eave + h, qF - 0.1), at(-w, eave, qF - 0.1));
    B.quad(at(w, eave, qF - 0.1), at(0, eave + h, qF - 0.1), at(0, eave + h, qF + 0.3), at(w, eave, qF + 0.3));
  }
  // the roof: glazed tile of Chinese form over the cornice, behind the balustrade
  part = "roof";
  const rs = sF + 0.5, rq = (qF - qB) / 2 + 0.5, qc = (qF + qB) / 2;
  const along = rs >= rq;
  const P = (x, y, z) => (along ? at(x, y, qc + z) : at(z, y, qc - x));
  const opts = { form: e.rf === "cj" ? "cj" : e.rf || "wd", rolled: false, prof: profile([0.5, 0.65, 0.85], 1), liftK: 0.25, near, tile: e.t, edge: e.te, gableHex: STONE_COLOURS.marble, bargeHex: STONE_COLOURS.marble, ridgeHex: shade(tileHex(e.t), 0.8), grade: fg, steps: 3, sides: 4 };
  const y0 = eave + 0.25;
  if (e.db) {
    const yUp = y0 + (ridge - y0) * 0.35;
    B.set(tileHex(e.te || e.t), fg, true);
    const n0 = [[-rs, rq], [rs, rq], [rs, -rq], [-rs, -rq]], f = 0.7;
    for (let k = 0; k < 4; k++) { const a0 = n0[k], b0 = n0[(k + 1) % 4]; B.quad(at(a0[0], y0, qc + a0[1]), at(b0[0], y0, qc + b0[1]), at(b0[0] * f, yUp, qc + b0[1] * f), at(a0[0] * f, yUp, qc + a0[1] * f)); }
    B.set(STONE_COLOURS.brick, g);
    K.box(-rs * 0.62, rs * 0.62, qc - rq * 0.62, qc + rq * 0.62, yUp - 0.6, yUp + 1.0);
    const P2 = (x, y, z) => (along ? at(x * 0.72, y, qc + z * 0.72) : at(z * 0.72, y, qc - x * 0.72));
    if (opts.form === "cj") pyramid(B, (s, y, q) => at(s, y, qc + q), rs * 0.72, rq * 0.72, yUp + 0.7, ridge, opts);
    else roof(B, P2, along ? rs : rq, along ? rq : rs, yUp + 0.7, ridge, opts);
  } else if (opts.form === "cj") pyramid(B, (s, y, q) => at(s, y, qc + q), rs, rq, y0, ridge, opts);
  else roof(B, P, along ? rs : rq, along ? rq : rs, y0, ridge, opts);
  part = "body";
  if (e.stair) steps.push(...curvedStairs(0, qF, plTop + Math.min(hS * 0.5, 3.2), hd - qF, 1));
  waySteps(plTop);
  return steps;

  // ---- helpers (hoisted) ----
  function octPts(r) { const out = []; for (let k = 0; k < 8; k++) { const t = ((k + 0.5) * 2 * Math.PI) / 8; out.push([r * Math.cos(t), r * Math.sin(t)]); } return out; }
  function octPrism(r, y0, y1) {
    const pts = octPts(r);
    for (let k = 0; k < 8; k++) { const a = pts[k], c = pts[(k + 1) % 8]; B.quad(at(a[0], y1, a[1]), at(a[0], y0, a[1]), at(c[0], y0, c[1]), at(c[0], y1, c[1])); B.tri(at(0, y1, 0), at(a[0], y1, a[1]), at(c[0], y1, c[1])); }
  }
  function skirtOct(r0, r1, y0, y1) {
    B.set(tileHex(e.te || e.t), fg, true);
    const a = octPts(r0), c = octPts(r1);
    for (let k = 0; k < 8; k++) B.quad(at(a[k][0], y0, a[k][1]), at(a[(k + 1) % 8][0], y0, a[(k + 1) % 8][1]), at(c[(k + 1) % 8][0], y1, c[(k + 1) % 8][1]), at(c[k][0], y1, c[k][1]));
  }
  function balustrade(hs, hq, y, qc0 = 0) {
    marble(fg);
    const hb = 0.9;
    K.box(-hs, hs, qc0 + hq - 0.25, qc0 + hq, y, y + 0.15);
    K.box(-hs, hs, qc0 - hq, qc0 - hq + 0.25, y, y + 0.15);
    K.box(-hs, hs, qc0 + hq - 0.22, qc0 + hq, y + hb - 0.12, y + hb);
    K.box(-hs, hs, qc0 - hq, qc0 - hq + 0.22, y + hb - 0.12, y + hb);
    K.box(hs - 0.22, hs, qc0 - hq, qc0 + hq, y + hb - 0.12, y + hb);
    K.box(-hs, -hs + 0.22, qc0 - hq, qc0 + hq, y + hb - 0.12, y + hb);
    for (const [s0, q0, s1, q1] of [[-hs, hq, hs, hq], [-hs, -hq, hs, -hq], [-hs, -hq, -hs, hq], [hs, -hq, hs, hq]]) {
      const L = Math.hypot(s1 - s0, q1 - q0), n = Math.max(1, Math.round(L / 0.55));
      for (let k = 0; k <= n; k++) { const s = s0 + ((s1 - s0) * k) / n, q = qc0 + q0 + ((q1 - q0) * k) / n; K.box(s - 0.07, s + 0.07, q - 0.07, q + 0.07, y, y + hb); }
    }
  }
  // two quarter-circle flights from a landing at the middle of a front, down to the ground on either side, with marble rails
  // avail: the depth of the box in front of the face; the flights' radius is chosen to fit it
  function curvedStairs(s0, qFace, yLand, avail, sgn) {
    const out = [];
    part = "steps";
    const R = Math.max(1.2, (avail - 1.75) / 0.9);
    const land = at(s0, 0, qFace + sgn * Math.min(R, avail), true), yG = groundAt ? (groundAt(land[0], land[2]) ?? base) : base;
    const h = yLand - yG;
    if (h < 0.3) { part = "body"; return out; }
    const n = Math.max(4, Math.round(h / 0.16)), rise = h / n;
    marble(fg);
    K.box(s0 - 1.6, s0 + 1.6, qFace, qFace + 1.6, yG - 0.1, yLand);
    for (const side of [-1, 1]) {
      // each flight runs down to the ground at its own foot
      const tEnd = Math.PI / 2, fs = s0 + side * R * Math.sin(tEnd), fq = qFace + sgn * R * 0.9 + sgn * 0.8;
      const fw = at(fs, 0, fq, true), gF = groundAt ? (groundAt(fw[0], fw[2]) ?? yG) : yG, riseS = (yLand - gF) / n, low = Math.min(gF, yG);
      for (let k = 0; k < n; k++) {
        const t = (Math.PI / 2) * ((k + 0.5) / n), cs = s0 + side * R * Math.sin(t), cq = qFace + sgn * R * (1 - Math.cos(t)) * 0.9 + sgn * 0.8;
        const top = yLand - (k + 1) * riseS;
        K.box(cs - 0.9, cs + 0.9, cq - 0.9, cq + 0.9, low - 0.1, Math.max(top, gF));
        if (near && k % 2 === 0) { K.box(cs - 0.1, cs + 0.1, cq + 0.85, cq + 1.05, top, top + 0.95); }
      }
      out.push([side > 0 ? "right" : "left", +fw[0].toFixed(2), +fw[2].toFixed(2), +gF.toFixed(2), +yLand.toFixed(2), +R.toFixed(2), 1.8]);
    }
    part = "body";
    return out;
  }
}
