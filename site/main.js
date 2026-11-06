/** Yuanmingyuan homepage: the full-screen hero carousel of AI pictures, the placeholders that take their render once it exists, the compare slider (model and plate), a lightbox over the views, and a gentle reveal on scroll. The carousel's slow crossfade and zoom are the only motion that runs by itself, and never with reduced motion: these are pictures of a place that was destroyed. */

const main = document.querySelector('main');
const words = main ? main.dataset : {};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * The placeholders (figure.ph[data-slot]). assets/gallery/manifest.json lists the slots whose picture exists
 * ("ready": ["home-gate-morning", ...]); each is assets/gallery/<slot>.webp. A figure with data-ready="1" takes its file without the manifest.
 * The picture gets the AI label, and its caption's label turns from "to come" to its data-filled text. Without the script the placeholder stays.
 */
async function fillPlaceholders() {
  const slots = [...document.querySelectorAll('figure.ph[data-slot]:not(.ph-filled)')]; // tools/home_gallery.py writes the filled ones into the page
  if (!slots.length || !words.gallery) return;
  let ready = new Set(slots.filter((f) => f.dataset.ready === '1').map((f) => f.dataset.slot));
  try {
    const r = await fetch(words.gallery + 'manifest.json', { cache: 'no-cache' });
    if (r.ok) (await r.json()).ready?.forEach((s) => ready.add(s));
  } catch { /* no manifest: placeholders stay */ }
  for (const fig of slots) {
    if (!ready.has(fig.dataset.slot)) continue;
    const frame = fig.querySelector('.ph-frame');
    const img = new Image();
    img.alt = fig.dataset.alt || '';
    img.loading = 'lazy'; // in the frame at once, so the browser fetches it only near the viewport
    img.decoding = 'async';
    img.addEventListener('load', () => {
      const link = document.createElement('a');
      link.className = 'gv-pic ph-link';
      link.href = img.src;
      link.dataset.lb = '';
      link.setAttribute('aria-label', fig.querySelector('h3')?.textContent || '');
      frame.replaceWith(link);
      link.append(frame);
      const tag = document.createElement('span');
      tag.className = 'pic-tag is-ai';
      tag.textContent = words.ai || 'AI visualisation';
      frame.append(tag);
      fig.classList.add('ph-filled');
      const label = fig.querySelector('.gv-label[data-filled]');
      if (label) label.textContent = label.dataset.filled;
    }, { once: true });
    img.src = `${words.gallery}${fig.dataset.slot}.webp`;
    frame.append(img);
  }
}

/** The compare slider: the model on top, clipped at --pos. The range input covers the box, so a drag, a click and the keys all move it. */
function startCompare(box) {
  const input = box.querySelector('input');
  const set = () => box.style.setProperty('--pos', `${input.value}%`);
  input.addEventListener('input', set);
  input.addEventListener('pointerdown', () => box.classList.add('cmp-dragging'));
  input.addEventListener('pointerup', () => box.classList.remove('cmp-dragging'));
  set();
}

/** One <dialog> for every picture link marked data-lb. Without the script the link simply opens the large file. */
function startLightbox() {
  const dlg = document.createElement('dialog');
  dlg.className = 'lb';
  dlg.innerHTML = `<div class="lb-stage"><img alt=""><p class="lb-cap"></p></div><button class="lb-close" type="button" aria-label="${words.lbClose || 'Close'}">×</button>`;
  document.body.append(dlg);
  const big = dlg.querySelector('img');
  const cap = dlg.querySelector('.lb-cap');
  dlg.querySelector('.lb-close').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.classList.contains('lb-stage')) dlg.close(); });
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[data-lb]');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    const fig = a.closest('figure');
    const img = a.querySelector('img');
    big.src = a.href;
    big.alt = a.dataset.lbAlt || img?.alt || '';
    const title = a.dataset.lbCap || fig?.querySelector('h3')?.textContent || '';
    // an AI picture keeps its label in the lightbox too
    cap.textContent = 'lbAi' in a.dataset && words.aiNote ? `${title} ${words.aiNote}` : title;
    dlg.showModal();
  });
}

