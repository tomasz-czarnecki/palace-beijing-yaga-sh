/** Yuanmingyuan homepage: the album leaf rises into place once. No idle motion: this is an archive painting of a place that was destroyed. */

const leaf = document.querySelector('.hero-figure');

if (leaf && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  leaf.style.transform = 'translateY(32px)';
  leaf.style.opacity = '0';
  requestAnimationFrame(() => requestAnimationFrame(() => {
    leaf.style.transition = 'transform 1.2s cubic-bezier(.16,.8,.24,1), opacity .9s ease';
    leaf.style.transform = 'none';
    leaf.style.opacity = '1';
  }));
}
