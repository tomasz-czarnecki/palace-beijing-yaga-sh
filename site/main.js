/** Yuanmingyuan homepage: the placeholders that take their render once it exists, the compare slider (model and plate), a lightbox over the views, and a gentle reveal on scroll. No idle motion: these are pictures of a place that was destroyed. */

const main = document.querySelector('main');
const words = main ? main.dataset : {};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * The placeholders (figure.ph[data-slot]). assets/gallery/manifest.json lists the slots whose picture exists
 * ("ready": ["home-gate-morning", ...]); each is assets/gallery/<slot>.webp. A figure with data-ready="1" takes its file without the manifest.
 * The picture gets the AI label, and its caption's label turns from "to come" to its data-filled text. Without the script the placeholder stays.
 */
async function fillPlaceholders() {
  const slots = [...document.querySelectorAll('figure.ph[data-slot]')];
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
    big.alt = img?.alt || '';
    cap.textContent = fig?.querySelector('h3')?.textContent || '';
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

startReveal();
document.querySelectorAll('[data-cmp]').forEach(startCompare);
if (document.querySelector('a[data-lb]') && 'HTMLDialogElement' in window) startLightbox();
fillPlaceholders();
