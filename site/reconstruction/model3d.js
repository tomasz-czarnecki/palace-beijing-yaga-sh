// The model preview in the building panel of the 3D view: one small scene with only the selected object. Classic script, loaded before 3d.js; defines the global createModelPreview.
// Round 13: copied from the sister project kostrzyn-yaga-sh (site/reconstruction/model3d.js), unchanged but for this line and the caption: here it shows a detailed model (models/<ID>-<slug>/) only.
// modelFor(id) (3d.js) hands over an Object3D in the main scene's coordinates and owned by this file, which disposes it at the next selection. userData: ground (height of its ground, in the same axes), front ([x, z] or null), props (the feature's properties, for the caption).
// One extra WebGLRenderer, made on the first selection and reused. It draws only while the panel is open and the canvas is on screen, only when something changed, and, apart from a selection's first frame, not while the main view is moving (busy). Under automation it doesn't auto-turn: on a software renderer the turn alone burns a whole core.
const PREVIEW = { paper: 0xfbf8f3, fov: 26, elevation: 0.38, turn: 1.5, frameMs: 33, figureM: 1.8, figureMinPx: 9 }; // elevation in radians; turn: 1.5 = 40 s for a full turn
const round = (v) => (v < 100 ? Math.round(v * 10) / 10 : Math.round(v));

// The long axis of what's in the model, and its size along and across that axis, on the ground.
function footprintOf(model) {
  const pts = [];
  model.traverse((o) => {
    const a = o.isMesh && o.geometry.attributes.position;
    if (a) for (let i = 0; i < a.count; i++) pts.push([a.getX(i), a.getZ(i)]);
  });
  const cx = pts.reduce((t, p) => t + p[0], 0) / pts.length, cz = pts.reduce((t, p) => t + p[1], 0) / pts.length;
  let xx = 0, zz = 0, xz = 0;
  for (const [x, z] of pts) { xx += (x - cx) ** 2; zz += (z - cz) ** 2; xz += (x - cx) * (z - cz); }
  const angle = Math.atan2(2 * xz, xx - zz) / 2, axis = [Math.cos(angle), Math.sin(angle)];
  let a0 = Infinity, a1 = -Infinity, c0 = Infinity, c1 = -Infinity;
  for (const p of pts) {
    const a = p[0] * axis[0] + p[1] * axis[1], c = p[1] * axis[0] - p[0] * axis[1];
    a0 = Math.min(a0, a); a1 = Math.max(a1, a); c0 = Math.min(c0, c); c1 = Math.max(c1, c);
  }
  return { pts, axis, length: a1 - a0, width: c1 - c0 };
}

// One line from the data. Size: as stated for a house, measured on the solid for the rest. Heights: above the ground the preview stands on.
function captionOf(p, foot, ground, datum) {
  const size = p.frontage_m ? [p.frontage_m, p.depth_m] : [foot.length, foot.width];
  const out = [`${size.map(round).join(" × ")} m`];
  if (p.parts) {
    const tower = p.parts.find((q) => q.part === "tower"), body = p.parts.filter((q) => q !== tower);
    out.push(`eave ${round(Math.max(...body.map((q) => q.eave_m)))} m`, `ridge ${round(Math.max(...body.map((q) => q.ridge_m)))} m`);
    if (tower) out.push(`tower ${round(tower.ridge_m)} m`);
  } else if (p.eave_m) out.push(`eave ${round(p.eave_m)} m`, `ridge ${round(p.ridge_m)} m`);
  else out.push(`${round(p.top_m - datum - ground)} m ${p.kind === "gate" ? "above the street" : "above its base"}`);
  out.push(p.assumed && p.confidence === "C" ? "assumed volume (C)" : `confidence ${p.confidence}`);
  return out.join(" · ");
}

