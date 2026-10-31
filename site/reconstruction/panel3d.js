// The building panel of the 3D view: one scrolling column of what we know about what was clicked. Classic script, loaded before 3d.js; defines the global createBuildingPanel.
// Data: data/buildings/<ID>.json (scripts/building_pages.py). On the research machine (local = true) it reads /_local/buildings/<ID>.json, the full copy, and falls back to the public file.
// `notes_html` was rendered at build time with raw HTML escaped; every other string is set as text.
// Pictures arrive as link entries for now: title, date, holder and a link. The pictures round brings the free images.
function createBuildingPanel({ local, onClose, onOpen }) {
  const root = document.getElementById("bpanel");
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
  const cache = {};

  function load(id) {
    if (!cache[id]) {
      const pub = () => fetch(`data/buildings/${encodeURIComponent(id)}.json`).then((r) => { if (!r.ok) throw new Error(`no page for ${id}`); return r.json(); });
      cache[id] = local ? fetch(`/_local/buildings/${encodeURIComponent(id)}.json`).then((r) => (r.ok ? r.json() : pub())).catch(pub) : pub();
      cache[id].catch(() => delete cache[id]);
    }
    return cache[id];
  }

  function section(title) {
    const s = el("section");
    s.append(el("h3", "", title));
    return s;
  }

  function rowList(rows) {
    const dl = el("dl");
    for (const [k, v] of rows) dl.append(el("dt", "", k), el("dd", "", v));
    return dl;
  }

  function factList(page) {
    const ul = el("ul", "facts");
    for (const f of page.facts) {
      const li = el("li");
      li.append(el("b", "", f.label + ": "), document.createTextNode(f.value));
      const tag = [f.sources.replaceAll(";", ", "), f.confidence && `confidence ${f.confidence}`].filter(Boolean).join(" · ");
      if (tag) li.append(el("span", "tag", tag));
      if (f.private) li.append(el("span", "copy", "research copy, not public"));
      ul.append(li);
    }
    return ul;
  }

  function linkTo([id, name], list) {
    const li = el("li");
    const b = el("button", "bp-link", name ? `${name} (${id})` : id);
    b.type = "button";
    b.onclick = () => onOpen(id);
    li.append(b);
    list.append(li);
  }

  function linkCard(photo) {
    const card = el("div", "ph-link");
    card.append(el("div", "ph-title", photo.title));
    card.append(el("div", "ph-meta", [photo.date, photo.creator].filter(Boolean).join(" · ")));
    card.append(el("div", "ph-meta", photo.archive));
    const a = el("a", "", "View at the holder");
    a.href = photo.source_url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    card.append(a);
    return card;
  }

  function show(page) {
    const body = el("div", "bp-body");
    const head = el("header", "bp-head");
    const title = el("div");
    title.append(el("h2", "", page.title));
    if (page.subtitle) title.append(el("div", "bp-sub", page.subtitle));
    title.append(el("div", "ids", page.id));
    const close = el("button", "bp-close", "×");
    close.type = "button";
    close.setAttribute("aria-label", "Close");
    close.onclick = onClose;
    head.append(title, close);

    if (page.parent) {
      const s = section("Part of");
      const ul = el("ul", "bp-links");
      linkTo(page.parent, ul);
      s.append(ul);
      body.append(s);
    }
    if (page.model) {
      const s = section("Our model now");
      s.append(el("p", "bp-line", page.model.line), rowList(page.model.rows));
      body.append(s);
    }
    const s = section("What we know");
    s.append(factList(page));
    if (page.notes_html) {
      const notes = el("div", "bp-notes");
      notes.innerHTML = page.notes_html;
      s.append(notes);
    }
    body.append(s);
    if (page.children && page.children.length) {
      const k = section(`Inside it (${page.children.length})`);
      const ul = el("ul", "bp-links");
      page.children.forEach((c) => linkTo(c, ul));
      k.append(ul);
      body.append(k);
    }
    if (page.photos.length) {
      const ph = section(`Pictures (${page.photos.length})`);
      page.photos.forEach((p) => ph.append(linkCard(p)));
      body.append(ph);
    }
    if (page.questions.length) {
      const q = section("Open questions");
      const ul = el("ul", "facts");
      for (const x of page.questions) ul.append(el("li", "", `${x.id}: ${x.title}`));
      q.append(ul);
      body.append(q);
    }
    if (page.sources.length) {
      const q = section("Sources");
      const ul = el("ul", "facts sources");
      for (const x of page.sources) {
        const li = el("li");
        li.append(el("b", "", x.id + " "));
        if (x.url) {
          const a = el("a", "", x.text || x.url);
          a.href = x.url;
          a.target = "_blank";
          a.rel = "noopener";
          li.append(a);
        } else li.append(document.createTextNode(x.text));
        if (x.licence) li.append(el("span", "tag", x.licence));
        ul.append(li);
      }
      q.append(ul);
      body.append(q);
    }
    root.replaceChildren(head, body);
    root.hidden = false;
    root.scrollTop = 0;
    document.body.classList.add("panel-open");
  }

  function fail(id) {
    const head = el("header", "bp-head"), close = el("button", "bp-close", "×");
    close.type = "button";
    close.setAttribute("aria-label", "Close");
    close.onclick = onClose;
    head.append(el("h2", "", id), close);
    root.replaceChildren(head, el("p", "bp-line", "This page could not be loaded."));
    root.hidden = false;
    document.body.classList.add("panel-open");
  }

  function hide() {
    root.hidden = true;
    document.body.classList.remove("panel-open");
  }

  addEventListener("keydown", (e) => { if (e.key === "Escape" && !root.hidden) onClose(); });
  return { load, show, fail, hide };
}