/** Reveal on scroll. What is already in view shows at once, so nothing above the fold ever blinks. */
function startReveal() {
  const items = [...document.querySelectorAll('.reveal')];
  if (!items.length || reduced || !('IntersectionObserver' in window)) return;
  document.documentElement.classList.add('js-reveal');
  const seen = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); seen.unobserve(e.target); }
  }, { rootMargin: '0px 0px -8% 0px' });
  for (const el of items) {
    if (el.getBoundingClientRect().top < innerHeight) el.classList.add('is-in');
    else seen.observe(el);
  }
}

/**
 * The hero (tools/home_gallery.py writes its slides, captions and locators). Slide 1 is in the page; the others' pictures sit in
 * inert <template>s and only the one after the slide shown comes out, so a visitor fetches the next picture and no more.
 * About 8 s a picture: the progress line under the dots is the clock, so a pause (the button, hover, focus on the controls,
 * a hidden tab, the hero out of view) holds the line, the zoom and the turn together. No autoplay with reduced motion.
 */
function startHero() {
  const root = document.querySelector('.hero-full');
  const box = root?.querySelector('.hero-show');
  const slides = box ? [...box.querySelectorAll('.hero-slide')] : [];
  if (slides.length < 2) return;
  const DWELL = 8000;
  const TOUCH_HOLD = 12000;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const caps = [...root.querySelectorAll('.hero-cap')];
  const locs = [...root.querySelectorAll('.hero-loc')];
  const nav = root.querySelector('.hero-nav');
  const dots = [...nav.querySelectorAll('.hero-dot')];
  const pause = nav.querySelector('.hero-pause');
  const clock = nav.querySelector('.hero-progress i');
  const arrows = [...box.querySelectorAll('.hero-arrow')];
  const status = box.querySelector('.hero-status');
  const n = slides.length;
  const ready = slides.map((s, i) => (i === 0 ? Promise.resolve() : null));
  const held = new Set(); // why it may not turn now: hover, focus, touch, hidden, away
  let stopped = motion.matches; // the visitor's choice (the button), or reduced motion
  let started = false;
  let at = 0;
  let want = 0;
  let touchTimer = 0;

  // A slide's picture comes out of its template once; the promise settles when it is decoded.
  function ensure(i) {
    i = (i + n) % n;
    if (ready[i]) return ready[i];
    const tpl = slides[i].querySelector('template.hero-slide-tpl');
    const pic = tpl.content.firstElementChild.cloneNode(true);
    tpl.replaceWith(pic);
    const img = pic.querySelector('img');
    ready[i] = img.decode ? img.decode().catch(() => {}) : Promise.resolve();
    return ready[i];
  }

  function still() {
    root.toggleAttribute('data-still', stopped || held.size > 0);
  }

  // Restart the clock for the slide shown; its animationend turns the slide.
  function run() {
    root.removeAttribute('data-run');
    if (!started || stopped) return;
    void clock.offsetWidth;
    root.setAttribute('data-run', '');
  }

  function setPause() {
    pause.dataset.state = stopped ? 'stopped' : 'playing';
    pause.setAttribute('aria-label', stopped ? pause.dataset.play : pause.dataset.pause);
    still();
  }

  // The new slide fades in over the old one, which stays whole underneath until it is covered.
  function show(i, announce) {
    slides.forEach((slide, j) => {
      slide.classList.toggle('is-under', j === at && j !== i);
      slide.classList.toggle('is-on', j === i);
      slide.inert = j !== i;
    });
    [caps, locs].forEach((list) => list.forEach((el, j) => {
      el.classList.toggle('is-on', j === i);
      el.toggleAttribute('aria-hidden', j !== i);
      el.querySelectorAll('a').forEach((a) => (j === i ? a.removeAttribute('tabindex') : a.setAttribute('tabindex', '-1')));
    }));
    dots.forEach((dot, j) => (j === i ? dot.setAttribute('aria-current', 'true') : dot.removeAttribute('aria-current')));
    at = i;
    root.dataset.at = String(i);
    if (announce) status.textContent = `${slides[i].getAttribute('aria-label')}: ${slides[i].dataset.title}`;
    run();
    if (started) ensure(i + 1);
  }

  function go(i, announce) {
    want = (i + n) % n;
    const target = want;
    ensure(target).then(() => { if (want === target && target !== at) show(target, announce); });
  }

  function hold(why, on) {
    if (on) held.add(why); else held.delete(why);
    still();
  }

  clock.addEventListener('animationend', (e) => {
    if (e.animationName !== 'hero-progress') return;
    if (document.querySelector('dialog[open]')) run();
    else go(at + 1, false);
  });

  nav.hidden = false;
  arrows.forEach((a) => { a.hidden = false; });
  root.style.setProperty('--dwell', `${DWELL}ms`);
  root.dataset.at = '0';
  setPause();
  box.querySelector('.hero-prev').addEventListener('click', () => go(want - 1, true));
  box.querySelector('.hero-next').addEventListener('click', () => go(want + 1, true));
  dots.forEach((dot, i) => dot.addEventListener('click', () => go(i, true)));
  pause.addEventListener('click', () => {
    stopped = !stopped;
    setPause();
    if (!stopped && !root.hasAttribute('data-run')) run();
  });
  const inCopy = (e) => e.target.closest('.hero-copy');
  box.addEventListener('keydown', (e) => {
    if ((e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') || inCopy(e)) return;
    e.preventDefault();
    go(want + (e.key === 'ArrowRight' ? 1 : -1), true);
  });

  // A clear sideways stroke over the picture turns it; an upright one stays a page scroll (touch-action in the CSS).
  let down = null;
  box.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'touch') {
      clearTimeout(touchTimer);
      hold('touch', true);
    }
    down = e.button || e.target.closest('a, button, .hero-copy, .hero-caps') ? null : { x: e.clientX, y: e.clientY };
  }, { passive: true });
  const lift = (e) => { if (e.pointerType === 'touch') touchTimer = setTimeout(() => hold('touch', false), TOUCH_HOLD); };
  box.addEventListener('pointerup', (e) => {
    lift(e);
    if (!down) return;
    const dx = e.clientX - down.x;
    const dy = e.clientY - down.y;
    down = null;
    if (Math.abs(dx) > 48 && Math.abs(dx) > 1.5 * Math.abs(dy)) go(want + (dx < 0 ? 1 : -1), true);
  });
  box.addEventListener('pointercancel', (e) => { down = null; lift(e); });
  box.addEventListener('pointerover', (e) => { if (e.pointerType === 'mouse') hold('hover', !!e.target.closest('.hero-nav, .hero-arrow, .hero-caps, .hero-where')); });
  box.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') hold('hover', false); });
  box.addEventListener('focusin', (e) => hold('focus', !inCopy(e)));
  box.addEventListener('focusout', (e) => { if (!box.contains(e.relatedTarget)) hold('focus', false); });
  document.addEventListener('visibilitychange', () => hold('hidden', document.hidden));
  motion.addEventListener('change', () => { stopped = motion.matches; setPause(); run(); });
  if ('IntersectionObserver' in window) new IntersectionObserver((seen) => hold('away', !seen.at(-1).isIntersecting)).observe(box);

  // After load, on idle: slide 1 may take its 3840 (wide, high-density screens), the next slide comes out, the clock starts.
  const begin = () => {
    if (started) return;
    started = true;
    const first = slides[0].querySelector('img[data-full]');
    // only where the 3840 can win, so no other screen re-picks (and, without a cache, fetches again) the file it has
    if (first && innerWidth * devicePixelRatio > 2560 && first.currentSrc.includes('-2560.')) first.srcset += `, ${first.dataset.full}`;
    ensure(at + 1);
    run();
  };
  const idle = () => (window.requestIdleCallback ? requestIdleCallback(begin, { timeout: 2500 }) : setTimeout(begin, 600));
  if (document.readyState === 'complete') idle();
  else window.addEventListener('load', idle, { once: true });
}

startHero();
startReveal();
document.querySelectorAll('[data-cmp]').forEach(startCompare);
if (document.querySelector('a[data-lb]') && 'HTMLDialogElement' in window) startLightbox();
fillPlaceholders();