function createModelPreview({ modelFor, sunDir, datum, busy }) {
  let renderer = null, scene, camera, controls, holder, disc, shadow, light, figure, figureNote, caption, wrap;
  let current = null; // { id, model, box, foot }
  let dirty = false, fresh = false, onScreen = false, raf = 0, last = 0, failed = false;
  const still = () => navigator.webdriver || matchMedia("(prefers-reduced-motion: reduce)").matches;
  const lightbox = document.getElementById("lightbox");

  function setUp() {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.autoUpdate = false; // nothing in the scene moves but the camera
    renderer.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)]; // the walls run on below the ground
    scene = new THREE.Scene();
    scene.background = new THREE.Color(PREVIEW.paper);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8370, 1.5));
    light = new THREE.DirectionalLight(0xffffff, 2.2);
    light.castShadow = true;
    light.shadow.mapSize.set(1024, 1024);
    light.shadow.radius = 4;
    scene.add(light, light.target);
    const fill = new THREE.DirectionalLight(0xffffff, 0.8); // the side away from the sun still reads
    fill.position.set(-sunDir.x, 0.3, -sunDir.z);
    scene.add(fill);
    camera = new THREE.PerspectiveCamera(PREVIEW.fov, 1, 1, 100);
    holder = new THREE.Group();
    scene.add(holder);

    const plane = new THREE.PlaneGeometry(1, 1);
    plane.rotateX(-Math.PI / 2);
    const ramp = document.createElement("canvas");
    ramp.width = ramp.height = 128;
    const ctx = ramp.getContext("2d"), grad = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
    grad.addColorStop(0, "rgba(201,190,170,.55)");
    grad.addColorStop(0.6, "rgba(201,190,170,.35)");
    grad.addColorStop(1, "rgba(201,190,170,0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 128);
    const texture = new THREE.CanvasTexture(ramp);
    texture.colorSpace = THREE.SRGBColorSpace;
    disc = new THREE.Mesh(plane, new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false }));
    shadow = new THREE.Mesh(plane, new THREE.ShadowMaterial({ color: 0x3a3226, opacity: 0.32, depthWrite: false }));
    shadow.receiveShadow = true;
    shadow.renderOrder = 1;
    scene.add(disc, shadow);

    figure = new THREE.Group();
    const dark = new THREE.MeshLambertMaterial({ color: 0x3a3226 });
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.19, 1.5, 12), dark), head = new THREE.Mesh(new THREE.SphereGeometry(0.13, 12, 10), dark);
    body.position.y = 0.75;
    head.position.y = PREVIEW.figureM - 0.13;
    body.castShadow = head.castShadow = true;
    figure.add(body, head);
    scene.add(figure);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enablePan = false;
    controls.maxPolarAngle = Math.PI / 2 - 0.02;
    controls.autoRotateSpeed = PREVIEW.turn;
    controls.addEventListener("change", () => { dirty = true; start(); });
    const canvas = renderer.domElement;
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", "3D model of the selected object: drag to turn, wheel or pinch to zoom, double-click to reset");
    canvas.addEventListener("pointerdown", () => { controls.autoRotate = false; });
    canvas.addEventListener("dblclick", resetView);

    wrap = document.createElement("figure");
    figureNote = document.createElement("span");
    figureNote.className = "bp-figure";
    figureNote.textContent = `Figure: ${PREVIEW.figureM} m`;
    caption = document.createElement("figcaption");
    wrap.append(canvas, figureNote, caption);

    new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; if (onScreen) { dirty = true; start(); } }).observe(canvas);
    new ResizeObserver(() => {
      const w = canvas.clientWidth, h = canvas.clientHeight, size = renderer.getSize(new THREE.Vector2());
      if (!w || !h || (w === size.x && h === size.y)) return;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      if (current) place();
      dirty = true;
      start();
    }).observe(canvas);
  }

  function resetView() {
    controls.reset();
    controls.autoRotate = !still();
    dirty = true;
    start();
  }

  function start() {
    if (raf) return;
    last = performance.now();
    raf = requestAnimationFrame(tick);
  }

  function tick(now) {
    raf = 0;
    if (!current || !onScreen || !(dirty || controls.autoRotate)) return; // nothing to draw: a change starts it again
    raf = requestAnimationFrame(tick);
    if (!lightbox.hidden || now - last < PREVIEW.frameMs || (busy() && !fresh)) return;
    controls.update(Math.min((now - last) / 1000, 0.1));
    last = now;
    if (dirty) { dirty = fresh = false; renderer.render(scene, camera); }
  }

  // The nearest distance at which every corner of the box stays in frame, whichever way the turn has got: a corner p needs d >= depth + |x| / tan, depth towards the camera.
  function fitDistance(box) {
    const c = box.getCenter(new THREE.Vector3()), tanV = Math.tan((PREVIEW.fov * Math.PI) / 360), tanH = tanV * camera.aspect;
    const ce = Math.cos(PREVIEW.elevation), se = Math.sin(PREVIEW.elevation);
    let d = 1;
    for (let n = 0; n < 24; n++) {
      const a = (n / 24) * 2 * Math.PI, hx = Math.cos(a), hz = Math.sin(a);
      for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
        const px = x - c.x, py = y - c.y, pz = z - c.z;
        const depth = px * hx * ce + py * se + pz * hz * ce, right = pz * hx - px * hz, up = py * ce - (px * hx + pz * hz) * se;
        d = Math.max(d, depth + Math.abs(right) / tanH, depth + Math.abs(up) / tanV);
      }
    }
    return d * 1.05;
  }

  // Puts the object on its ground at the origin, and the camera, the ground, the shadow and the figure around it.
  function place() {
    const { model, foot, front, ground } = current;
    holder.position.set(0, 0, 0); // setFromObject trusts the parents' world matrix, which still holds the last selection's offset
    holder.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(model);
    const cx = (box.min.x + box.max.x) / 2, cz = (box.min.z + box.max.z) / 2;
    holder.position.set(-cx, -ground, -cz);
    const local = new THREE.Box3(new THREE.Vector3(box.min.x - cx, 0, box.min.z - cz), new THREE.Vector3(box.max.x - cx, box.max.y - ground, box.max.z - cz));
    const height = local.max.y, reach = foot.pts.reduce((r, p) => Math.max(r, Math.hypot(p[0] - cx, p[1] - cz)), 0);

    // First view: the street face, or else the long side on the sun's side, a little off square and towards the sun.
    const side = [-foot.axis[1], foot.axis[0]], sunny = side[0] * sunDir.x + side[1] * sunDir.z >= 0 ? 1 : -1;
    const face = front || [side[0] * sunny, side[1] * sunny], off = face[0] * sunDir.z - face[1] * sunDir.x >= 0 ? 0.5 : -0.5;
    const view = [face[0] * Math.cos(off) - face[1] * Math.sin(off), face[0] * Math.sin(off) + face[1] * Math.cos(off)];

    // The figure stands just in front of the nearest point of the object. It only shows if it comes out big enough to read.
    const near = foot.pts.reduce((b, p) => { const v = (p[0] - cx) * view[0] + (p[1] - cz) * view[1]; return v > b.v ? { v, p } : b; }, { v: -Infinity, p: null }).p;
    const fx = near[0] - cx + view[0] * 1.6, fz = near[1] - cz + view[1] * 1.6;
    const fitBox = local.clone().expandByPoint(new THREE.Vector3(fx, 0, fz));
    const dist = fitDistance(fitBox), target = fitBox.getCenter(new THREE.Vector3());
    const size = renderer.getSize(new THREE.Vector2()), perMetre = size.y / (2 * dist * Math.tan((PREVIEW.fov * Math.PI) / 360));
    figure.position.set(fx, 0, fz);
    figure.visible = PREVIEW.figureM * perMetre >= PREVIEW.figureMinPx;
    figureNote.hidden = !figure.visible;

    // The ground fades out just before the frame's lower edge: the widest r with a ground point towards the camera still in view. Same look at any size.
    const tanV = Math.tan((PREVIEW.fov * Math.PI) / 360), ce = Math.cos(PREVIEW.elevation), se = Math.sin(PREVIEW.elevation), lower = target.y * ce;
    const rGround = (0.94 * (tanV * (dist + target.y * se) - lower)) / (se + tanV * ce), lift = Math.max(reach, height) * 0.0015;
    disc.scale.set(2 * rGround, 1, 2 * rGround);
    disc.position.y = lift;
    const rShadow = reach + height * 1.4;
    shadow.scale.set(2 * rShadow, 1, 2 * rShadow);
    shadow.position.y = 2 * lift;
    const reachLight = rShadow * 2;
    light.position.copy(sunDir).multiplyScalar(reachLight);
    light.target.position.set(0, 0, 0);
    Object.assign(light.shadow.camera, { left: -rShadow, right: rShadow, top: rShadow, bottom: -rShadow, near: 0.1, far: reachLight * 2 });
    light.shadow.camera.updateProjectionMatrix();
    renderer.shadowMap.needsUpdate = true;

    Object.assign(camera, { near: dist * 0.02, far: dist * 6 });
    camera.updateProjectionMatrix();
    controls.target.copy(target);
    camera.position.set(target.x + view[0] * dist * ce, target.y + dist * se, target.z + view[1] * dist * ce);
    controls.minDistance = dist * 0.35;
    controls.maxDistance = dist * 1.8;
    controls.autoRotate = !still();
    controls.update();
    controls.saveState();
    dirty = fresh = true;
  }

  function clear() {
    if (current) {
      holder.remove(current.model);
      current.model.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        for (const m of [].concat(o.material || [])) m.dispose();
      });
      current = null;
    }
    if (wrap) wrap.remove();
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
  }

  // Into `slot`, the preview of `id`; no id, or nothing to show for it, leaves the slot empty. The same object again keeps its view.
  function show(id, slot) {
    if (current && current.id === id) { slot.append(wrap); return; }
    clear();
    if (!id || !slot || failed) return;
    if (!renderer) {
      try { setUp(); } catch (err) { failed = true; console.warn("No model preview:", err); return; }
    }
    const model = modelFor(id);
    if (!model) return;
    slot.append(wrap);
    const { ground, front, props } = model.userData, foot = footprintOf(model);
    holder.add(model);
    current = { id, model, foot, front, ground };
    caption.textContent = captionOf(props, foot, ground, datum);
    const w = renderer.domElement.clientWidth, h = renderer.domElement.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    place();
    if (onScreen) start();
  }

  return { show, clear, get renderer() { return renderer; }, get camera() { return camera; }, get controls() { return controls; }, get holder() { return holder; } };
}
