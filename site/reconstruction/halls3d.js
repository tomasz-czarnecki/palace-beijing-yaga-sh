// The boxes of the gardens: every feature of data/halls_1860.geojson (scripts/boxes1860.py) as a platform, a wall box and a simple roof, merged into a few meshes. Classic script, loaded before kit3d.js and 3d.js; defines HALL_COLOURS, HallBuffer and buildHalls.
// Each box keeps its ranges in the meshes and an oriented box for picking, so a click tests a few thousand rectangles, not every triangle. A selected box is recoloured in place, in the boxes and in the kit's meshes alike (Round 11: the kit adds its ranges to the same entries).
// Local frame: s along the frontage, q towards the front, y up. The feature's ring is front-left, front-right, back-right, back-left.
// Round 11: the plain boxes sit in groups by what is assumed: pA the box itself (no block on the plan), pK a box on the plan whose kit form is the class's, pS a box whose kit form has a source, pX/pXA shapes the kit leaves as they are. setView() shows the boxes or the kit (kit3d.js) by the switches kit and assumed.
const HALL_COLOURS = {
  platform: 0xb9b2a3, wall: 0xc2a98a, wallAssumed: 0xe7e0d3, stone: 0xd8d3c4, europeanWall: 0xe2ddcf, underside: 0x6e685e, water: 0x6f9fb0, court: 0x9aa87a,
  // Colours chosen for the view: grey tile is the rule with named exceptions (typology section 5); the shades are not read from a source.
  tile: { grey: 0x5f6469, yellow: 0xd6a31c, blue: 0x3e6fa6, green: 0x3f8f6a, mixed: 0x3d8d92, black: 0x2b2d31, slate: 0x56626c, glazed: 0x4b86a3, stone: 0xbfb9aa, purple: 0x6a4763, ochre: 0xc9953a, red: 0xb4532f },
  conf: { A: 0x2f8f4e, B: 0xd9a441, C: 0xc4513a },
  selected: 0xffcf3a,
};

// A growing triangle soup with two colour sets: the view's colours and the confidence tint, a byte per channel. Ranges of it belong to boxes. No normals: the material shades flat from the screen's derivatives, which also keeps the memory down (Round 11).
class HallBuffer {
  constructor(key) { this.key = key; this.pos = []; this.col = []; this.cf = []; this.rgb = [255, 255, 255]; this.crgb = [255, 255, 255]; this._c = new THREE.Color(); }
  // hex: the view's colour; grade: A, B or C; dark: the confidence tint darker (roofs)
  set(hex, grade, dark) {
    const c = this._c;
    c.setHex(hex); this.rgb = [Math.round(c.r * 255), Math.round(c.g * 255), Math.round(c.b * 255)];
    c.setHex(HALL_COLOURS.conf[grade] ?? HALL_COLOURS.conf.C);
    const k = dark ? 0.55 : 1;
    this.crgb = [Math.round(c.r * k * 255), Math.round(c.g * k * 255), Math.round(c.b * k * 255)];
  }
  tri(a, b, d) {
    this.pos.push(a[0], a[1], a[2], b[0], b[1], b[2], d[0], d[1], d[2]);
    const [r, g, bl] = this.rgb, [cr, cg, cb] = this.crgb;
    this.col.push(r, g, bl, r, g, bl, r, g, bl);
    this.cf.push(cr, cg, cb, cr, cg, cb, cr, cg, cb);
  }
  quad(a, b, d, e) { this.tri(a, b, d); this.tri(a, d, e); }
  get count() { return this.pos ? this.pos.length / 3 : this.n; }
  finish() {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(this.pos), 3));
    this.n = this.pos.length / 3;
    this.plain = new Uint8Array(this.col);
    this.colours = this.plain.slice();
    this.conf = new Uint8Array(this.cf);
    g.setAttribute("color", new THREE.BufferAttribute(this.colours, 3, true));
    this.attr = g.getAttribute("color");
    this.pos = this.col = this.cf = null;
    this.mesh = new THREE.Mesh(g, HallBuffer.material || (HallBuffer.material = new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide, flatShading: true })));
    this.mesh.userData.group = this.key;
    return this.mesh;
  }
  dispose() { if (this.mesh) { this.mesh.geometry.dispose(); this.mesh.removeFromParent(); } this.plain = this.colours = this.conf = null; this.dead = true; }
}

