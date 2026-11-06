// Working map of the gardens before October 1860: today's OSM as the base, the public layers of data/ as toggles. The layer control is also the legend. A click opens names, sources and confidence.
// All these layers are public: geometry traced from S01, credited (research/README.md). On the research machine (tools/serve_local.py, which marks its answers with X-Palace-Local) the georeferenced plan S01 is offered under /_local/ as well; it is not in site/ and never public. ?public=1 shows what a visitor sees. ?layers=all or ?layers=water_1860,walls_1860 chooses the layers, ?plan=0.5 shows the plan at that opacity.
const params = new URLSearchParams(location.search);
const LOCAL_HOST = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname) && !params.get("public");

const CREDIT = 'S01 traced, image courtesy of the Princeton University Art Museum · <a href="../credits.html">sources and credits</a>';
const map = L.map("map", { preferCanvas: true }).setView([40.0045, 116.2985], 14);
window.map = map;
const osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: `© OpenStreetMap contributors (ODbL) · ${CREDIT}`,
}).addTo(map);
L.control.scale({ imperial: false }).addTo(map);

const load = (name) => fetch(`data/${name}.geojson`).then((r) => r.json());
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
// A popup: Chinese and pinyin first, then the English, then the source and confidence. The 3D link goes to the building's page.
function popup(p, extra = "") {
  const box = document.createElement("div");
  const zh = p.name_zh || p.name || "";
  const title = [zh, p.name_pinyin].filter(Boolean).join(" ") || p.id;
  const bid = p.building_id || (/^(YM|CC|XY|QC|Z-|OW)/.test(p.id || "") ? p.id : "");
  box.innerHTML = `<div class="pop-title">${esc(title)}</div>` +
    (p.name_en ? `<div class="pop-sub">${esc(p.name_en)}</div>` : "") +
    `<div class="pop-tag">${esc(p.id)}${p.garden ? " · " + esc(p.garden) : ""}</div>` + extra +
    `<div class="pop-tag">sources ${esc((p.sources || "").replaceAll(";", ", "))}${p.confidence ? " · confidence " + esc(p.confidence) : ""}${p.assumed ? " · ASSUMED" : ""}</div>` +
    (p.note ? `<div class="pop-note">${esc(p.note)}</div>` : "") +
    (bid ? `<div><a href="3d.html?b=${encodeURIComponent(bid)}">Open in the 3D view</a></div>` : "");
  return box;
}
const line = (color) => `<span class="sw line" style="border-color:${color}"></span>`;
const fill = (color, edge) => `<span class="sw" style="background:${color};border-color:${edge || color}"></span>`;
const dot = (color) => `<span class="sw dot" style="background:${color}"></span>`;
const kindOf = (p) => ({ outer_wall: "garden wall", separating_wall: "wall between gardens" }[p.kind] || p.kind);
// Placement accuracy (Round 8): how far a position taken from the plan may stand from where it stood, in metres, from the blind check set.
const errColour = (m) => (m == null ? "#9ca3af" : m < 5 ? "#15803d" : m < 10 ? "#65a30d" : m < 20 ? "#eab308" : m < 40 ? "#ea580c" : "#b91c1c");
const errScale = `<span class="sw" style="background:linear-gradient(90deg,#15803d,#65a30d,#eab308,#ea580c,#b91c1c)"></span>`;
const errText = (p) => p.kind === "region"
  ? `<div class="pop-tag">${esc(p.region)} · check set: median ${esc(p.median_m)} m, 90% within ${esc(p.p90_m)} m, worst ${esc(p.max_m)} m (${esc(p.n_check)} points)</div><div class="pop-tag">previous fit: median ${esc(p.previous_median_m)} m, 90% ${esc(p.previous_p90_m)} m, worst ${esc(p.previous_max_m)} m · fit in use here: ${esc(p.fit)}</div>`
  : p.kind === "cell" ? `<div class="pop-tag">expected about ${esc(p.expected_m)} m (estimate between check points; nearest ${esc(p.nearest_check_m)} m away)</div>`
  : `<div class="pop-sub">${esc(p.feature)}</div><div class="pop-tag">check point (${esc(p.point_kind)}), never in a fit: off by ${esc(p.dist_m)} m (east ${esc(p.dE_m)}, north ${esc(p.dN_m)}); previous fit ${esc(p.previous_dist_m)} m</div>`;

