/* ══════════════════════════════════════════
   steps.js — Sidebar step scroll tracker
══════════════════════════════════════════ */
function initSteps() {
  const stepEls = document.querySelectorAll('.step');
  const sections = [
    { el: document.getElementById('sec-1'), n: 1 },
    { el: document.getElementById('sec-2'), n: 2 },
    { el: document.getElementById('sec-3'), n: 3 },
    { el: document.getElementById('sec-4'), n: 4 },
  ].filter(s => s.el);

  function sync() {
    let cur = 1;
    sections.forEach(({ el, n }) => {
      if (el.getBoundingClientRect().top < window.innerHeight * 0.55) cur = n;
    });
    stepEls.forEach(s => {
      const n = +s.dataset.step;
      s.classList.toggle('active', n === cur);
      s.classList.toggle('done',   n < cur);
    });
  }

  sync();
  window.addEventListener('scroll', sync, { passive: true });
}
