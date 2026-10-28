/* COMP3511 Midterm study site — shared behaviour (classic script, works on file://) */
(function () {
  'use strict';
  var LS = window.localStorage;
  function lsGet(k, d) { try { var v = LS.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function lsSet(k, v) { try { LS.setItem(k, JSON.stringify(v)); } catch (e) {} }
  window.SiteStore = { get: lsGet, set: lsSet };

  /* ---------- theme ---------- */
  var theme = lsGet('c3511-theme', null);
  if (!theme) theme = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', theme);

  function ready(fn) { if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }

  ready(function () {
    var tbtn = document.getElementById('theme-btn');
    if (tbtn) {
      tbtn.textContent = theme === 'dark' ? '☀️' : '🌙';
      tbtn.addEventListener('click', function () {
        theme = theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', theme);
        lsSet('c3511-theme', theme);
        tbtn.textContent = theme === 'dark' ? '☀️' : '🌙';
      });
    }
    var mbtn = document.getElementById('menu-btn');
    var sb = document.querySelector('.sidebar');
    if (mbtn && sb) mbtn.addEventListener('click', function () { sb.classList.toggle('open'); });

    highlightCode();
    initToc();
    initSearch();
    initDone();
    initCountdown();
  });

  /* ---------- tiny C highlighter + copy buttons ---------- */
  var KW = /\b(if|else|for|while|do|return|break|continue|switch|case|default|struct|typedef|sizeof|void|static|const|true|false|TRUE|FALSE|NULL)\b/;
  var TY = /\b(int|char|long|short|unsigned|boolean|bool|float|double|pid_t|size_t|ssize_t|pthread_t|pthread_mutex_t|pthread_cond_t|sem_t|semaphore|item|message|atomic_int|mode_t)\b/;
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function hlLine(src) {
    var out = '', re = /(\/\*[\s\S]*?\*\/|\/\/[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+\b|\b[A-Za-z_]\w*\b(?=\s*\()|\b[A-Za-z_]\w*\b)/g, last = 0, m;
    while ((m = re.exec(src))) {
      out += esc(src.slice(last, m.index));
      var t = m[0], cls = null;
      if (t.indexOf('/*') === 0 || t.indexOf('//') === 0) cls = 'tok-com';
      else if (t[0] === '"' || t[0] === "'") cls = 'tok-str';
      else if (/^\d+$/.test(t)) cls = 'tok-num';
      else if (KW.test(t) && t.match(KW)[0] === t) cls = 'tok-kw';
      else if (TY.test(t) && t.match(TY)[0] === t) cls = 'tok-ty';
      else if (/^[A-Za-z_]\w*$/.test(t) && /^\s*\(/.test(src.slice(m.index + t.length))) cls = 'tok-fn';
      out += cls ? '<span class="' + cls + '">' + esc(t) + '</span>' : esc(t);
      last = m.index + t.length;
    }
    return out + esc(src.slice(last));
  }
  function highlightCode() {
    var blocks = document.querySelectorAll('pre.code');
    for (var i = 0; i < blocks.length; i++) {
      var pre = blocks[i], code = pre.querySelector('code');
      var lang = pre.getAttribute('data-lang') || '';
      if (code && (lang === 'c' || lang === '')) {
        var txt = code.textContent;
        if (lang === 'c' || /[;{}]/.test(txt)) code.innerHTML = hlLine(txt);
      }
      var b = document.createElement('button');
      b.className = 'btn copy'; b.textContent = 'copy';
      (function (pre, b) {
        b.addEventListener('click', function () {
          var t = pre.querySelector('code').textContent;
          if (navigator.clipboard) navigator.clipboard.writeText(t);
          b.textContent = 'copied ✓'; setTimeout(function () { b.textContent = 'copy'; }, 1200);
        });
      })(pre, b);
      pre.appendChild(b);
    }
  }

  /* ---------- TOC scrollspy ---------- */
  function initToc() {
    var links = document.querySelectorAll('.toc a');
    if (!links.length) return;
    var heads = [];
    for (var i = 0; i < links.length; i++) {
      var id = links[i].getAttribute('href').slice(1);
      var h = document.getElementById(id);
      if (h) heads.push([h, links[i]]);
    }
    function spy() {
      var y = window.scrollY + 90, cur = null;
      for (var i = 0; i < heads.length; i++) { if (heads[i][0].offsetTop <= y) cur = heads[i][1]; }
      for (var j = 0; j < links.length; j++) links[j].classList.remove('active');
      if (cur) {
        cur.classList.add('active');
        var toc = document.querySelector('.toc');
        if (toc && (cur.offsetTop < toc.scrollTop || cur.offsetTop > toc.scrollTop + toc.clientHeight - 40)) toc.scrollTop = cur.offsetTop - 80;
      }
    }
    window.addEventListener('scroll', spy, { passive: true });
    spy();
  }

  /* ---------- search ---------- */
  function norm(s) { return (s || '').toLowerCase(); }
  function initSearch() {
    var inp = document.getElementById('search');
    var box = document.getElementById('search-results');
    if (!inp || !box || !window.SEARCH_INDEX) return;
    var idx = window.SEARCH_INDEX, sel = -1, items = [];
    function snippet(text, terms) {
      var lt = norm(text), pos = -1;
      for (var i = 0; i < terms.length && pos < 0; i++) pos = lt.indexOf(terms[i]);
      var start = Math.max(0, pos - 40), s = text.slice(start, start + 150);
      s = esc(s);
      for (var j = 0; j < terms.length; j++) {
        if (!terms[j]) continue;
        var rx = new RegExp('(' + terms[j].replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
        s = s.replace(rx, '<mark>$1</mark>');
      }
      return (start > 0 ? '…' : '') + s + '…';
    }
    function run() {
      var q = norm(inp.value.trim());
      if (q.length < 2) { box.classList.remove('open'); box.innerHTML = ''; return; }
      var terms = q.split(/\s+/).filter(Boolean);
      var scored = [];
      for (var i = 0; i < idx.length; i++) {
        var e = idx[i], t = norm(e.t), x = norm(e.x), sc = 0, ok = true;
        for (var k = 0; k < terms.length; k++) {
          var term = terms[k], inT = t.indexOf(term) >= 0, inX = x.indexOf(term) >= 0;
          if (!inT && !inX) { ok = false; break; }
          sc += (inT ? 10 : 0) + (inX ? 2 : 0);
          if (t.indexOf(term) === 0) sc += 5;
        }
        if (ok) { sc += (e.w || 0); scored.push([sc, e]); }
      }
      scored.sort(function (a, b) { return b[0] - a[0]; });
      items = scored.slice(0, 30);
      sel = -1;
      if (!items.length) { box.innerHTML = '<a><span class="sr-snip">冇結果 No results</span></a>'; box.classList.add('open'); return; }
      var h = '';
      for (var j = 0; j < items.length; j++) {
        var e2 = items[j][1];
        h += '<a href="' + e2.u + '"><span class="sr-title">' + esc(e2.t) + '</span><span class="sr-page">' + esc(e2.p) + '</span>' +
             '<div class="sr-snip">' + snippet(e2.x, terms) + '</div></a>';
      }
      box.innerHTML = h; box.classList.add('open');
    }
    inp.addEventListener('input', run);
    inp.addEventListener('focus', run);
    inp.addEventListener('keydown', function (ev) {
      var as = box.querySelectorAll('a[href]');
      if (ev.key === 'ArrowDown') { sel = Math.min(as.length - 1, sel + 1); ev.preventDefault(); }
      else if (ev.key === 'ArrowUp') { sel = Math.max(0, sel - 1); ev.preventDefault(); }
      else if (ev.key === 'Enter') { if (as[sel < 0 ? 0 : sel]) window.location.href = as[sel < 0 ? 0 : sel].getAttribute('href'); return; }
      else if (ev.key === 'Escape') { box.classList.remove('open'); inp.blur(); return; }
      for (var i = 0; i < as.length; i++) as[i].classList.toggle('active', i === sel);
      if (as[sel]) as[sel].scrollIntoView({ block: 'nearest' });
    });
    document.addEventListener('click', function (ev) { if (!box.contains(ev.target) && ev.target !== inp) box.classList.remove('open'); });
    document.addEventListener('keydown', function (ev) {
      if ((ev.key === '/' || (ev.key === 'k' && (ev.ctrlKey || ev.metaKey))) && document.activeElement !== inp &&
          !/input|textarea|select/i.test(document.activeElement.tagName)) { ev.preventDefault(); inp.focus(); inp.select(); }
    });
  }

  /* ---------- reviewed / done markers ---------- */
  function initDone() {
    var done = lsGet('c3511-done', {});
    var page = document.body.getAttribute('data-page');
    var btn = document.getElementById('mark-done');
    if (btn && page) {
      function paint() { btn.textContent = done[page] ? '✅ 已溫完 Reviewed' : '☐ 標記為已溫 Mark reviewed'; btn.classList.toggle('primary', !!done[page]); }
      paint();
      btn.addEventListener('click', function () { done[page] = !done[page]; lsSet('c3511-done', done); paint(); paintNav(); });
    }
    function paintNav() {
      var as = document.querySelectorAll('.sidebar a[data-page]');
      for (var i = 0; i < as.length; i++) {
        var p = as[i].getAttribute('data-page'), dot = as[i].querySelector('.done-dot');
        if (dot) dot.textContent = done[p] ? '✓' : '';
      }
      var cards = document.querySelectorAll('.card[data-page]');
      for (var j = 0; j < cards.length; j++) cards[j].classList.toggle('done', !!done[cards[j].getAttribute('data-page')]);
    }
    paintNav();
  }

  /* ---------- countdown ---------- */
  function initCountdown() {
    var el = document.getElementById('countdown');
    if (!el) return;
    var target = new Date('2026-10-29T20:00:00+08:00').getTime();
    function tick() {
      var d = target - Date.now();
      if (d <= 0) { el.textContent = '考試進行中 / 已完成 — 加油！'; return; }
      var h = Math.floor(d / 3600000), m = Math.floor(d % 3600000 / 60000), s = Math.floor(d % 60000 / 1000);
      el.textContent = '距離開考 ' + h + ' 小時 ' + (m < 10 ? '0' : '') + m + ' 分 ' + (s < 10 ? '0' : '') + s + ' 秒';
    }
    tick(); setInterval(tick, 1000);
  }
})();
