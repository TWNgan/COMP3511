/*!
 * sched-ui.js - interactive UI for sched.js (COMP3511 CPU-scheduling simulator).
 * Classic script, no dependencies; load after sched.js. Mounts automatically into
 * <div id="sched-app"></div> (optional attribute data-preset="<preset id>").
 *
 *   SchedUI.mount(element, { preset: 's26-q41' })
 *     -> { el, load(presetId), run(), state(), result() }
 */
(function () {
  'use strict';

  var DEFAULT_PRESET = 's26-q41';
  var MAX_ROWS = 20;

  /* Parameter inputs, shown according to Sched.ALGOS[i].params. */
  var PARAMS = {
    q: { label: 'Quantum q', type: 'int', min: 1 },
    arrivalFirst: { label: 'Arrival at the instant a quantum expires', type: 'bool',
      options: [['true', 'new arrival queues first (course)'], ['false', 'preempted process queues first']] },
    srtfTie: { label: 'Equal remaining time', type: 'select',
      options: [['keep', 'running process keeps the CPU'], ['preempt', 'new arrival preempts']] },
    preemptive: { label: 'Preemption', type: 'bool', options: [['false', 'non-preemptive'], ['true', 'preemptive']] },
    smallerIsHigher: { label: 'Priority order', type: 'bool',
      options: [['true', 'smaller number = higher'], ['false', 'larger number = higher']] },
    quanta: { label: 'Quanta Q0,Q1,... (last may be FCFS)', type: 'text', placeholder: '4,8,FCFS' },
    aging: { label: 'Aging: back to Q0 after waiting (0 = off)', type: 'int', min: 0 },
    alpha: { label: '\u03b1 per unit waiting', type: 'num' },
    beta: { label: '\u03b2 per unit running', type: 'num' },
    init: { label: 'Initial priority', type: 'num' },
    checkEvery: { label: 'Re-check every', type: 'int', min: 1 },
    dynTie: { label: 'Equal priority', type: 'select', options: [['larger', 'larger id wins'], ['smaller', 'smaller id wins']] },
    horizon: { label: 'Simulate from 0 to', type: 'int', min: 1 },
    rtTie: { label: 'Equal priority', type: 'select',
      options: [['keepRunning', 'running job keeps the CPU'], ['smallerId', 'smaller task id wins']] }
  };

  var HELP = {
    fcfs: 'Runs processes in arrival order, each to completion (non-preemptive). Same arrival time \u2192 lower id first.',
    sjf: 'When the CPU becomes free, the arrived process with the shortest burst runs to completion. Ties \u2192 earlier arrival, then lower id.',
    srtf: 'Preemptive SJF: at every arrival, the process with the shortest remaining time gets the CPU.',
    rr: 'FIFO ready queue; each turn lasts at most q. A process whose quantum expires goes to the tail, behind any process arriving at that same instant (course rule).',
    priority: 'The ready process with the highest priority runs. Ties \u2192 earlier arrival, then lower id (when preemptive, the running process keeps the CPU on a tie).',
    'priority-rr': 'The highest priority runs; equal priorities share the CPU round robin with quantum q. A higher-priority arrival preempts; the preempted process goes back to the head of its level and keeps the rest of its quantum.',
    mlfq: 'New jobs enter the tail of Q0. A job that uses its whole quantum moves to the tail of the next queue. A job preempted by a higher queue returns to the HEAD of its own queue and keeps the rest of its quantum. Labels show the queue each slice ran in.',
    dynamic: 'Larger value = higher priority = initial + \u03b1\u00b7(time waiting) + \u03b2\u00b7(time running). Re-evaluated every k units of the current run and whenever the CPU becomes free.',
    rm: 'Rate Monotonic: fixed priority, shorter period = higher priority. Every task releases a job at 0, T, 2T, ...; a late job keeps running (soft real-time) and counts as a miss.',
    edf: 'Earliest Deadline First: the job with the earliest absolute deadline runs. Every task releases a job at 0, T, 2T, ...; a late job keeps running and counts as a miss.'
  };

  var FIELDS = {
    arrival: { head: 'Arrival', title: 'arrival time', min: 0 },
    burst: { head: 'Burst', title: 'CPU burst time', min: 1 },
    priority: { head: 'Priority', title: 'priority number', min: null },
    C: { head: 'C', title: 'processing time per job', min: 1 },
    D: { head: 'D', title: 'relative deadline', min: 1 },
    T: { head: 'T', title: 'period', min: 1 }
  };

  /* ---------------------------------------------------------------- helpers */
  function esc(s) {
    return String(s === null || s === undefined ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  /** Escape, then typeset the ASCII used by sched.js log text. */
  function pretty(s) {
    return esc(s).replace(/-&gt;/g, '\u2192').replace(/\*/g, '\u00d7').replace(/ - /g, ' \u2212 ');
  }
  function colorClass(name) {
    var m = /^P(\d+)$/.exec(String(name));
    if (!m) return 'sch-idle';
    return +m[1] <= 8 ? 'sch-c' + m[1] : 'sch-cx';
  }
  function swatch(name) { return '<span class="sch-sw ' + colorClass(name) + '" aria-hidden="true"></span>'; }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function rowsFrom(procs) {
    return procs.map(function (x) {
      return { arrival: x[0], burst: x[1], priority: x[2] === undefined || x[2] === null ? '' : x[2] };
    });
  }
  function tasksFrom(procs) { return procs.map(function (x) { return { C: x[0], D: x[1], T: x[2] }; }); }

  var TEMPLATE =
    '<div class="sch-root">' +
      '<div class="sch-card sch-input">' +
        '<div class="sch-toolbar">' +
          '<label class="sch-field"><span>Load example</span><select class="sch-preset"></select></label>' +
          '<label class="sch-field"><span>Algorithm</span><select class="sch-algo"></select></label>' +
        '</div>' +
        '<p class="sch-help"></p>' +
        '<div class="sch-params"></div>' +
        '<div class="sch-tablewrap"><table class="sch-tbl sch-ptable"><thead></thead><tbody></tbody></table></div>' +
        '<div class="sch-actions"><button type="button" class="sch-btn sch-add">+ Add process</button></div>' +
        '<div class="sch-msg" role="alert" hidden></div>' +
      '</div>' +
      '<div class="sch-out">' +
        '<div class="sch-card">' +
          '<div class="sch-h">Gantt chart</div>' +
          '<div class="sch-gantt-scroll"></div>' +
          '<div class="sch-legend"></div>' +
          '<div class="sch-gtext-row"><code class="sch-gtext" tabindex="0"></code>' +
            '<button type="button" class="sch-btn sch-copy">Copy</button></div>' +
        '</div>' +
        '<div class="sch-card sch-results"></div>' +
        '<div class="sch-card">' +
          '<details class="sch-logbox" open><summary class="sch-h">Step-by-step log <span class="sch-logcount"></span></summary>' +
            '<div class="sch-logscroll"><table class="sch-tbl sch-log"><thead><tr>' +
              '<th scope="col">t</th><th scope="col">What happens</th><th scope="col">CPU and why</th>' +
              '<th scope="col">Waiting after the decision</th>' +
            '</tr></thead><tbody class="sch-logbody"></tbody></table></div>' +
          '</details>' +
        '</div>' +
      '</div>' +
    '</div>';

  /* ================================================================ mount */
  function mount(host, options) {
    if (!host) return null;
    if (host.__schedUI) return host.__schedUI;
    var S = window.Sched;
    if (!S) { host.textContent = 'Scheduling simulator: assets/sched.js did not load.'; return null; }
    options = options || {};
    var fmt = S.fmt;
    var algoById = {}, presetById = {};
    S.ALGOS.forEach(function (a) { algoById[a.id] = a; });
    S.PRESETS.forEach(function (p) { presetById[p.id] = p; });

    var state = {
      algo: 'fcfs', preset: '', opts: clone(S.DEFAULTS),
      rows: rowsFrom(presetById[DEFAULT_PRESET].procs),
      tasks: tasksFrom(presetById['s26-q42-rm'].procs)
    };
    var last = null, lastWidth = 0;

    host.innerHTML = TEMPLATE;
    var q = function (sel) { return host.querySelector(sel); };
    var els = {
      preset: q('.sch-preset'), algo: q('.sch-algo'), help: q('.sch-help'), params: q('.sch-params'),
      thead: q('.sch-ptable thead'), tbody: q('.sch-ptable tbody'), add: q('.sch-add'), msg: q('.sch-msg'),
      out: q('.sch-out'), gscroll: q('.sch-gantt-scroll'), legend: q('.sch-legend'), gtext: q('.sch-gtext'),
      copy: q('.sch-copy'), results: q('.sch-results'), log: q('.sch-logbody'), logCount: q('.sch-logcount')
    };

    // ---- selectors
    var groups = [], byGroup = {};
    S.PRESETS.forEach(function (p) {
      if (!byGroup[p.group]) { byGroup[p.group] = []; groups.push(p.group); }
      byGroup[p.group].push(p);
    });
    els.preset.innerHTML = '<option value="">Custom (your own input)</option>' + groups.map(function (g) {
      return '<optgroup label="' + esc(g) + '">' + byGroup[g].map(function (p) {
        return '<option value="' + esc(p.id) + '">' + esc(p.name) + '</option>';
      }).join('') + '</optgroup>';
    }).join('');
    els.algo.innerHTML = S.ALGOS.map(function (a) {
      return '<option value="' + a.id + '">' + esc(a.name) + '</option>';
    }).join('');

    // ---- input side
    function meta() { return algoById[state.algo]; }
    function list() { return meta().rt ? state.tasks : state.rows; }

    function renderParams() {
      var m = meta();
      els.help.textContent = HELP[m.id] || '';
      els.params.innerHTML = m.params.map(function (k) {
        var d = PARAMS[k], v = state.opts[k];
        if (d.options) {
          return '<label class="sch-field"><span>' + esc(d.label) + '</span><select data-opt="' + k + '">' +
            d.options.map(function (o) {
              return '<option value="' + o[0] + '"' + (String(v) === o[0] ? ' selected' : '') + '>' + esc(o[1]) + '</option>';
            }).join('') + '</select></label>';
        }
        var num = d.type !== 'text';
        return '<label class="sch-field"><span>' + esc(d.label) + '</span><input data-opt="' + k + '" type="' +
          (num ? 'number' : 'text') + '"' + (num ? ' step="' + (d.type === 'num' ? 'any' : '1') + '"' : ' class="sch-wide" spellcheck="false"') +
          (d.min !== undefined ? ' min="' + d.min + '"' : '') + (d.placeholder ? ' placeholder="' + esc(d.placeholder) + '"' : '') +
          ' value="' + esc(v) + '"></label>';
      }).join('');
    }

    function renderTable() {
      var m = meta(), L = list();
      els.thead.innerHTML = '<tr><th scope="col">' + (m.rt ? 'Task' : 'Process') + '</th>' + m.fields.map(function (f) {
        return '<th scope="col" title="' + esc(FIELDS[f].title) + '">' + FIELDS[f].head + '</th>';
      }).join('') + '<th scope="col"><span class="sch-sr">Remove</span></th></tr>';
      els.tbody.innerHTML = L.map(function (row, i) {
        var name = 'P' + (i + 1);
        return '<tr><th scope="row">' + swatch(name) + name + '</th>' + m.fields.map(function (f) {
          var mn = FIELDS[f].min;
          return '<td><input type="number" step="1"' + (mn === null ? '' : ' min="' + mn + '"') + ' data-i="' + i +
            '" data-f="' + f + '" value="' + esc(row[f]) + '" aria-label="' + name + ' ' + esc(FIELDS[f].title) + '"></td>';
        }).join('') + '<td><button type="button" class="sch-del" data-i="' + i + '"' + (L.length < 2 ? ' disabled' : '') +
          ' title="Remove ' + name + '" aria-label="Remove ' + name + '">\u00d7</button></td></tr>';
      }).join('');
      els.add.textContent = m.rt ? '+ Add task' : '+ Add process';
      els.add.disabled = L.length >= MAX_ROWS;
    }

    function renderControls() {
      els.algo.value = state.algo;
      els.preset.value = state.preset;
      renderParams();
      renderTable();
    }

    function loadPreset(id) {
      var p = presetById[id];
      if (!p) return false;
      state.algo = p.algo;
      state.opts = clone(S.DEFAULTS);
      Object.keys(p.opts || {}).forEach(function (k) { state.opts[k] = p.opts[k]; });
      if (Array.isArray(state.opts.quanta)) {
        state.opts.quanta = state.opts.quanta.map(function (x) { return x === null ? 'FCFS' : x; }).join(',');
      }
      if (algoById[p.algo].rt) state.tasks = tasksFrom(p.procs); else state.rows = rowsFrom(p.procs);
      state.preset = id;
      renderControls();
      compute();
      return true;
    }

    function markCustom() {
      if (state.preset) { state.preset = ''; els.preset.value = ''; }
    }

    function runOpts() {
      var o = {};
      Object.keys(state.opts).forEach(function (k) {
        var d = PARAMS[k], v = state.opts[k];
        o[k] = d && d.type === 'bool' ? (v === true || v === 'true') : v;
      });
      return o;
    }

    // ---- output side
    function showError(text) {
      els.msg.hidden = !text;
      els.msg.textContent = text ? 'Cannot simulate: ' + text + '.' : '';
      els.out.classList.toggle('sch-stale', !!text);
    }

    function compute() {
      var res;
      try { res = S.run(state.algo, list(), runOpts()); } catch (err) { showError(err.message); return; }
      showError('');
      last = res;
      renderGantt(res);
      renderLegend(res);
      els.gtext.textContent = res.gantt;
      if (res.kind === 'rt') renderRT(res); else renderProc(res);
      renderLog(res);
    }

    function renderGantt(res) {
      var blocks = res.blocks, box = els.gscroll;
      if (!blocks.length) { box.innerHTML = ''; return; }
      var t0 = blocks[0].start, t1 = blocks[blocks.length - 1].end, span = Math.max(1, t1 - t0);
      var minDur = Infinity;
      blocks.forEach(function (b) { minDur = Math.min(minDur, b.end - b.start); });
      lastWidth = box.clientWidth;
      var avail = (lastWidth || 680) - 32;
      // fit the box when possible, but keep the shortest slice wide enough for its label
      var unit = Math.min(Math.max(avail / span, 22 / minDur, 3), 64);
      var X = function (t) { return Math.round((t - t0) * unit); };
      var bars = blocks.map(function (b) {
        var left = X(b.start), w = X(b.end) - left, idle = b.name === 'idle';
        var qn = b.level === null || b.level === undefined ? '' : 'Q' + b.level;
        var fits = w - 2 >= b.name.length * 7 + 6;
        var tip = (idle ? 'idle' : b.name + (qn ? ' in ' + qn : '')) + ': ' + b.start + '\u2013' + b.end +
          ' (' + (b.end - b.start) + ' unit' + (b.end - b.start === 1 ? '' : 's') + ')';
        return '<div class="sch-blk ' + colorClass(b.name) + '" style="left:' + (left + 1) + 'px;width:' +
          Math.max(1, w - 2) + 'px" title="' + esc(tip) + '">' +
          (fits ? '<span class="sch-bn">' + esc(b.name) + '</span>' + (qn ? '<span class="sch-bq">' + qn + '</span>' : '') : '') +
          '</div>';
      }).join('');
      // every boundary time; a label that would collide drops to a second row
      var times = [t0].concat(blocks.map(function (b) { return b.end; }));
      var rowEnd = [-Infinity, -Infinity];
      var ticks = times.map(function (t) {
        var cx = X(t), half = (String(t).length * 6.6 + 4) / 2, row = 0;
        if (cx - half < rowEnd[0] + 2 && cx - half >= rowEnd[1] + 2) row = 1;
        rowEnd[row] = cx + half;
        return '<span class="sch-tick' + (row ? ' sch-tick2' : '') + '" style="left:' + cx + 'px">' + t + '</span>';
      }).join('');
      box.innerHTML = '<div class="sch-gantt" role="img" aria-label="' + esc('Gantt chart: ' + res.gantt) +
        '" style="width:' + X(t1) + 'px"><div class="sch-bars">' + bars + '</div><div class="sch-ticks">' + ticks + '</div></div>';
    }

    function renderLegend(res) {
      var items = (res.kind === 'rt' ? res.tasks : res.procs).map(function (p) {
        return '<span class="sch-li">' + swatch(p.name) + p.name + '</span>';
      });
      if (res.blocks.some(function (b) { return b.name === 'idle'; })) {
        items.push('<span class="sch-li">' + swatch('idle') + 'idle</span>');
      }
      if (res.algo === 'mlfq') items.push('<span class="sch-li">Qk under a name = the queue that slice ran in</span>');
      els.legend.innerHTML = items.join('');
    }

    function workLine(label, avg) {
      return '<div><span class="sch-wl">' + label + '</span> <code>' + (avg ? esc(avg.text) : '\u2013') + '</code></div>';
    }

    function renderProc(res) {
      var showPri = algoById[res.algo].fields.indexOf('priority') >= 0;
      var head = ['Process', 'Arrival', 'Burst'].concat(showPri ? ['Priority'] : [],
        ['Completion', 'TAT', 'WT', 'RT (course)', 'RT (textbook)']);
      var tips = { TAT: 'turnaround time = completion \u2212 arrival', WT: 'waiting time = turnaround \u2212 burst',
        'RT (course)': 'response time = time the first run ends \u2212 arrival (slide 5.12)',
        'RT (textbook)': 'response time = time of first start \u2212 arrival' };
      var cell = function (v, tip) { return '<td' + (tip ? ' title="' + esc(tip) + '"' : '') + '>' + fmt(v) + '</td>'; };
      var body = res.rows.map(function (r) {
        return '<tr><th scope="row">' + swatch(r.name) + r.name + '</th>' + cell(r.arrival) + cell(r.burst) +
          (showPri ? cell(r.priority) : '') + cell(r.completion) +
          cell(r.tat, r.completion + ' \u2212 ' + r.arrival) + cell(r.wt, r.tat + ' \u2212 ' + r.burst) +
          cell(r.rtCourse, 'first run ends at ' + r.firstRunEnd + ': ' + r.firstRunEnd + ' \u2212 ' + r.arrival) +
          cell(r.rtStart, 'first starts at ' + r.firstStart + ': ' + r.firstStart + ' \u2212 ' + r.arrival) + '</tr>';
      }).join('');
      var a = res.avg, blanks = showPri ? 4 : 3;
      var foot = '<tr><th scope="row">Average</th>' + new Array(blanks + 1).join('<td></td>') +
        cell(a.tat.value) + cell(a.wt.value) + cell(a.rtCourse ? a.rtCourse.value : null) + cell(a.rtStart.value) + '</tr>';
      els.results.innerHTML = '<div class="sch-h">Results</div>' +
        '<div class="sch-tablewrap"><table class="sch-tbl"><thead><tr>' + head.map(function (h) {
          return '<th scope="col"' + (tips[h] ? ' title="' + esc(tips[h]) + '"' : '') + '>' + h + '</th>';
        }).join('') + '</tr></thead><tbody>' + body + '</tbody><tfoot>' + foot + '</tfoot></table></div>' +
        '<div class="sch-work">' +
          workLine('Average waiting time', a.wt) +
          workLine('Average turnaround time', a.tat) +
          workLine('Average response time (course)', a.rtCourse) +
          workLine('Average response time (textbook)', a.rtStart) +
        '</div>' +
        '<p class="sch-note">Turnaround = completion \u2212 arrival \u00b7 Waiting = turnaround \u2212 burst \u00b7 ' +
        'Response (course, slide 5.12) = time the first run ends (quantum expiry, preemption or completion) \u2212 arrival \u00b7 ' +
        'Response (textbook) = first start \u2212 arrival. Hover a cell for its working.</p>';
    }

    function renderRT(res) {
      var U = res.util.value, B = res.rmBound.value, n = res.rmBound.n;
      var miss = res.misses;
      var verdict;
      if (U > 1 + 1e-9) verdict = 'U > 1: the CPU is overloaded, so deadlines will be missed under any scheduler.';
      else {
        if (U <= B + 1e-9) verdict = 'U \u2264 N(2^(1/N) \u2212 1): RM is guaranteed to meet every deadline (Liu\u2013Layland), and EDF too since U \u2264 1.';
        else verdict = 'U \u2264 1, so EDF can meet every deadline; U is above the RM bound, so the RM test is inconclusive (it is only a sufficient condition).';
        if (res.tasks.some(function (t) { return t.D !== t.T; })) {
          verdict += ' Both tests assume D = T; with D \u2260 T rely on the simulation.';
        }
      }
      var missText = miss.length
        ? '<span class="sch-bad-i" aria-hidden="true">\u2717</span> <b>' + miss.length + ' deadline' + (miss.length === 1 ? '' : 's') +
          ' missed</b> in [0, ' + res.horizon + ']: ' + miss.map(function (m) {
            return m.task + ' (deadline ' + m.deadline + ', ' + (m.finish === null ? 'not finished' : 'finished ' + m.finish) + ')';
          }).join('; ')
        : '<span class="sch-ok-i" aria-hidden="true">\u2713</span> <b>No deadline missed</b> in [0, ' + res.horizon + ']';
      var status = function (j) {
        if (j.status === 'met') return '<span class="sch-ok-i" aria-hidden="true">\u2713</span> met';
        if (j.status === 'missed') return '<span class="sch-bad-i" aria-hidden="true">\u2717</span> <b>missed</b>';
        return 'unfinished at ' + res.horizon + ' (' + j.remaining + ' left; deadline is after the window)';
      };
      var jobs = res.jobs.map(function (j) {
        return '<tr><th scope="row">' + swatch(j.task) + j.task + '#' + j.k + '</th><td>' + j.release + '</td><td>' +
          j.deadline + '</td><td>' + (j.finish === null ? '\u2013' : j.finish) + '</td><td class="sch-left">' + status(j) + '</td></tr>';
      }).join('');
      els.results.innerHTML = '<div class="sch-h">Deadlines</div><p class="sch-missline">' + missText + '</p>' +
        '<div class="sch-work">' +
          '<div><span class="sch-wl">Utilisation</span> <code>U = ' + esc(res.tasks.map(function (t) { return t.C + '/' + t.T; }).join(' + ')) +
            ' = ' + fmt(U, 3) + '</code></div>' +
          '<div><span class="sch-wl">RM bound</span> <code>N(2<sup>1/N</sup> \u2212 1) = ' + n + '(2<sup>1/' + n + '</sup> \u2212 1) = ' +
            fmt(B, 3) + '</code></div>' +
          (res.hyperperiod ? '<div><span class="sch-wl">Hyperperiod</span> <code>lcm(' +
            res.tasks.map(function (t) { return t.T; }).join(', ') + ') = ' + res.hyperperiod + '</code></div>' : '') +
        '</div><p class="sch-note">' + esc(verdict) + '</p>' +
        '<div class="sch-tablewrap sch-jobs"><table class="sch-tbl"><thead><tr><th scope="col">Job</th><th scope="col">Release</th>' +
        '<th scope="col">Deadline</th><th scope="col">Finish</th><th scope="col" class="sch-left">Status</th></tr></thead><tbody>' +
        jobs + '</tbody></table></div>';
    }

    function renderLog(res) {
      els.logCount.textContent = '(' + res.log.length + ' steps)';
      els.log.innerHTML = res.log.map(function (e) {
        var ev = e.events.map(function (s) {
          return '<div' + (/MISSES|LATE/.test(s) ? ' class="sch-miss"' : '') + '>' + pretty(s) + '</div>';
        }).join('') || '<span class="sch-dim">\u2013</span>';
        var who = String(e.cpu).split(/[@#]/)[0];
        var cpu = e.cpu === '-' ? '<span class="sch-dim">\u2013</span>'
          : swatch(e.cpu === 'idle' ? 'idle' : who) + '<b>' + esc(e.cpu) + '</b>';
        var waiting = String(e.queue || '').split(/\s{2,}/).map(pretty).join('<br>');
        return '<tr><td>' + e.t + '</td><td>' + ev + '</td><td>' + cpu +
          (e.why ? '<div class="sch-why">' + pretty(e.why) + '</div>' : '') + '</td><td class="sch-q">' + waiting + '</td></tr>';
      }).join('');
    }

    function copyGantt() {
      var text = last ? last.gantt : '';
      var done = function () {
        els.copy.textContent = 'Copied';
        setTimeout(function () { els.copy.textContent = 'Copy'; }, 1200);
      };
      var fallback = function () {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { if (document.execCommand('copy')) done(); } catch (e) { /* ignore */ }
        document.body.removeChild(ta);
      };
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback);
      else fallback();
    }

    // ---- events
    function onEdit(e) {
      var t = e.target;
      if (t.hasAttribute('data-opt')) {
        state.opts[t.getAttribute('data-opt')] = t.value;
        markCustom(); compute();
      } else if (t.hasAttribute('data-f')) {
        var row = list()[+t.getAttribute('data-i')];
        if (row) { row[t.getAttribute('data-f')] = t.value; markCustom(); compute(); }
      }
    }
    host.addEventListener('input', onEdit);
    host.addEventListener('change', function (e) {
      var t = e.target;
      if (t === els.preset) { if (t.value) loadPreset(t.value); }
      else if (t === els.algo) { state.algo = t.value; markCustom(); renderControls(); compute(); }
      else onEdit(e);
    });
    host.addEventListener('click', function (e) {
      var t = e.target.closest ? e.target.closest('button') : null;
      if (!t || !host.contains(t)) return;
      if (t === els.copy) { copyGantt(); return; }
      var L = list();
      if (t === els.add) {
        if (L.length >= MAX_ROWS) return;
        var prev = L[L.length - 1];
        if (meta().rt) L.push({ C: 1, D: 5, T: 5 });
        else L.push({ arrival: prev ? (Number(prev.arrival) || 0) + 1 : 0, burst: 4, priority: prev && prev.priority !== '' ? prev.priority : 1 });
        markCustom(); renderTable(); compute();
        var inputs = els.tbody.querySelectorAll('tr:last-child input');
        if (inputs.length) inputs[0].focus();
      } else if (t.classList.contains('sch-del')) {
        if (L.length < 2) return;
        L.splice(+t.getAttribute('data-i'), 1);
        markCustom(); renderTable(); compute();
      }
    });

    // re-fit the chart when the available width changes (also when first shown)
    var raf = 0;
    var refit = function () {
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        if (last && els.gscroll.clientWidth !== lastWidth) renderGantt(last);
      });
    };
    if (window.ResizeObserver) new ResizeObserver(refit).observe(els.gscroll);
    else window.addEventListener('resize', refit);

    var ctl = {
      el: host,
      load: loadPreset,
      run: compute,
      state: function () { return clone(state); },
      result: function () { return last; }
    };
    host.__schedUI = ctl;
    if (!loadPreset(options.preset || host.getAttribute('data-preset') || DEFAULT_PRESET)) loadPreset(DEFAULT_PRESET);
    return ctl;
  }

  window.SchedUI = { mount: mount };

  function autoMount() {
    var el = document.getElementById('sched-app');
    if (el) mount(el);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoMount);
  else autoMount();
})();
