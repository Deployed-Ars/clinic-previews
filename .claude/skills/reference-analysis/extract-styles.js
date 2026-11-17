// Run in the page via javascript_tool. Returns a compact style profile.
(() => {
  const cs = (el) => getComputedStyle(el);
  const hex = (c) => {
    // Only legacy rgb()/rgba() is parsed; oklab()/color() etc. are returned raw (shortened) rather than mangled.
    if (!/^rgba?\(/.test(c)) return c === 'transparent' ? null : c.slice(0, 40);
    const m = c.match(/[\d.]+/g);
    if (!m || (m[3] !== undefined && +m[3] === 0)) return null;
    return '#' + m.slice(0, 3).map(n => Math.round(+n).toString(16).padStart(2, '0')).join('');
  };
  const count = (map, k) => { if (k) map[k] = (map[k] || 0) + 1; };
  const bg = {}, fg = {}, fonts = {}, radius = {}, shadows = {};
  const all = [...document.querySelectorAll('body *')].slice(0, 4000);
  for (const el of all) {
    const s = cs(el);
    if (s.display === 'none' || s.visibility === 'hidden') continue;
    count(bg, hex(s.backgroundColor));
    if (el.childNodes.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) {
      count(fg, hex(s.color));
      count(fonts, s.fontFamily.split(',')[0].replace(/["']/g, '').trim());
    }
    if (s.borderRadius !== '0px') count(radius, s.borderRadius);
    if (s.boxShadow !== 'none') count(shadows, s.boxShadow.slice(0, 60));
  }
  const top = (m, n = 8) => Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, n);
  const heading = (t) => { const e = document.querySelector(t); if (!e) return null; const s = cs(e);
    return { text: e.textContent.trim().slice(0, 80), font: s.fontFamily.split(',')[0], size: s.fontSize, weight: s.fontWeight, lh: s.lineHeight, ls: s.letterSpacing, color: hex(s.color) }; };
  const buttons = [...document.querySelectorAll('a,button')]
    .filter(e => /book|reserve|request|appointment|consult|contact|whatsapp/i.test(e.textContent))
    .slice(0, 5).map(e => { const s = cs(e); return { text: e.textContent.trim().slice(0, 40), bg: hex(s.backgroundColor), color: hex(s.color), radius: s.borderRadius, padding: s.padding, font: s.fontSize + '/' + s.fontWeight }; });
  const sections = [...document.querySelectorAll('header,nav,section,footer,main > div')]
    .map(e => ({ tag: e.tagName.toLowerCase(), id: e.id || null, h: (e.querySelector('h1,h2,h3') || {}).textContent?.trim().slice(0, 60) || null, h_px: Math.round(e.getBoundingClientRect().height) }))
    .filter(x => x.h_px > 40);
  return {
    title: document.title, lang: document.documentElement.lang, dir: document.dir || document.documentElement.dir,
    fonts: top(fonts, 5), bgColors: top(bg), textColors: top(fg), radius: top(radius, 4), shadows: top(shadows, 3),
    h1: heading('h1'), h2: heading('h2'), body: heading('p'), buttons, sections,
    sticky: [...document.querySelectorAll('header,nav,div')].some(e => cs(e).position === 'fixed' && e.getBoundingClientRect().top < 5),
    fixedWidgets: [...document.querySelectorAll('*')].filter(e => cs(e).position === 'fixed').slice(0, 8).map(e => (e.id || e.className || e.tagName).toString().slice(0, 40)),
    googleFonts: [...document.querySelectorAll('link[href*="fonts.g"]')].map(l => l.href),
  };
})()
