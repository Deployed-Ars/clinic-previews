/* Shared behaviour. No dependencies. Every feature degrades gracefully without JS. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // header state + mobile menu
  const header = $('[data-header]'), banner = $('.concept-banner');
  // the fixed header sits below the concept banner and slides up to the top as the banner scrolls away
  const place = () => { if (header && banner) header.style.setProperty('--hy', Math.max(0, banner.offsetHeight - scrollY) + 'px'); };
  const onScroll = () => { header && header.toggleAttribute('data-scrolled', scrollY > 24); place(); };
  onScroll(); addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', place);
  const burger = $('[data-burger]'), nav = $('#nav');
  if (burger && nav) {
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open);
      header.toggleAttribute('data-open', open);
    });
    nav.addEventListener('click', e => { if (e.target.closest('a')) { nav.classList.remove('open'); burger.setAttribute('aria-expanded', false); header.removeAttribute('data-open'); } });
  }

  // reveal on scroll
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((es) => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { threshold: .12, rootMargin: '0px 0px -40px 0px' }) : null;
  $$('.reveal').forEach(el => io ? io.observe(el) : el.classList.add('in'));
  // safety net: never leave content hidden
  setTimeout(() => $$('.reveal:not(.in)').forEach(el => { const r = el.getBoundingClientRect(); if (r.top < innerHeight) el.classList.add('in'); }), 1500);

  // counters: HTML already holds the final value, so a failure can never show 0
  if (!reduce && io) {
    const co = new IntersectionObserver((es) => es.forEach(e => {
      if (!e.isIntersecting) return; co.unobserve(e.target);
      const el = e.target, end = parseFloat(el.dataset.count), t0 = performance.now(), dur = 1400;
      const dec = (String(el.dataset.count).split('.')[1] || '').length;
      const step = now => {
        const k = Math.min(1, (now - t0) / dur), v = end * (1 - Math.pow(1 - k, 3));
        el.textContent = v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
        if (k < 1) requestAnimationFrame(step); else el.textContent = end.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
      };
      requestAnimationFrame(step);
    }), { threshold: .6 });
    $$('[data-count]').forEach(el => co.observe(el));
  }

  // before / after sliders
  $$('[data-ba]').forEach(f => {
    const r = $('input[type=range]', f);
    const set = () => f.style.setProperty('--pos', r.value + '%');
    r.addEventListener('input', set); set();
  });

  // carousels
  $$('[data-carousel]').forEach(c => {
    const tr = $('.car-track', c), step = () => (tr.firstElementChild?.getBoundingClientRect().width || 300) + 22;
    const dir = getComputedStyle(c).direction === 'rtl' ? -1 : 1;
    $('[data-next]', c)?.addEventListener('click', () => tr.scrollBy({ left: step() * dir, behavior: 'smooth' }));
    $('[data-prev]', c)?.addEventListener('click', () => tr.scrollBy({ left: -step() * dir, behavior: 'smooth' }));
  });

  // tabs
  $$('[data-tabs]').forEach(w => {
    const tabs = $$('[role=tab]', w), panels = $$('[role=tabpanel]', w);
    const show = i => { tabs.forEach((t, j) => { t.setAttribute('aria-selected', i === j); t.tabIndex = i === j ? 0 : -1; }); panels.forEach((p, j) => p.hidden = i !== j); };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => show(i));
      t.addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const n = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length; show(n); tabs[n].focus(); } });
    });
    show(0);
  });

  // WhatsApp widget
  const wa = $('[data-wa]');
  if (wa) {
    const b = $('[data-wa-toggle]', wa), pop = $('#wa-pop', wa);
    b.addEventListener('click', () => { pop.hidden = !pop.hidden; b.setAttribute('aria-expanded', !pop.hidden); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { pop.hidden = true; b.setAttribute('aria-expanded', false); } });
  }

  // forms hand off to WhatsApp (static site, no backend)
  $$('[data-wa-form]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault();
    if (f.dataset.live !== 'true') { // concept demo: never contact the clinic's real number
      const st = $('.form-status', f); if (st) st.textContent = f.dataset.demoNote;
      return;
    }
    const d = new FormData(f), num = f.dataset.waForm;
    const msg = (f.dataset.msg || '').replace('{n}', d.get('n') || '').replace('{p}', d.get('p') || '').replace('{s}', d.get('s') || '-').replace('{m}', d.get('m') || '').trim();
    window.open(num ? `https://wa.me/${num}?text=${encodeURIComponent(msg)}` : `mailto:?body=${encodeURIComponent(msg)}`, '_blank', 'noopener');
  }));
})();