function buildHalls({ fc, toXZ, datum, kit }) {
  const info = [], buffers = [];
  const groups = {};
  const buf = (key) => { if (!groups[key]) { groups[key] = new HallBuffer(key); buffers.push(groups[key]); } return groups[key]; };
  const KIT_SHAPES = new Set(["shape"]);

  for (const f of fc.features) {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(toXZ);
    const cx = (ring[0][0] + ring[2][0]) / 2, cz = (ring[0][1] + ring[2][1]) / 2;
    const uLen = Math.hypot(ring[1][0] - ring[0][0], ring[1][1] - ring[0][1]), aLen = Math.hypot(ring[1][0] - ring[2][0], ring[1][1] - ring[2][1]);
    const u = [(ring[1][0] - ring[0][0]) / uLen, (ring[1][1] - ring[0][1]) / uLen], a = [(ring[1][0] - ring[2][0]) / aLen, (ring[1][1] - ring[2][1]) / aLen];
    const hf = uLen / 2, hd = aLen / 2;
    const at = (s, y, q) => [cx + u[0] * s + a[0] * q, y, cz + u[1] * s + a[1] * q];
    const base = p.ground_m - datum + (p.stand || 0), foot = (p.stand ? p.ground_m - datum : p.foot_m - datum), top = base + p.ridge_m;
    const spec = kit && kit.halls[p.id];
    const byKit = Boolean(spec) && !KIT_SHAPES.has(spec.k) && spec.src !== "model";
    const key = !byKit ? (p.assumed ? "pXA" : "pX") : p.assumed ? "pA" : spec.a ? "pK" : "pS";
    const B = buf(key);
    const start = B.count;
    const minSide = Math.min(hf, hd) * 2;
    // Platform edge and eave overhang, close to params.json by class: 下出 about 0.08 of the depth, 上出 about 0.1.
    const edge = Math.min(Math.max(minSide * 0.08, 0.15), 1.25), over = Math.min(Math.max(minSide * 0.1, 0.25), 1.6);
    const wallHex = p.european ? HALL_COLOURS.europeanWall : p.assumed ? HALL_COLOURS.wallAssumed : HALL_COLOURS.wall;
    const tileHex = HALL_COLOURS.tile[p.tiles] ?? HALL_COLOURS.tile.grey;
    const entry = { id: p.id, bid: p.building_id, parent: p.parent_id, props: p, spec, cx, cz, u, a, hf, hd, y0: foot, y1: top, base, foot, wallHex, tileHex, plainKey: key, ranges: [], hidden: false };
    const g = p.confidence;
    const setColour = (hex, dark) => B.set(hex, g, dark || hex === tileHex);
    const tri = (x, y, z) => B.tri(x, y, z);
    const quad = (x, y, z, w) => B.quad(x, y, z, w);

    // Sides of a rectangle, in order, outward.
    const prism = (s, q, y0, y1, hex) => {
      setColour(hex);
      const n = [[-s, q], [s, q], [s, -q], [-s, -q]];
      for (let i = 0; i < 4; i++) {
        const [as, aq] = n[i], [bs, bq] = n[(i + 1) % 4];
        quad(at(as, y1, aq), at(as, y0, aq), at(bs, y0, bq), at(bs, y1, bq));
      }
    };
    const lid = (s, q, y, hex) => { setColour(hex); quad(at(-s, y, q), at(s, y, q), at(s, y, -q), at(-s, y, -q)); };
    const under = (s, q, y) => { setColour(HALL_COLOURS.underside, true); quad(at(-s, y, -q), at(s, y, -q), at(s, y, q), at(-s, y, q)); };

    // A roof over a rectangle: the ridge runs along the longer side. `swap` turns the axes so the code below always thinks ridge = along x, half-length hx; half-width hz.
    const roof = (hs, hq, y0, y1, form, rolled, hex) => {
      const along = hs >= hq;
      const hx = along ? hs : hq, hz = along ? hq : hs;
      const P = (x, y, z) => (along ? at(x, y, z) : at(z, y, -x));
      setColour(hex);
      const band = rolled ? hz * 0.14 : 0; // 卷棚: two ridge purlins, a narrow flat top
      if (form === "gable") {
        quad(P(-hx, y0, hz), P(hx, y0, hz), P(hx, y1, band), P(-hx, y1, band));
        quad(P(hx, y0, -hz), P(-hx, y0, -hz), P(-hx, y1, -band), P(hx, y1, -band));
        if (band) quad(P(-hx, y1, band), P(hx, y1, band), P(hx, y1, -band), P(-hx, y1, -band));
        setColour(hex === HALL_COLOURS.tile.stone ? hex : wallHex);
        for (const s of [-1, 1]) {
          const pts = band ? [P(s * hx, y0, hz), P(s * hx, y1, band), P(s * hx, y1, -band), P(s * hx, y0, -hz)] : [P(s * hx, y0, hz), P(s * hx, y1, 0), P(s * hx, y0, -hz)];
          if (s < 0) { if (band) quad(pts[0], pts[1], pts[2], pts[3]); else tri(pts[0], pts[1], pts[2]); }
          else if (band) quad(pts[3], pts[2], pts[1], pts[0]); else tri(pts[2], pts[1], pts[0]);
        }
      } else if (form === "hip" || form === "pyramid") {
        const r = form === "pyramid" ? 0 : Math.max(hx - hz, 0); // ridge half-length
        quad(P(-hx, y0, hz), P(hx, y0, hz), P(r, y1, band), P(-r, y1, band));
        quad(P(hx, y0, -hz), P(-hx, y0, -hz), P(-r, y1, -band), P(r, y1, -band));
        tri(P(hx, y0, hz), P(hx, y0, -hz), P(r, y1, band && -band));
        if (band) tri(P(hx, y0, hz), P(r, y1, -band), P(r, y1, band));
        tri(P(-hx, y0, -hz), P(-hx, y0, hz), P(-r, y1, band));
        if (band) tri(P(-hx, y0, -hz), P(-r, y1, band), P(-r, y1, -band));
        if (band) quad(P(-r, y1, band), P(r, y1, band), P(r, y1, -band), P(-r, y1, -band));
      } else {
        // 歇山: a hipped skirt, then a gable set in from it.
        const k = 0.42, ib = hz * k, yb = y0 + (y1 - y0) * k;
        const bx = hx - ib, bz = hz - ib;
        quad(P(-hx, y0, hz), P(hx, y0, hz), P(bx, yb, bz), P(-bx, yb, bz));
        quad(P(hx, y0, -hz), P(-hx, y0, -hz), P(-bx, yb, -bz), P(bx, yb, -bz));
        quad(P(hx, y0, hz), P(hx, y0, -hz), P(bx, yb, -bz), P(bx, yb, bz));
        quad(P(-hx, y0, -hz), P(-hx, y0, hz), P(-bx, yb, bz), P(-bx, yb, -bz));
        const b2 = rolled ? bz * 0.2 : 0;
        quad(P(-bx, yb, bz), P(bx, yb, bz), P(bx, y1, b2), P(-bx, y1, b2));
        quad(P(bx, yb, -bz), P(-bx, yb, -bz), P(-bx, y1, -b2), P(bx, y1, -b2));
        if (b2) quad(P(-bx, y1, b2), P(bx, y1, b2), P(bx, y1, -b2), P(-bx, y1, -b2));
        setColour(hex === HALL_COLOURS.tile.stone ? hex : wallHex);
        if (b2) {
          quad(P(-bx, yb, bz), P(-bx, y1, b2), P(-bx, y1, -b2), P(-bx, yb, -bz));
          quad(P(bx, yb, -bz), P(bx, y1, -b2), P(bx, y1, b2), P(bx, yb, bz));
        } else {
          tri(P(-bx, yb, bz), P(-bx, y1, 0), P(-bx, yb, -bz));
          tri(P(bx, yb, -bz), P(bx, y1, 0), P(bx, yb, bz));
        }
      }
    };

    // An octagon about the centre, radius r, prism and optional cone.
    const octagon = (r, y0, y1, yTop, wallCol, roofCol) => {
      const n = 8, pts = [];
      for (let i = 0; i < n; i++) pts.push([r * Math.cos(((i + 0.5) * 2 * Math.PI) / n), r * Math.sin(((i + 0.5) * 2 * Math.PI) / n)]);
      setColour(wallCol);
      for (let i = 0; i < n; i++) {
        const [as, aq] = pts[(i + 1) % n], [bs, bq] = pts[i];
        quad(at(as, y1, aq), at(as, y0, aq), at(bs, y0, bq), at(bs, y1, bq));
      }
      setColour(roofCol);
      const peak = at(0, yTop, 0);
      for (let i = 0; i < n; i++) {
        const [as, aq] = pts[(i + 1) % n], [bs, bq] = pts[i];
        tri(at(as, y1, aq), at(bs, y1, bq), peak);
      }
    };

    const pl = p.platform_m, eave = base + p.eave_m, ridge = top;
    if (p.shape === "terrace") {
      prism(hf, hd, foot, base + p.eave_m, HALL_COLOURS.stone);
      lid(hf, hd, base + p.eave_m, HALL_COLOURS.stone);
    } else if (p.shape === "court") { // a sunken lawn or paving, drawn at ground level
      prism(hf, hd, foot, base + p.eave_m, HALL_COLOURS.court);
      lid(hf, hd, base + p.eave_m, HALL_COLOURS.court);
    } else if (p.shape === "basin") { // a round basin
      octagon(Math.min(hf, hd), foot, base + p.eave_m, base + p.eave_m, HALL_COLOURS.stone, HALL_COLOURS.water);
    } else if (p.shape === "wall") {
      prism(hf, hd, foot, eave, HALL_COLOURS.stone);
      lid(hf, hd, eave, HALL_COLOURS.stone);
    } else if (p.shape === "pool") {
      const rim = 0.6, h = base + p.eave_m;
      for (const [cs, cq, hs, hq] of [[0, hd - rim / 2, hf, rim / 2], [0, -hd + rim / 2, hf, rim / 2], [hf - rim / 2, 0, rim / 2, hd], [-hf + rim / 2, 0, rim / 2, hd]]) {
        const n = [[cs - hs, cq + hq], [cs + hs, cq + hq], [cs + hs, cq - hq], [cs - hs, cq - hq]];
        setColour(HALL_COLOURS.stone);
        for (let i = 0; i < 4; i++) { const [as, aq] = n[i], [bs, bq] = n[(i + 1) % 4]; quad(at(as, h, aq), at(as, foot, aq), at(bs, foot, bq), at(bs, h, bq)); }
        quad(at(n[0][0], h, n[0][1]), at(n[1][0], h, n[1][1]), at(n[2][0], h, n[2][1]), at(n[3][0], h, n[3][1]));
      }
      setColour(HALL_COLOURS.water);
      quad(at(-hf + rim, h - 0.1, hd - rim), at(hf - rim, h - 0.1, hd - rim), at(hf - rim, h - 0.1, -hd + rim), at(-hf + rim, h - 0.1, -hd + rim));
    } else if (p.shape === "octagon") {
      const r = Math.min(hf, hd);
      if (p.ridge_m > p.eave_m) {
        octagon(r, foot, base + pl, base + pl, HALL_COLOURS.stone, HALL_COLOURS.stone);
        octagon(r - edge, base + pl, eave, ridge, wallHex, tileHex);
      } else octagon(r, foot, eave, eave, HALL_COLOURS.stone, HALL_COLOURS.stone);
    } else {
      // Platform, walls inset by the platform edge, then the roof from the eave's edge, half the overhang lower than the wall's top.
      prism(hf, hd, foot, base + pl, HALL_COLOURS.platform);
      lid(hf, hd, base + pl, HALL_COLOURS.platform);
      const ws = Math.max(hf - edge, hf * 0.6), wq = Math.max(hd - edge, hd * 0.6);
      const rs = ws + over, rq = wq + over, tip = eave - over * 0.5;
      const form = p.roof;
      // A wall's top stays under the roof where the roof crosses the wall line, however low its pitch.
      const under_roof = (halfWidth, rise) => Math.min(eave, tip + (0.85 * over * rise) / halfWidth);
      if (p.tiers_m) {
        // A three-storey tower: each tier a little narrower under its own eave.
        let y = base + pl, s = ws, q = wq;
        p.tiers_m.forEach((tier, i) => {
          const yTop = base + tier;
          prism(s, q, y, yTop, wallHex);
          const last = i === p.tiers_m.length - 1;
          const nextS = s * 0.86, nextQ = q * 0.86, lip = over;
          under(s + lip, q + lip, yTop - lip * 0.5);
          if (last) roof(s + lip, q + lip, yTop - lip * 0.5, ridge, "hip_gable", Boolean(p.rolled), tileHex);
          else {
            setColour(tileHex);
            const y2 = yTop + 0.9;
            const n0 = [[-(s + lip), q + lip], [s + lip, q + lip], [s + lip, -(q + lip)], [-(s + lip), -(q + lip)]], n1 = [[-nextS, nextQ], [nextS, nextQ], [nextS, -nextQ], [-nextS, -nextQ]];
            for (let k = 0; k < 4; k++) quad(at(n0[k][0], yTop - lip * 0.5, n0[k][1]), at(n0[(k + 1) % 4][0], yTop - lip * 0.5, n0[(k + 1) % 4][1]), at(n1[(k + 1) % 4][0], y2, n1[(k + 1) % 4][1]), at(n1[k][0], y2, n1[k][1]));
            y = yTop;
            s = nextS;
            q = nextQ;
          }
        });
      } else if (p.double) {
        // Double eaves 重檐: a skirt roof, a short upper wall set in, the main roof.
        const inS = ws * 0.72, inQ = wq * 0.72, yUp = eave + (ridge - eave) * 0.26;
        const y2 = eave + 0.9;
        prism(ws, wq, base + pl, under_roof(rq - inQ, y2 - tip), wallHex);
        under(rs, rq, tip);
        setColour(tileHex);
        const n0 = [[-rs, rq], [rs, rq], [rs, -rq], [-rs, -rq]], n1 = [[-inS, inQ], [inS, inQ], [inS, -inQ], [-inS, -inQ]];
        for (let k = 0; k < 4; k++) quad(at(n0[k][0], tip, n0[k][1]), at(n0[(k + 1) % 4][0], tip, n0[(k + 1) % 4][1]), at(n1[(k + 1) % 4][0], y2, n1[(k + 1) % 4][1]), at(n1[k][0], y2, n1[k][1]));
        prism(inS, inQ, eave, yUp, wallHex);
        const lip = over * 0.7;
        under(inS + lip, inQ + lip, yUp - lip * 0.5);
        roof(inS + lip, inQ + lip, yUp - lip * 0.5, ridge, form, Boolean(p.rolled), tileHex);
      } else if (p.rolls > 1) {
        // Parallel rolls 勾连搭: one gable roof per roll, ridges along the frontage.
        const n = p.rolls, w = (2 * rq) / n;
        prism(ws, wq, base + pl, under_roof(w / 2, ridge - tip), wallHex);
        under(rs, rq, tip);
        for (let i = 0; i < n; i++) {
          const q0 = -rq + i * w, q1 = q0 + w, mid = (q0 + q1) / 2, band = w * 0.07;
          setColour(tileHex);
          quad(at(-rs, tip, q1), at(rs, tip, q1), at(rs, ridge, mid + band), at(-rs, ridge, mid + band));
          quad(at(rs, tip, q0), at(-rs, tip, q0), at(-rs, ridge, mid - band), at(rs, ridge, mid - band));
          quad(at(-rs, ridge, mid + band), at(rs, ridge, mid + band), at(rs, ridge, mid - band), at(-rs, ridge, mid - band));
          setColour(wallHex);
          quad(at(-rs, tip, q1), at(-rs, ridge, mid + band), at(-rs, ridge, mid - band), at(-rs, tip, q0));
          quad(at(rs, tip, q0), at(rs, ridge, mid - band), at(rs, ridge, mid + band), at(rs, tip, q1));
        }
      } else {
        const midY = p.mid_eave_m ? base + p.mid_eave_m : null;
        const wallTop = under_roof(Math.min(rs, rq), ridge - tip);
        prism(ws, wq, base + pl, midY ?? wallTop, wallHex);
        if (midY) {
          // A second storey: a skirt at the middle eave and a wall above it.
          const lip = over * 0.8;
          under(ws + lip, wq + lip, midY - lip * 0.4);
          setColour(tileHex);
          const n0 = [[-(ws + lip), wq + lip], [ws + lip, wq + lip], [ws + lip, -(wq + lip)], [-(ws + lip), -(wq + lip)]], n1 = [[-ws, wq], [ws, wq], [ws, -wq], [-ws, -wq]];
          for (let k = 0; k < 4; k++) quad(at(n0[k][0], midY - lip * 0.4, n0[k][1]), at(n0[(k + 1) % 4][0], midY - lip * 0.4, n0[(k + 1) % 4][1]), at(n1[(k + 1) % 4][0], midY + 0.5, n1[(k + 1) % 4][1]), at(n1[k][0], midY + 0.5, n1[k][1]));
          prism(ws, wq, midY, wallTop, wallHex);
        }
        under(rs, rq, tip);
        roof(rs, rq, tip, ridge, form, Boolean(p.rolled), tileHex);
      }
    }
    entry.ranges.push({ buf: B, start, count: B.count - start });
    info.push(entry);
  }

  const mesh = new THREE.Group();
  const plainMeshes = {};
  for (const B of buffers.slice()) { plainMeshes[B.key] = B.finish(); mesh.add(plainMeshes[B.key]); }

  const paint = (b, fn) => { for (const r of b.ranges) if (!r.buf.dead) for (let i = r.start; i < r.start + r.count; i++) fn(r.buf, i); };
  let confMode = false;
  // Colours in confidence mode: each part carries its own tint (HallBuffer.set): the box's grade on platform and walls, the form's on the kit's roofs and openings.
  const recolour = () => {
    for (const B of buffers) { B.colours.set(confMode ? B.conf : B.plain); B.attr.needsUpdate = true; }
  };
  const live = () => { for (let i = buffers.length - 1; i >= 0; i--) if (buffers[i].dead) buffers.splice(i, 1); };
  let selected = [];
  const c = new THREE.Color();
  const select = (list) => {
    recolour();
    selected = list;
    c.setHex(HALL_COLOURS.selected);
    for (const b of list) {
      paint(b, (B, i) => {
        const k = B.plain[3 * i] + B.plain[3 * i + 1] + B.plain[3 * i + 2] < 306 ? 0.7 : 1;
        B.colours[3 * i] = 255 * c.r * k; B.colours[3 * i + 1] = 255 * c.g * k; B.colours[3 * i + 2] = 255 * c.b * k;
      });
    }
    for (const B of buffers) B.attr.needsUpdate = true;
  };
  const setConfMode = (on) => { confMode = on; select(selected); };
  // The kit's buffers join after it has drawn (kit3d.js): their ranges are already on the entries.
  const addBuffers = (list) => { live(); buffers.push(...list); };
  const repaint = () => { live(); select(selected); };

  // Which meshes show: the plain boxes, or the kit; and the assumed ones or not. `kitOn` is false when there is no kit.
  const setView = ({ kitOn, assumed }) => {
    const show = { pX: true, pXA: assumed, pA: !kitOn && assumed, pK: !kitOn || !assumed, pS: !kitOn };
    for (const [k, m] of Object.entries(plainMeshes)) m.visible = show[k];
    for (const b of info) b.hidden = b.props.assumed && !assumed;
  };

  // Nearest box along a ray, or null.
  const pick = (ray) => {
    const o = ray.origin, d = ray.direction;
    let best = null, bestT = Infinity;
    for (const b of info) {
      if (b.hidden) continue;
      const px = o.x - b.cx, pz = o.z - b.cz;
      const os = px * b.u[0] + pz * b.u[1], oq = px * b.a[0] + pz * b.a[1];
      const ds = d.x * b.u[0] + d.z * b.u[1], dq = d.x * b.a[0] + d.z * b.a[1];
      let t0 = 0, t1 = bestT;
      const slab = (or, dr, lo, hi) => {
        if (Math.abs(dr) < 1e-9) return or >= lo && or <= hi;
        let a0 = (lo - or) / dr, a1 = (hi - or) / dr;
        if (a0 > a1) [a0, a1] = [a1, a0];
        t0 = Math.max(t0, a0);
        t1 = Math.min(t1, a1);
        return t0 <= t1;
      };
      if (slab(os, ds, -b.hf, b.hf) && slab(oq, dq, -b.hd, b.hd) && slab(o.y, d.y, b.y0, b.y1)) { best = b; bestT = t0; }
    }
    return best ? { box: best, t: bestT } : null;
  };
  // Is a point (with a radius) inside any box's footprint? For walking. Pools and low walls count too; only a terrace can be stood on, and that is left out for simplicity.
  const cells = new Map(), CELL = 40;
  const key = (i, j) => i * 100003 + j;
  for (const b of info) {
    if (b.props.shape === "terrace" || b.props.shape === "court") continue;
    const r = Math.hypot(b.hf, b.hd);
    for (let i = Math.floor((b.cx - r) / CELL); i <= Math.floor((b.cx + r) / CELL); i++) for (let j = Math.floor((b.cz - r) / CELL); j <= Math.floor((b.cz + r) / CELL); j++) {
      const k = key(i, j);
      if (!cells.has(k)) cells.set(k, []);
      cells.get(k).push(b);
    }
  }
  const blocked = (x, z, radius = 0.5) => {
    for (const b of cells.get(key(Math.floor(x / CELL), Math.floor(z / CELL))) || []) {
      if (b.hidden) continue;
      const px = x - b.cx, pz = z - b.cz;
      if (Math.abs(px * b.u[0] + pz * b.u[1]) < b.hf + radius && Math.abs(px * b.a[0] + pz * b.a[1]) < b.hd + radius) return true;
    }
    return false;
  };
  return { mesh, info, select, setConfMode, pick, blocked, setView, addBuffers, repaint, plainMeshes };
}