// [file, name, swatch, Leaflet options, on by default, extra lines for the popup]. Added in this order, so the small things lie on top.
const LAYERS = [
  ["osm_today", "Today's park (OSM)", dot("#7c3aed"), {
    style: (f) => ({ color: f.properties.kind === "water" ? "#60a5fa" : f.properties.kind === "ruin" ? "#7c3aed" : "#a78bfa", weight: 1, fillOpacity: 0.12 }),
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 3, color: "#7c3aed", weight: 1, fillOpacity: 0.7 }),
  }, false, (p) => `<div class="pop-sub">${esc(p["name:en"] || "")} today's state</div>`],
  ["georef_error", "Placement accuracy: expected error of a position, from the blind check set (green under 5 m, red over 40 m)", errScale, {
    style: (f) => f.properties.kind === "region" ? { color: "#111827", weight: 2, dashArray: "6 4", fill: false } : { color: errColour(f.properties.expected_m), weight: 0, fillColor: errColour(f.properties.expected_m), fillOpacity: 0.45 },
    // Check points as small squares in the marker pane, above the canvas layers, so walls and gates never hide them.
    pointToLayer: (f, ll) => L.marker(ll, { icon: L.divIcon({ className: "", iconSize: [12, 12], html: `<div style="width:10px;height:10px;border:1px solid #111827;background:${errColour(f.properties.dist_m)}"></div>` }) }),
  }, false, errText],
  // Round 20: what stood and ran round the gardens (scripts/surroundings1860.py): roads, canals, villages, camps, the neighbouring gardens. Mostly C: the popup says how sure.
  ["surroundings_1860", "Around the gardens, 1860 (mostly C)", fill("#e7d3a8", "#8a5a2b"), {
    style: (f) => ({ color: { road: "#8a5a2b", canal: "#1d6fa5", river: "#1d6fa5" }[f.properties.kind] || "#8a5a2b", weight: f.properties.kind === "road" ? 2 : 1.5, dashArray: f.properties.confidence === "C" ? "5 4" : null, fillColor: f.properties.kind === "neighbour_garden" ? "#c9d7a4" : "#e7d3a8", fillOpacity: 0.3 }),
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 4, color: "#fff", weight: 1, fillColor: f.properties.confidence === "C" ? "#d6a35c" : "#8a5a2b", fillOpacity: 0.95 }),
  }, true, (p) => `<div class="pop-tag">${esc(p.kind.replace("_", " "))}${p.state_1860 ? " · 1860: " + esc(p.state_1860) : ""}</div>${p.position_basis ? `<div class="pop-tag">where: ${esc(p.position_basis)}</div>` : ""}`],
  ["fields_1860", "Rice fields 稻田", fill("#d9e2a0", "#7c8f33"), { style: () => ({ color: "#7c8f33", weight: 1, fillColor: "#d9e2a0", fillOpacity: 0.7 }) }, true],
  ["scenes_1860", "Scenes and compounds (outline drawn by the reader, not a source)", fill("#fde68a55", "#b45309"), { style: () => ({ color: "#b45309", weight: 1, dashArray: "4 3", fillColor: "#fde68a", fillOpacity: 0.12 }) }, true, (p) => `<div class="pop-tag">${p.area_m2 ? p.area_m2.toLocaleString("en") + " m²" : ""}${p.malone_no ? " · Malone no. " + esc(p.malone_no) : ""}</div>`],
  ["islands_1860", "Islands", fill("#c9d7a4", "#6b7f3a"), { style: () => ({ color: "#6b7f3a", weight: 1, fillColor: "#c9d7a4", fillOpacity: 0.45 }) }, true, (p) => `<div class="pop-tag">${p.area_m2 ? p.area_m2.toLocaleString("en") + " m²" : ""}</div>`],
  ["water_1860", "Water: lakes, ponds, canals", fill("#7fb2d6", "#1d6fa5"), { style: () => ({ color: "#1d6fa5", weight: 1, fillColor: "#7fb2d6", fillOpacity: 0.75 }) }, true, (p) => `<div class="pop-tag">${esc(p.kind)}${p.area_m2 ? " · " + p.area_m2.toLocaleString("en") + " m²" : ""}</div>`],
  ["hills_1860", "Hills (height C)", fill("#8aa672", "#3f6130"), { style: () => ({ color: "#3f6130", weight: 1, fillColor: "#8aa672", fillOpacity: 0.65 }) }, true, (p) => `<div class="pop-tag">about ${esc(p.height_est_m)} m high, estimated</div>`],
  ["walls_1860", "Garden walls and gates", line("#7f1d1d"), {
    style: (f) => ({ color: f.properties.kind === "separating_wall" ? "#b45309" : "#7f1d1d", weight: 2.5 }),
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 4, color: "#fff", weight: 1, fillColor: "#7f1d1d", fillOpacity: 1 }),
  }, true, (p) => `<div class="pop-tag">${esc(kindOf(p))}</div>`],
  ["bridges_1860", "Bridges", line("#57534e"), { style: () => ({ color: "#57534e", weight: 2.5 }) }, true],
  ["footprints_1860", "Footprints as drawn on the plan", fill("#d6483b88", "#991b1b"), { style: () => ({ color: "#991b1b", weight: 0.7, fillColor: "#ef4444", fillOpacity: 0.5 }) }, true, (p) => `<div class="pop-tag">${esc(p.hall_class)}, ${esc(p.frontage_m)} × ${esc(p.depth_m)} m by the hall scale</div>`],
  ["halls_1860", "Boxes of the 3D view (dashed: assumed)", fill("#3b82f655", "#1e40af"), { style: (f) => ({ color: f.properties.assumed ? "#be185d" : "#1e40af", weight: 0.8, dashArray: f.properties.assumed ? "3 2" : null, fillColor: f.properties.assumed ? "#f472b6" : "#3b82f6", fillOpacity: 0.3 }) }, false, (p) => `<div class="pop-tag">${esc(p.hall_class)}, ${esc(p.frontage_m)} × ${esc(p.depth_m)} m, eave ${esc(p.eave_m)} m, ridge ${esc(p.ridge_m)} m, ${esc(p.roof)}; basis: ${esc(p.basis)}</div>`],
  ["buildings_1860", "Buildings and compounds as points", dot("#0f766e"), {
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: f.properties.parent_id ? 2 : 4, color: "#fff", weight: 0.7, fillColor: f.properties.parent_id ? "#0f766e" : "#b45309", fillOpacity: 0.95 }),
  }, false, (p) => `<div class="pop-tag">${esc(p.type)}${p.built ? " · built " + esc(p.built) : ""}${p.pos_confidence ? " · position " + esc(p.pos_confidence) : ""}</div>`],
];

