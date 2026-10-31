// The building panel of the 3D view: one scrolling column of what we know about what was clicked. Classic script, loaded before 3d.js; defines the global createBuildingPanel.
// Data: data/buildings/<ID>.json (scripts/building_pages.py). On the research machine (local = true) it reads /_local/buildings/<ID>.json, the full copy, and falls back to the public file.
// `notes_html` was rendered at build time with raw HTML escaped; every other string is set as text.
// Evidence comes first, because it is what a click is for: the object's own pictures, its own texts and drawings, the plan as a link; then reconstructions by other people (modern interpretation, not evidence), surviving comparable buildings (not this building), then what speaks for its set of buildings (`fallback`), fetched from that page. A research-only picture or reconstruction is a `link_only` entry: title, date, holder and a link, never an image. The research copy on localhost may carry a local image for it, marked as such.
function createBuildingPanel({ local, onClose, onOpen }) {
  const root = document.getElementById("bpanel");
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
  const cache = {};
  const GROUPS = [["stood", "Made while it stood"], ["later", "Later prints and copies"], ["ruins", "Photographs of the ruins"], ["today", "Today"]];
  const KIND = { poem: "Poem", text: "Text", description: "Description", drawing: "Drawing", plan: "Plan", archaeology: "Archaeology" };
  const NOT_EVIDENCE = "Modern interpretation, not evidence. Each author's own reading of the sources; nothing here sets a position or a size in our model.";
  const NOT_THIS = "These buildings stand elsewhere. They show what the lost building may have looked like, not the building itself.";
  const COPY = "research copy, not public";
  let shown = null; // guards the fallback, fetched after the panel opens

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

  function outLink(url, label) {
    const a = el("a", "", label);
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    return a;
  }

  function holderName(url) {
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch (e) { return "the holder"; }
  }

  function conf(photo) {
    return el("span", `conf ${photo.conf}`, photo.conf);
  }

  // A research-only picture: no image, no thumbnail, no hotlink.
  function linkCard(photo) {
    const card = el("div", "ph-link");
    card.append(el("div", "ph-title", photo.title));
    card.append(el("div", "ph-meta", [photo.date, photo.creator].filter(Boolean).join(" · ")));
    if (photo.why || photo.era) {
      const d = el("div", "ph-shows");
      d.append(conf(photo), document.createTextNode(" " + (photo.why || "")));
      card.append(d);
    }
    card.append(el("div", "ph-meta", photo.archive));
    if (photo.caveat) card.append(el("div", "ph-caveat", photo.caveat));
    if (photo.status && photo.status !== "viewed") card.append(el("span", "ev-index", "seen in a search index only"));
    if (photo.image) {
      const img = el("img", "ph-local");
      img.src = photo.image;
      img.alt = photo.title;
      img.loading = "lazy";
      card.append(img, el("span", "copy", COPY));
    }
    card.append(outLink(photo.source_url, `View at ${holderName(photo.source_url)}`));
    return card;
  }

  // The tile opens the larger view, which holds the reason, the licence and the source.
  function tile(photo, list, big) {
    const fig = el("figure", big ? "ph big" : "ph");
    const b = el("button", "ph-open");
    b.type = "button";
    b.setAttribute("aria-label", `Enlarge: ${photo.title}`);
    const img = el("img");
    img.src = big ? photo.image : photo.thumb;
    img.alt = photo.title;
    img.loading = "lazy";
    b.append(img);
    b.onclick = () => openPhoto(list, list.indexOf(photo));
    fig.append(b);
    const cap = el("figcaption");
    const of = photo.of ? `${photo.of[1] || photo.of[0]}: ` : "";
    cap.append(el("div", "ph-title", of + photo.title));
    const meta = el("div", "ph-meta");
    if (!photo.twin || photo.conf !== "sure") meta.append(conf(photo));
    meta.append(document.createTextNode(` ${photo.date || ""}`));
    cap.append(meta);
    if (photo.caveat) cap.append(el("div", "ph-caveat", photo.caveat));
    cap.append(el("div", "ph-credit", photo.attribution));
    fig.append(cap);
    return fig;
  }

  // Pictures under the period they were made in. The first one with an image stands large. Link cards close the block.
  function pictureBlock(photos, into, first = true) {
    const withImage = photos.filter((p) => p.image && !p.link_only);
    let big = first ? withImage[0] : null;
    for (const [key, title] of GROUPS) {
      const list = withImage.filter((p) => p.group === key);
      if (!list.length) continue;
      if (withImage.length > 1) into.append(el("h4", "", `${title} (${list.length})`));
      const grid = el("div", "ph-grid");
      for (const p of list) {
        grid.append(tile(p, withImage, p === big));
      }
      into.append(grid);
    }
    const cards = photos.filter((p) => p.link_only);
    if (cards.length) {
      into.append(el("h4", "", `More pictures, link only, not ours to copy (${cards.length})`));
      cards.forEach((p) => into.append(linkCard(p)));
    }
  }

  function evidenceCard(e) {
    const card = el("div", "ev");
    const top = el("div", "ev-top");
    top.append(el("span", `ev-kind ${e.kind}`, KIND[e.kind] || e.kind));
    if (e.status !== "viewed") top.append(el("span", "ev-index", "seen in a search index only"));
    if (e.conf !== "sure") top.append(conf(e));
    card.append(top, el("div", "ph-title", e.title));
    card.append(el("div", "ph-meta", [e.date, e.locator, e.source_id].filter(Boolean).join(" · ")));
    if (e.summary) card.append(el("p", "ev-sum", e.summary));
    for (const [text, lang] of [[e.excerpt_zh, "zh"], [e.excerpt_other, ""]]) {
      if (!text) continue;
      const q = el("blockquote", "ev-text", text);
      if (lang) q.lang = lang;
      if (text.length > 160) {
        const d = el("details");
        d.append(el("summary", "", `${text.slice(0, 70).replace(/\s+/g, " ")} …`), q);
        card.append(d);
      } else card.append(q);
    }
    if (e.link) card.append(outLink(e.link, e.rights_class === "free" ? "Source" : `View at ${holderName(e.link)}`));
    return card;
  }

  // Texts, then drawings and plans, then what was dug up, then later studies. A long list folds after a few.
  function evidenceBlock(list, into) {
    const parts = [
      ["Period texts and poems", (e) => e.kind === "poem" || e.kind === "text"],
      ["Described", (e) => e.kind === "description" && e.rights_class === "free"],
      ["Drawings and plans", (e) => e.kind === "drawing" || e.kind === "plan"],
      ["Archaeology", (e) => e.kind === "archaeology"],
      ["Later studies", (e) => e.kind === "description" && e.rights_class !== "free"],
    ];
    for (const [title, test] of parts) {
      const rows = list.filter(test);
      if (!rows.length) continue;
      into.append(el("h4", "", `${title} (${rows.length})`));
      rows.slice(0, 5).forEach((e) => into.append(evidenceCard(e)));
      if (rows.length > 5) {
        const d = el("details", "ev-more");
        d.append(el("summary", "", `${rows.length - 5} more`));
        d.addEventListener("toggle", () => { if (d.open && d.children.length === 1) rows.slice(5).forEach((e) => d.append(evidenceCard(e))); });
        into.append(d);
      }
    }
  }

  function planCard(ref) {
    const card = el("div", "ev plan");
    if (ref.image) {
      const img = el("img", "ph-local");
      img.src = ref.image;
      img.alt = "The plan S01 round this object";
      img.loading = "lazy";
      card.append(img, el("span", "copy", COPY));
    }
    card.append(el("p", "ev-sum", ref.text));
    card.append(outLink(ref.link, "View the plan at Princeton University Art Museum"));
    return card;
  }

  // Folds what is long: rows after the first few wait in a <details> until it opens.
  function foldedList(rows, into, draw, shownFirst = 5) {
    rows.slice(0, shownFirst).forEach((r) => into.append(draw(r)));
    if (rows.length > shownFirst) {
      const d = el("details", "ev-more");
      d.append(el("summary", "", `${rows.length - shownFirst} more`));
      d.addEventListener("toggle", () => { if (d.open && d.children.length === 1) rows.slice(shownFirst).forEach((r) => d.append(draw(r))); });
      into.append(d);
    }
  }

  // Reconstructions by others. Free images large enough to read; everything else a card with author, institution and year. The repair models of 1873-74 are not modern, and stand apart.
  function reconBlock(list, into) {
    into.append(el("p", "bp-warn", NOT_EVIDENCE));
    const modern = list.filter((r) => r.era !== "period"), period = list.filter((r) => r.era === "period");
    const images = modern.filter((r) => r.image && !r.link_only);
    if (images.length) {
      const grid = el("div", "ph-grid");
      images.slice(0, 8).forEach((r) => grid.append(tile(r, images, false)));
      into.append(grid);
    }
    foldedList(modern.filter((r) => !(r.image && !r.link_only)), into, linkCard);
    if (period.length) {
      into.append(el("h4", "", `Card models of the repair of 1873–74, later than 1860 (${period.length})`));
      period.forEach((r) => into.append(linkCard(r)));
    }
  }

  function twinCard(t) {
    const card = el("div", "tw");
    card.append(el("div", "tw-name", t.name));
    card.append(el("div", "ph-meta", [t.place, t.standing === "no" ? "lost" : t.standing === "yes" ? "" : t.standing === "partly" ? "partly standing" : `${t.standing}, not the original`].filter(Boolean).join(" · ")));
    const rel = el("div", "tw-rel");
    rel.append(el("b", "", t.relation), el("span", `conf-grade`, ` confidence ${t.confidence}`));
    if (t.status !== "viewed") rel.append(el("span", "ev-index", "seen in a search index only"));
    card.append(rel);
    t.photos.forEach((p) => { p.twin = t.name; });
    const shown = t.photos.filter((p) => p.image && !p.link_only);
    if (shown.length) {
      const grid = el("div", "ph-grid");
      shown.forEach((p) => grid.append(tile(p, shown, false)));
      card.append(grid);
    }
    t.photos.filter((p) => p.link_only).forEach((p) => card.append(linkCard(p)));
    if (t.tells) card.append(el("p", "ev-sum", t.tells));
    if (t.basis) {
      const d = el("details", "tw-basis");
      d.append(el("summary", "", "Why this pairing"), el("p", "ev-sum", t.basis));
      card.append(d);
    }
    if (t.link) card.append(outLink(t.link, "Source"));
    return card;
  }

  function twinBlock(list, into) {
    into.append(el("p", "bp-warn", NOT_THIS));
    const standing = list.filter((t) => t.standing !== "no"), lost = list.filter((t) => t.standing === "no");
    foldedList(standing, into, twinCard);
    if (lost.length) {
      into.append(el("h4", "", `Named as its model or copy, and now lost (${lost.length})`));
      lost.forEach((t) => into.append(twinCard(t)));
    }
  }

  // What speaks for the set of buildings: fetched from that page, so nothing is written twice.
  function addFallback(page, slot) {
    for (const f of page.fallback || []) {
      if (f.refs_only) { addRefs(page, f, slot); continue; }
      const s = section(f.heading);
      s.className = "bp-fallback";
      const hold = el("p", "bp-line", "Loading…");
      s.append(hold);
      slot.append(s);
      load(f.id).then((other) => {
        if (shown !== page.id) return;
        hold.remove();
        pictureBlock(other.photos || [], s, f.kind !== "garden");
        evidenceBlock(other.evidence || [], s);
        if (other.reconstructions && other.reconstructions.length) {
          s.append(el("h4", "", `Reconstructions by others (${other.reconstructions.length})`));
          reconBlock(other.reconstructions, s);
        }
        if (other.twins && other.twins.length) {
          s.append(el("h4", "", `Surviving comparable buildings, not this building (${other.twins.length})`));
          twinBlock(other.twins, s);
        }
        if (f.kind !== "garden") {
          const ul = el("ul", "bp-links");
          linkTo([f.id, f.name], ul);
          s.append(ul);
        }
      }).catch(() => { hold.textContent = "This evidence could not be loaded."; });
    }
  }

  // Only the reconstructions and comparables of the garden or the class of hall, folded: they speak for many objects and for this one least.
  function addRefs(page, f, slot) {
    const d = el("details", "bp-refs");
    slot.append(d);
    load(f.id).then((other) => {
      if (shown !== page.id) return;
      const recons = other.reconstructions || [], twins = other.twins || [];
      if (!recons.length && !twins.length) { d.remove(); return; }
      d.append(el("summary", "", `${f.heading} (${recons.length + twins.length})`));
      d.addEventListener("toggle", () => {
        if (!d.open || d.children.length > 1) return;
        if (recons.length) { d.append(el("h4", "", `Reconstructions by others (${recons.length})`)); reconBlock(recons, d); }
        if (twins.length) { d.append(el("h4", "", `Comparable buildings (${twins.length})`)); twinBlock(twins, d); }
      });
    }).catch(() => d.remove());
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
    shown = page.id;
    const own = page.photos || [];
    if (own.length) {
      const ph = section(`Pictures of it (${own.length})`);
      pictureBlock(own, ph);
      body.append(ph);
    }
    if (page.photos_inside && page.photos_inside.length) {
      const ph = section(`Pictures of its halls (${page.photos_inside.length})`);
      pictureBlock(page.photos_inside, ph, !own.length);
      body.append(ph);
    }
    if ((page.evidence && page.evidence.length) || page.plan_ref) {
      const ev = section(page.evidence && page.evidence.length ? `Texts and drawings (${page.evidence.length})` : "On the plan");
      evidenceBlock(page.evidence || [], ev);
      if (page.plan_ref) {
        if (page.evidence && page.evidence.length) ev.append(el("h4", "", "On the plan"));
        ev.append(planCard(page.plan_ref));
      }
      body.append(ev);
    }
    if (page.searched) body.append(el("p", "bp-searched", page.searched));
    if (page.reconstructions && page.reconstructions.length) {
      const s = section(`Reconstructions by others (${page.reconstructions.length})`);
      reconBlock(page.reconstructions, s);
      body.append(s);
    }
    if (page.twins && page.twins.length) {
      const s = section(`Surviving comparable buildings, not this building (${page.twins.length})`);
      twinBlock(page.twins, s);
      body.append(s);
    }
    if (page.fallback && page.fallback.length) {
      const slot = el("div", "bp-fallbacks");
      body.append(slot);
      addFallback(page, slot);
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
    shown = null;
    root.hidden = true;
    document.body.classList.remove("panel-open");
  }

  // The larger view. Left and right arrows go through the block's pictures; Esc closes.
  const $ = (id) => document.getElementById(id);
  let box = null;
  function openPhoto(list, n) {
    box = { list, n, back: document.activeElement };
    drawPhoto();
    $("lightbox").hidden = false;
    $("lb-close").focus();
  }

  function drawPhoto() {
    const { list, n } = box, photo = list[n], cap = $("lb-caption"), img = $("lb-img");
    img.src = photo.image;
    img.alt = photo.title;
    cap.textContent = "";
    cap.append(el("h2", "", photo.title));
    const row = (k, v) => { if (v) { const d = el("div", "row"); d.append(el("span", "k", k), el("span", "", v)); cap.append(d); } };
    row("Date", photo.date);
    row("By", photo.creator);
    row("Holder", photo.archive);
    if (photo.era) row("Kind", photo.era === "period" ? "A card model of the repair of 1873–74" : "A modern interpretation, not evidence");
    if (photo.twin) row("Not this building", `It shows ${photo.twin}, a comparable building that stands elsewhere.`);
    row("Identification", photo.of ? `${photo.of[1] || ""} ${photo.of[0]}: ${photo.conf}` : photo.conf);
    row(photo.era ? "As its author states" : "Why", photo.why);
    row("Note", photo.caveat);
    row("Also shows", photo.also_shows);
    row("Camera", photo.camera_note);
    row("Rights", photo.licence);
    row("Credit", photo.attribution);
    cap.append(outLink(photo.source_url, "Source"));
    cap.append(el("div", "count", `${n + 1} of ${list.length}`));
    $("lb-prev").disabled = list.length < 2;
    $("lb-next").disabled = list.length < 2;
  }

  function closePhoto() {
    if (!box) return;
    $("lightbox").hidden = true;
    $("lb-img").removeAttribute("src");
    if (box.back && box.back.focus) box.back.focus();
    box = null;
  }

  function stepPhoto(d) {
    box.n = (box.n + d + box.list.length) % box.list.length;
    drawPhoto();
  }

  $("lb-close").onclick = closePhoto;
  $("lb-prev").onclick = () => stepPhoto(-1);
  $("lb-next").onclick = () => stepPhoto(1);
  $("lightbox").addEventListener("click", (e) => { if (e.target.id === "lightbox" || e.target.id === "lb-stage") closePhoto(); });
  addEventListener("keydown", (e) => {
    if (box) {
      if (e.key === "Escape") { e.stopImmediatePropagation(); closePhoto(); }
      else if (e.key === "ArrowLeft") stepPhoto(-1);
      else if (e.key === "ArrowRight") stepPhoto(1);
    } else if (e.key === "Escape" && !root.hidden) onClose();
  }, true);
  return { load, show, fail, hide };
}
