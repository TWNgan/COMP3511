/* Small exam calculators for the Tools page */
(function () {
  'use strict';
  function $(id) { return document.getElementById(id); }
  function num(id) { return parseFloat($(id).value); }
  function r4(x) { return Math.round(x * 10000) / 10000; }
  function ready(fn) { if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }

  ready(function () {
    if (!$('calc-amdahl')) return;

    function amdahl() {
      var mode = $('am-mode').value, S = num('am-s'), N = num('am-n'), out;
      if (mode === 'parallel') S = 1 - S;
      if (isNaN(S) || isNaN(N) || N <= 0) { $('am-out').textContent = '請輸入數字'; return; }
      var sp = 1 / (S + (1 - S) / N);
      out = 'S (serial) = ' + r4(S) + ', N = ' + N + '\n' +
            'speedup ≤ 1 / (S + (1 − S)/N) = 1 / (' + r4(S) + ' + ' + r4(1 - S) + '/' + N + ')\n' +
            '        = 1 / ' + r4(S + (1 - S) / N) + ' = ' + r4(sp) + '\n' +
            'limit N → ∞ : 1/S = ' + (S > 0 ? r4(1 / S) : '∞');
      $('am-out').textContent = out;
    }
    function amdahlRev() {
      var X = num('amr-x'), N = num('amr-n');
      if (isNaN(X) || isNaN(N) || N <= 1 || X <= 0) { $('amr-out').textContent = '請輸入數字（N > 1）'; return; }
      var S = (1 / X - 1 / N) / (1 - 1 / N);
      $('amr-out').textContent = 'S = (1/X − 1/N) / (1 − 1/N) = (' + r4(1 / X) + ' − ' + r4(1 / N) + ') / ' + r4(1 - 1 / N) +
        ' = ' + r4(S) + '  → serial ' + r4(S * 100) + '%, parallel ' + r4((1 - S) * 100) + '%' +
        (S < 0 ? '\n(負數 = 唔可能，因為 speedup 不可能 > N)' : '');
    }
    function amat() {
      var h = num('am-h'), ht = num('am-ht'), mt = num('am-mt'), mp = $('am-mtype').value;
      if (h > 1) h = h / 100;
      var missTime = mp === 'penalty' ? ht + mt : mt;
      var v = h * ht + (1 - h) * missTime;
      $('amat-out').textContent = 'hit ratio = ' + r4(h) + ', miss ratio = ' + r4(1 - h) + '\n' +
        (mp === 'penalty' ? 'miss time = hit time + penalty = ' + r4(missTime) + '\n' : '') +
        'AMAT = ' + r4(h) + ' × ' + ht + ' + ' + r4(1 - h) + ' × ' + r4(missTime) + ' = ' + r4(v);
    }
    function expavg() {
      var a = num('ea-a'), t0 = num('ea-t0');
      var ts = $('ea-ts').value.split(/[\s,]+/).filter(Boolean).map(parseFloat);
      var tau = t0, lines = ['τ0 = ' + t0];
      ts.forEach(function (t, i) {
        var nt = a * t + (1 - a) * tau;
        lines.push('τ' + (i + 1) + ' = ' + a + '×' + t + ' + ' + r4(1 - a) + '×' + r4(tau) + ' = ' + r4(nt));
        tau = nt;
      });
      $('ea-out').textContent = lines.join('\n');
    }
    function little() {
      var n = num('li-n'), l = num('li-l'), w = num('li-w');
      var out;
      if (isNaN(n)) out = 'n = λ × W = ' + l + ' × ' + w + ' = ' + r4(l * w);
      else if (isNaN(l)) out = 'λ = n / W = ' + n + ' / ' + w + ' = ' + r4(n / w);
      else out = 'W = n / λ = ' + n + ' / ' + l + ' = ' + r4(n / l);
      $('li-out').textContent = out + '\n(留空要求嘅一格)';
    }
    function rmutil() {
      var rows = $('rt-tasks').value.split('\n').map(function (s) { return s.trim(); }).filter(Boolean);
      var U = 0, parts = [], n = 0;
      rows.forEach(function (r) {
        var p = r.split(/[\s,]+/).map(parseFloat);
        if (p.length >= 2 && !isNaN(p[0]) && !isNaN(p[1])) { U += p[0] / p[1]; parts.push(p[0] + '/' + p[1]); n++; }
      });
      var bound = n ? n * (Math.pow(2, 1 / n) - 1) : 0;
      $('rt-out').textContent = 'U = ' + parts.join(' + ') + ' = ' + r4(U) + '\n' +
        'RM bound N(2^(1/N) − 1) with N = ' + n + ' : ' + r4(bound) + '\n' +
        (U <= bound ? '→ U ≤ bound：RM guaranteed schedulable' : U <= 1 ? '→ bound < U ≤ 1：RM 未必得（要畫 Gantt 驗證）；EDF 可以 (D = T)' : '→ U > 1：一定有 deadline miss');
    }
    function forkc() {
      var k = $('fk-pat').value, n = parseInt($('fk-n').value, 10), out = '';
      var f = {
        'f1': ['fork();', function (n) { return Math.pow(2, n); }, '2^n'],
        'f2': ['fork(); fork();', function (n) { return Math.pow(4, n); }, '4^n'],
        'f3': ['if (fork()) fork();', function (n) { return Math.pow(3, n); }, '3^n'],
        'f4': ['if (fork() == 0) fork();', function (n) { return Math.pow(3, n); }, '3^n'],
        'f5': ['if (fork()) fork(); else break;', function (n) { return Math.pow(2, n + 1) - 1; }, '2^(n+1) − 1  (breaks = 2^n − 1)'],
        'f6': ['if (fork()) printf; else printf;  (lines printed)', function (n) { return Math.pow(2, n + 1) - 2; }, '2^(n+1) − 2'],
        'f7': ['if (!fork()) { loop n: if (fork()) fork(); } fork();  (lines)', function (n) { return 2 * (Math.pow(3, n) + 1); }, '2(3^n + 1)']
      }[k];
      out = 'pattern per iteration: ' + f[0] + '\nformula: ' + f[2] + '\nn = ' + n + ' → ' + f[1](n);
      $('fk-out').textContent = out;
    }
    ['am-mode', 'am-s', 'am-n'].forEach(function (id) { $(id).addEventListener('input', amdahl); });
    ['amr-x', 'amr-n'].forEach(function (id) { $(id).addEventListener('input', amdahlRev); });
    ['am-h', 'am-ht', 'am-mt', 'am-mtype'].forEach(function (id) { $(id).addEventListener('input', amat); });
    ['ea-a', 'ea-t0', 'ea-ts'].forEach(function (id) { $(id).addEventListener('input', expavg); });
    ['li-n', 'li-l', 'li-w'].forEach(function (id) { $(id).addEventListener('input', little); });
    $('rt-tasks').addEventListener('input', rmutil);
    ['fk-pat', 'fk-n'].forEach(function (id) { $(id).addEventListener('input', forkc); });
    amdahl(); amdahlRev(); amat(); expavg(); little(); rmutil(); forkc();
  });
})();