// Opacity slider for the georeferenced plan.
function addOpacitySlider(layer, title) {
  const control = L.control({ position: "bottomleft" });
  control.onAdd = () => {
    const box = L.DomUtil.create("div", "leaflet-bar");
    box.style.cssText = "background:#fff;padding:4px 8px;font:12px system-ui";
    box.innerHTML = `${title} <input id="plan-opacity" type="range" min="0" max="1" step="0.05" value="${layer.options.opacity}">`;
    L.DomEvent.disableClickPropagation(box);
    box.querySelector("input").oninput = (e) => layer.setOpacity(e.target.value);
    return box;
  };
  control.addTo(map);
}

async function main() {
  // /_local/ is there only when the answer says so: a plain static server gets no request for it, so no 404.
  const local = LOCAL_HOST && (await fetch(location.href, { method: "HEAD" }).then((r) => r.headers.get("X-Palace-Local") === "1").catch(() => false));
  const overlays = {};
  if (local) {
    const o = await fetch("/_local/overlays/princeton-1920s.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
    if (o) {
      const plan = L.imageOverlay(`/_local/overlays/${o.image}`, o.bounds_leaflet, { opacity: Number(params.get("plan") || 0.6) });
      overlays[`${fill("#d8cdb4", "#8a7a55")} The plan S01 (local only, not public)`] = plan;
      if (params.get("plan")) plan.addTo(map);
      addOpacitySlider(plan, "Plan S01");
    }
  }
  const data = await Promise.all(LAYERS.map(([file]) => load(file)));
  const chosen = params.get("layers");
  LAYERS.forEach(([file, name, swatch, opts, on, extra], i) => {
    const layer = L.geoJSON(data[i], { ...opts, onEachFeature: (f, l) => l.bindPopup(() => popup(f.properties, extra ? extra(f.properties) : ""), { maxWidth: 340 }) });
    overlays[`${swatch} ${name} <span class="note">(${data[i].features.length})</span>`] = layer;
    if (chosen ? chosen === "all" || chosen.split(",").includes(file) : on) layer.addTo(map);
    if (file === "walls_1860") map.fitBounds(layer.getBounds(), { padding: [20, 20] });
  });
  L.control.layers({ OpenStreetMap: osm }, overlays, { collapsed: false }).addTo(map);
  window.__ready = true;
}

main();
