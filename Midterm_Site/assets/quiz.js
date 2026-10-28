/* MC quiz page — uses window.QUIZ = [{id, ch, topic, src, kind:'past'|'new', stem, opts:[html], ans:'C', alt:'D'|null, exp}] */
(function () {
  'use strict';
  function ready(fn) { if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }
  ready(function () {
    var root = document.getElementById('quiz-app');
    if (!root || !window.QUIZ) return;
    var Q = window.QUIZ, store = window.SiteStore;
    var hist = store.get('c3511-quiz', {});          // id -> 'right' | 'wrong'
    var state = { chs: {}, kinds: { past: true, new: true }, mode: 'all', order: 'paper' };
    var CHS = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6'];
    CHS.forEach(function (c) { state.chs[c] = true; });

    root.innerHTML =
      '<div class="filters" id="qf-ch"></div>' +
      '<div class="filters" id="qf-kind"></div>' +
      '<div class="quiz-bar">' +
        '<select id="q-mode" class="btn"><option value="all">全部題目 All</option><option value="unanswered">未做 Unanswered</option><option value="wrong">錯題 Wrong only</option></select>' +
        '<select id="q-order" class="btn"><option value="paper">按試卷次序 By paper</option><option value="ch">按章節 By chapter</option><option value="random">隨機 Random</option></select>' +
        '<button class="btn" id="q-reveal">顯示全部答案 Reveal all</button>' +
        '<button class="btn" id="q-reset">重設紀錄 Reset</button>' +
        '<span class="quiz-stats" id="q-stats"></span>' +
      '</div>' +
      '<div id="q-list"></div>';

    function chip(container, label, on, fn) {
      var c = document.createElement('span');
      c.className = 'chip' + (on ? ' on' : ''); c.textContent = label;
      c.addEventListener('click', function () { var v = fn(); c.classList.toggle('on', v); render(); });
      container.appendChild(c);
    }
    var fch = document.getElementById('qf-ch'), fk = document.getElementById('qf-kind');
    CHS.forEach(function (c) {
      chip(fch, c.toUpperCase().replace('CH', 'Ch'), true, function () { state.chs[c] = !state.chs[c]; return state.chs[c]; });
    });
    chip(fk, '歷屆 Past papers', true, function () { state.kinds.past = !state.kinds.past; return state.kinds.past; });
    chip(fk, '新練習 New practice', true, function () { state.kinds['new'] = !state.kinds['new']; return state.kinds['new']; });
    document.getElementById('q-mode').addEventListener('change', function (e) { state.mode = e.target.value; render(); });
    document.getElementById('q-order').addEventListener('change', function (e) { state.order = e.target.value; render(); });
    document.getElementById('q-reset').addEventListener('click', function () {
      if (confirm('清除所有作答紀錄？Clear all quiz history?')) { hist = {}; store.set('c3511-quiz', hist); render(); }
    });
    document.getElementById('q-reveal').addEventListener('click', function () {
      var els = document.querySelectorAll('.qexp'); for (var i = 0; i < els.length; i++) els[i].classList.add('show');
      var items = document.querySelectorAll('.qitem');
      for (var j = 0; j < items.length; j++) markAnswer(items[j], null);
    });

    function stats() {
      var r = 0, w = 0;
      for (var k in hist) { if (hist[k] === 'right') r++; else if (hist[k] === 'wrong') w++; }
      document.getElementById('q-stats').textContent = '✔ ' + r + '   ✘ ' + w + '   / ' + Q.length + ' 題';
    }

    function markAnswer(item, chosen) {
      var q = item._q, lis = item.querySelectorAll('.qopts li');
      for (var i = 0; i < lis.length; i++) {
        var L = lis[i].getAttribute('data-l');
        lis[i].classList.add('locked');
        if (L === q.ans || (q.alt && L === q.alt)) lis[i].classList.add('correct');
        if (chosen && L === chosen && L !== q.ans && L !== q.alt) lis[i].classList.add('wrong');
      }
      item.querySelector('.qexp').classList.add('show');
    }

    function render() {
      var list = Q.filter(function (q) {
        if (!state.chs[q.ch]) return false;
        if (!state.kinds[q.kind]) return false;
        if (state.mode === 'wrong' && hist[q.id] !== 'wrong') return false;
        if (state.mode === 'unanswered' && hist[q.id]) return false;
        return true;
      });
      if (state.order === 'ch') list.sort(function (a, b) { return a.ch < b.ch ? -1 : a.ch > b.ch ? 1 : 0; });
      else if (state.order === 'random') {
        for (var i = list.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = list[i]; list[i] = list[j]; list[j] = t; }
      }
      var box = document.getElementById('q-list');
      box.innerHTML = list.length ? '' : '<p>冇符合條件嘅題目。No questions match the filters.</p>';
      list.forEach(function (q, n) {
        var d = document.createElement('div');
        d.className = 'qitem'; d.id = q.id; d._q = q;
        var opts = q.opts.map(function (o, k) {
          var L = String.fromCharCode(65 + k);
          return '<li data-l="' + L + '"><b>' + L + '.</b> ' + o + '</li>';
        }).join('');
        var st = hist[q.id] === 'right' ? ' <span class="ok">✔</span>' : hist[q.id] === 'wrong' ? ' <span class="no">✘</span>' : '';
        d.innerHTML =
          '<div class="qhead"><span class="qid">' + (n + 1) + '. ' + q.id + '</span><span class="qtopic">' + q.topic + '</span>' +
          '<span class="badge ' + q.kind + '">' + (q.kind === 'past' ? '歷屆' : '新題') + '</span><span class="qch">' + q.ch.toUpperCase() + '</span>' + st + '</div>' +
          '<div class="qstem">' + q.stem + '</div><ul class="qopts">' + opts + '</ul>' +
          '<div class="qexp"><b>Answer: ' + q.ans + (q.alt ? ' (also ' + q.alt + ')' : '') + '</b><div>' + q.exp + '</div></div>';
        var lis = d.querySelectorAll('.qopts li');
        for (var i = 0; i < lis.length; i++) {
          lis[i].addEventListener('click', function () {
            if (this.classList.contains('locked')) return;
            var L = this.getAttribute('data-l');
            var right = (L === q.ans || (q.alt && L === q.alt));
            hist[q.id] = right ? 'right' : 'wrong';
            store.set('c3511-quiz', hist);
            markAnswer(d, L);
            stats();
          });
        }
        box.appendChild(d);
      });
      stats();
      if (window.location.hash) { var el = document.getElementById(window.location.hash.slice(1)); if (el) el.scrollIntoView(); }
    }
    render();
  });
})();
